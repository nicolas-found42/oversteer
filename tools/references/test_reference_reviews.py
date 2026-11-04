"""Human annotations change effective references without rewriting model judgments."""

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import reference_reviews
import review_pilot


def fixture():
    assets = {
        name: {"id": name, "sha256": name + "-hash", "platform_declared": "PS3"}
        for name in ("exact", "broad", "wrong-parent", "unknown", "legacy", "untouched")
    }
    rows = [
        {
            "id": name,
            "status": "complete",
            "screen_state": "menu/profile/select",
            "screen_review": False,
            "screen_distribution": {"menu/profile/select": 0.99},
            "tags": [],
        }
        for name in assets
    ]
    reviews = [
        {
            "asset_id": "legacy",
            "source_sha256": "legacy-hash",
            "state": "menu/profile/select",
            "action": "exclude-from-state-leads",
        }
    ]
    for name, outcome, label in [
        ("exact", "label", "replay/playback/camera"),
        ("broad", "category", "menu"),
        ("wrong-parent", "category", "career"),
        ("unknown", "unreadable", ""),
    ]:
        reviews.append(
            {
                "asset_id": name,
                "source_sha256": name + "-hash",
                "action": "annotate-screen",
                "pilot_id": "pilot",
                "review_id": name,
                "outcome": outcome,
                "label": label,
                "notes": "User evidence",
                "updated_at": "2026-11-03T23:00:00Z",
            }
        )
    return assets, rows, {"schema_version": 2, "reviews": reviews}


class ReviewOverlayTests(unittest.TestCase):
    def test_import_cli_is_idempotent_and_checks_original_images_before_writing(self):
        assets, rows, document = fixture()
        for row in rows:
            asset = assets[row["id"]]
            asset.update(kind="frame", source_id=asset["id"])
            asset["path"] = asset["id"] + ".jpg"
            asset["sha256"] = hashlib.sha256(asset["id"].encode()).hexdigest()
            row["image_sha256"] = asset["sha256"]
        document = {
            "schema_version": 1,
            "reviews": [
                {
                    **document["reviews"][0],
                    "source_sha256": assets["legacy"]["sha256"],
                }
            ],
        }
        pilot = review_pilot.make_pilot(list(assets.values()), rows, len(rows), "test")
        exact = next(x for x in pilot["items"] if x["asset_id"] == "exact")
        annotations = {
            "pilot_id": pilot["pilot_id"],
            "answers": {
                exact["review_id"]: {
                    "outcome": "label",
                    "label": "replay/playback/camera",
                    "notes": "Replay controls",
                    "updated_at": "2026-11-03T23:00:00Z",
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            (vault / "judgments").mkdir(parents=True)
            (vault / "assets.json").write_text(json.dumps(list(assets.values())))
            machine = vault / "judgments/classifications.json"
            machine.write_text(json.dumps(rows))
            for asset in assets.values():
                (vault / asset["path"]).write_bytes(asset["id"].encode())
            frozen = root / "pilot"
            frozen.mkdir()
            for item in pilot["items"]:
                image = frozen / item["image"]
                image.parent.mkdir(exist_ok=True)
                image.write_bytes(item["asset_id"].encode())
            manifest, exported, reviews = (
                frozen / "audit-manifest.json",
                root / "annotations.json",
                root / "reviews.json",
            )
            manifest.write_text(json.dumps(pilot))
            exported.write_text(json.dumps(annotations))
            reviews.write_text(json.dumps(document))
            original_reviews, original_machine = reviews.read_bytes(), machine.read_bytes()
            command = [
                sys.executable,
                review_pilot.__file__,
                "import-reviews",
                str(exported),
                "--manifest",
                str(manifest),
                "--vault",
                str(vault),
                "--reviews",
                str(reviews),
            ]
            source = vault / assets["exact"]["path"]
            source.write_bytes(b"changed")
            failed = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("Original reviewed reference image changed", failed.stderr)
            self.assertEqual(reviews.read_bytes(), original_reviews)
            source.write_bytes(b"exact")
            subprocess.run(command, capture_output=True, text=True, check=True)
            imported = reviews.read_bytes()
            subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertEqual(reviews.read_bytes(), imported)
            self.assertEqual(machine.read_bytes(), original_machine)
            self.assertEqual(len(json.loads(imported)["reviews"]), 2)

    def test_exact_relabels_parent_stays_coarse_and_uncertainty_withholds_a_lead(self):
        assets, rows, document = fixture()
        untouched = copy.deepcopy((rows, document))
        result = reference_reviews.apply_reviews(assets, rows, document)
        by_id = {x["id"]: x for x in result["rows"]}
        self.assertEqual(set(by_id), {"exact", "broad", "untouched"})
        self.assertEqual(by_id["exact"]["screen_state"], "replay/playback/camera")
        self.assertFalse(by_id["exact"]["screen_review"])
        self.assertIsNone(by_id["exact"]["screen_distribution"].get("replay/playback/camera"))
        self.assertEqual(by_id["exact"]["machine_screen_state"], "menu/profile/select")
        self.assertTrue(by_id["broad"]["screen_review"])
        self.assertEqual(by_id["broad"]["human_review"]["label"], "menu")
        self.assertNotIn("career", {x["screen_state"] for x in result["rows"]})
        self.assertEqual({x["category"] for x in result["parent_categories"]}, {"career", "menu"})
        self.assertEqual(len(result["rejected"]), 4)
        self.assertEqual((rows, document), untouched)

    def test_changed_images_unknown_labels_and_duplicate_annotations_fail_closed(self):
        for fault in ("hash", "label", "duplicate"):
            with self.subTest(fault=fault):
                assets, rows, document = fixture()
                if fault == "hash":
                    assets["exact"]["sha256"] = "changed"
                elif fault == "label":
                    document["reviews"][1]["label"] = "invented/state"
                else:
                    document["reviews"].append(copy.deepcopy(document["reviews"][1]))
                with self.assertRaises(ValueError):
                    reference_reviews.apply_reviews(assets, rows, document)

    def test_import_is_idempotent_and_keeps_prior_manual_review(self):
        assets, rows, document = fixture()
        original = {"schema_version": 1, "reviews": document["reviews"][:1]}
        pilot = {
            "pilot_id": "pilot",
            "items": [
                {
                    "review_id": "0001",
                    "asset_id": "exact",
                    "source_sha256": "exact-hash",
                    "screen_state": "menu/profile/select",
                },
            ],
        }
        annotations = {
            "answers": {
                "0001": {
                    "outcome": "label",
                    "label": "replay/playback/camera",
                    "notes": "Replay controls",
                    "updated_at": "now",
                }
            }
        }
        provenance = {"annotations_content_sha256": "content", "annotations_file_sha256": "file"}
        imported = reference_reviews.import_annotations(pilot, annotations, original, provenance)
        self.assertEqual(imported["reviews"][0], original["reviews"][0])
        self.assertEqual(len(imported["reviews"]), 2)
        self.assertEqual(
            reference_reviews.import_annotations(pilot, annotations, imported, provenance), imported
        )
        changed = {**provenance, "annotations_content_sha256": "different"}
        with self.assertRaises(ValueError):
            reference_reviews.import_annotations(pilot, annotations, imported, changed)

    def test_both_builders_apply_reviews_preserve_gaps_and_exclude_portable_leads(self):
        root = Path(__file__).resolve().parents[2]
        modules = {}
        for name, relative in [
            ("coverage", "tools/game/assets/reference_coverage.py"),
            ("runtime", "tools/game/reference.py"),
            ("compare", "tools/game/compare.py"),
        ]:
            spec = importlib.util.spec_from_file_location("test_" + name, root / relative)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[name] = module
        assets, rows, document = fixture()
        assets["sole"] = {"id": "sole", "sha256": "sole-hash", "platform_declared": "PS3"}
        assets["portable"] = {
            "id": "portable",
            "sha256": "portable-hash",
            "platform_declared": "PSP",
        }
        rows.extend(
            [
                {
                    "id": "sole",
                    "status": "complete",
                    "screen_state": "race/pause/menu",
                    "screen_review": False,
                    "screen_distribution": {"race/pause/menu": 1.0},
                },
                {
                    "id": "portable",
                    "status": "complete",
                    "screen_state": "replay/playback/camera",
                    "screen_review": False,
                    "screen_distribution": {"replay/playback/camera": 1.0},
                },
            ]
        )
        document["reviews"].append(
            {
                "asset_id": "sole",
                "source_sha256": "sole-hash",
                "action": "annotate-screen",
                "pilot_id": "pilot",
                "review_id": "sole",
                "outcome": "label",
                "label": "replay/playback/camera",
                "notes": "Replay",
                "updated_at": "now",
            }
        )
        for asset in assets.values():
            asset.update(
                path=asset["id"] + ".jpg",
                source_url="https://example.org/video",
                timestamp_seconds=1,
            )
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            data, vault = temporary / "data/juiced2", temporary / "vault"
            data.mkdir(parents=True)
            (vault / "judgments").mkdir(parents=True)
            (data / "reference-reviews.json").write_text(json.dumps(document))
            (vault / "assets.json").write_text(json.dumps(list(assets.values())))
            machine = vault / "judgments/classifications.json"
            machine.write_text(json.dumps(rows))
            before = machine.read_bytes()
            for key in ("coverage", "runtime"):
                module = modules[key]
                with patch.object(module, "ROOT", temporary), patch.object(module, "VAULT", vault):
                    module.main() if key == "coverage" else module.build()
            self.assertEqual(machine.read_bytes(), before)
            coverage = json.loads((data / "reference-coverage.json").read_text())
            runtime = json.loads((data / "runtime-reference.json").read_text())
            for result in (coverage, runtime):
                by_state = {x["state"]: x for x in result["states"]}
                self.assertEqual(by_state["race/pause/menu"]["reference_leads"], [])
                replay = by_state["replay/playback/camera"]["reference_leads"]
                self.assertEqual({x["asset_id"] for x in replay}, {"exact", "sole"})
                self.assertTrue(all(x["human_review"]["outcome"] == "label" for x in replay))
                self.assertTrue(all(x["probability"] is None for x in replay))
                profile = by_state["menu/profile/select"]["reference_leads"]
                self.assertEqual(profile[0]["asset_id"], "untouched")
                self.assertEqual(profile[1]["asset_id"], "broad")
                self.assertTrue(profile[1]["requires_review"])
                self.assertEqual(len(result["reviewed_parent_categories"]), 2)
            self.assertTrue(
                {x["state"]: x for x in coverage["states"]}["race/pause/menu"][
                    "canonical_reference_gap"
                ]
            )
            run = temporary / "run"
            run.mkdir()
            (run / "verification.json").write_text(
                json.dumps({"cases": [{"case": {"id": "pause"}}]})
            )
            output = temporary / "comparison"
            compare = modules["compare"]
            with (
                patch.object(compare, "ROOT", temporary),
                patch("sys.argv", ["compare.py", "--runs", str(run), "--output", str(output)]),
            ):
                # compare.py uses the conventional vault path; the data is still synthetic.
                (temporary / "artifacts").mkdir()
                (temporary / "artifacts/juiced2-vault").symlink_to(vault)
                compare.main()
            comparisons = json.loads((output / "comparisons.json").read_text())
            self.assertEqual(comparisons["pairs"], [])
            self.assertEqual(comparisons["unpaired"][0]["reason"], "reference-gap")


if __name__ == "__main__":
    unittest.main()

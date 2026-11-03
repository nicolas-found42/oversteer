"""Sampling, evidence identity, and conservative scoring for the blind pilot."""

import copy
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import review_pilot


def corpus():
    assets, predictions = [], []
    for source in range(12):
        for frame in range(8):
            identity = f"source-{source}-{frame}"
            sha = f"{source * 8 + frame:064x}"
            assets.append(
                {
                    "id": identity,
                    "kind": "frame",
                    "source_id": f"source-{source}",
                    "sha256": sha,
                    "path": f"frames/{identity}.jpg",
                    "platform_declared": "PS3" if source % 2 else "PC",
                }
            )
            predictions.append(
                {
                    "id": identity,
                    "status": "complete",
                    "screen_state": "menu/main" if frame % 2 else "boot/title",
                    "screen_review": frame % 3 == 0,
                    "image_sha256": sha,
                }
            )
    return assets, predictions


class PilotTests(unittest.TestCase):
    @unittest.skipUnless(
        shutil.which("node")
        and (review_pilot.ROOT / "tools/visual/node_modules/playwright").exists()
        and (review_pilot.DEFAULT_VAULT / "assets.json").exists(),
        "Requires the existing reference corpus and Playwright install",
    )
    def test_browser_harness_exercises_current_template_not_stale_user_page(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "tools/references"
            source.mkdir(parents=True)
            for name in ("review_pilot.py", "jev_catalog_v2.py", "test_review_pilot.cjs"):
                shutil.copyfile(Path(__file__).with_name(name), source / name)
            # Deliberately regress the source template in a sandbox. A stale generated
            # user page remains valid: the harness must detect the SOURCE regression.
            (source / "review_pilot.html").write_text(
                '<img id="frame" src="data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%271%27%20height=%271%27%3E%3C/svg%3E">'
                '<strong id="progress">source-template-regression</strong>'
            )
            modules = root / "tools/visual/node_modules"
            modules.parent.mkdir()
            modules.symlink_to(review_pilot.ROOT / "tools/visual/node_modules")
            vault = root / "artifacts/juiced2-vault"
            vault.mkdir(parents=True)
            original = review_pilot.DEFAULT_VAULT
            for name in ("assets.json", "judgments", "frames", "screenshots"):
                (vault / name).symlink_to(original / name)
            coverage = root / "data/juiced2/reference-coverage.json"
            coverage.parent.mkdir(parents=True)
            coverage.symlink_to(review_pilot.ROOT / "data/juiced2/reference-coverage.json")
            stale = vault / "review-pilot"
            review_pilot.build(original, stale, 200, "juiced2-human-pilot-1")
            result = subprocess.run(
                ["node", str(source / "test_review_pilot.cjs")],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            self.assertNotEqual(
                result.returncode, 0, "Browser checks passed against a stale artifact"
            )
            self.assertIn("source-template-regression", result.stderr)

    def test_score_cli_cannot_overwrite_annotations_manifest_or_existing_evidence(self):
        assets, predictions = corpus()
        for asset, prediction in zip(assets, predictions, strict=True):
            asset["sha256"] = hashlib.sha256(asset["id"].encode()).hexdigest()
            prediction["image_sha256"] = asset["sha256"]
        pilot = review_pilot.make_pilot(assets, predictions, 40, "test")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for item in pilot["items"]:
                image = root / item["image"]
                image.parent.mkdir(exist_ok=True)
                image.write_bytes(item["asset_id"].encode())
            manifest = root / "audit-manifest.json"
            annotations = root / "annotations.json"
            evidence = root / "prior-evidence.json"
            contents = {
                manifest: json.dumps(pilot),
                annotations: json.dumps({"pilot_id": pilot["pilot_id"], "answers": {}}),
                evidence: '{"reviewer_evidence":"must survive"}',
            }
            for output in contents:
                with self.subTest(output=output.name):
                    for path, content in contents.items():
                        path.write_text(content)
                    result = subprocess.run(
                        [
                            sys.executable,
                            review_pilot.__file__,
                            "score",
                            str(annotations),
                            "--manifest",
                            str(manifest),
                            "--output",
                            str(output),
                        ],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertNotEqual(result.returncode, 0, "Scoring overwrote frozen evidence")
                    self.assertEqual(output.read_text(), contents[output])
            fresh = root / "new-evaluation.json"
            result = subprocess.run(
                [
                    sys.executable,
                    review_pilot.__file__,
                    "score",
                    str(annotations),
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(fresh),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(fresh.read_text())["missing_annotations"], 40)

    def test_category_eligibility_at_95_percent_and_with_sparse_samples(self):
        self.assertEqual(review_pilot.MIN_PRECISION, 0.95)
        self.assertEqual(review_pilot.CONFIDENCE, 0.95)
        seed = "boundary"
        sources = {}
        for i in range(100):
            key = f"recording-{i}"
            split = int(review_pilot.identity([seed, key])[:8], 16) % 2
            sources.setdefault(split, key)
        assets, predictions = [], []
        for source in sources.values():
            for i in range(20):
                identity = f"{source}-{i}"
                sha = hashlib.sha256(identity.encode()).hexdigest()
                assets.append(
                    {
                        "id": identity,
                        "kind": "frame",
                        "source_id": source,
                        "sha256": sha,
                        "path": f"{identity}.jpg",
                        "platform_declared": "PS3",
                    }
                )
                predictions.append(
                    {
                        "id": identity,
                        "status": "complete",
                        "screen_state": "menu/main",
                        "screen_review": False,
                        "image_sha256": sha,
                    }
                )
        for size in (2, 40):
            pilot = review_pilot.make_pilot(assets, predictions, size, seed)
            answers = {
                x["review_id"]: {"outcome": "label", "label": "menu/main"} for x in pilot["items"]
            }
            annotations = {"pilot_id": pilot["pilot_id"], "answers": answers}
            report = review_pilot.evaluate(pilot, annotations)
            self.assertEqual(report["categories"]["menu/main"]["eligible"], size == 40)
            self.assertFalse(report["automatic_acceptance_enabled"])
            if size == 40:
                heldout = [x for x in pilot["items"] if x["split"] == "heldout"]
                for errors, expected_bound, eligible in ((1, 0.95, True), (2, 0.9, False)):
                    for item in heldout[:errors]:
                        answers[item["review_id"]]["label"] = "boot/title"
                    category = review_pilot.evaluate(pilot, annotations)["categories"]["menu/main"]
                    self.assertEqual(category["heldout_auto_precision_lower_95"], expected_bound)
                    self.assertEqual(category["eligible"], eligible)

    def test_sampling_is_reproducible_source_disjoint_and_weighted(self):
        assets, predictions = corpus()
        first = review_pilot.make_pilot(assets, predictions, 40, "test")
        self.assertEqual(first, review_pilot.make_pilot(assets[::-1], predictions, 40, "test"))
        self.assertEqual(len(first["items"]), 40)
        splits = {}
        for item in first["items"]:
            splits.setdefault(item["source_group"], set()).add(item["split"])
        self.assertTrue(all(len(values) == 1 for values in splits.values()))
        self.assertEqual({x["split"] for x in first["items"]}, {"tuning", "heldout"})
        self.assertEqual({x["screen_review"] for x in first["items"]}, {False, True})
        self.assertAlmostEqual(sum(x["weight"] for x in first["items"]), len(assets))

    def test_duplicate_images_and_press_pages_cannot_cross_splits(self):
        assets, predictions = corpus()
        assets[8]["sha256"] = assets[0]["sha256"]
        predictions[8]["image_sha256"] = assets[0]["sha256"]
        for asset in assets[-2:]:
            asset["kind"] = "press-screenshot"
            asset["source_page"] = "https://example.org/same-gallery"
            asset["source_id"] = asset["id"]
        pilot = review_pilot.make_pilot(assets, predictions, 40, "test")
        self.assertEqual(pilot["population_size"], len(assets) - 1)
        groups = {x["source_key"]: x["group"] for x in pilot["sources"]}
        self.assertEqual(groups["source-0"], groups["source-1"])
        self.assertIn("https://example.org/same-gallery", groups)

    def test_prediction_bound_to_different_image_is_rejected(self):
        assets, predictions = corpus()
        predictions[0]["image_sha256"] = "changed"
        with self.assertRaisesRegex(ValueError, "hash"):
            review_pilot.make_pilot(assets, predictions, 40, "test")

    def test_public_data_contains_no_assignment_or_source_metadata(self):
        assets, predictions = corpus()
        pilot = review_pilot.make_pilot(assets, predictions, 40, "test")
        public = review_pilot.public_data(pilot)
        self.assertEqual(set(public), {"pilot_id", "items", "catalog"})
        self.assertTrue(all(set(x) == {"id", "image"} for x in public["items"]))

    def test_exact_bound_handles_census_and_no_evidence(self):
        self.assertEqual(review_pilot.success_lower_count(100, 0, 0, 0.05), 0)
        self.assertEqual(review_pilot.success_lower_count(10, 10, 9, 0.05), 9)
        self.assertEqual(review_pilot.success_lower_count(10, 10, 10, 0.05), 10)
        # One perfect result out of a large population is not a 95% precision audit.
        self.assertLess(review_pilot.success_lower_count(10000, 1, 1, 0.05), 9500)
        self.assertGreaterEqual(review_pilot.success_lower_count(10000, 100, 100, 0.05), 9500)

    def test_exact_bound_has_claimed_coverage_for_small_finite_populations(self):
        # Enumerate the sampling distribution, including dependent draws without replacement.
        for population in range(2, 12):
            for sample in range(1, population + 1):
                for actual_successes in range(population + 1):
                    undercoverage = 0
                    for observed in range(
                        max(0, sample - population + actual_successes),
                        min(sample, actual_successes) + 1,
                    ):
                        lower = review_pilot.success_lower_count(population, sample, observed, 0.05)
                        if lower > actual_successes:
                            undercoverage += (
                                math.comb(actual_successes, observed)
                                * math.comb(population - actual_successes, sample - observed)
                                / math.comb(population, sample)
                            )
                    self.assertLessEqual(undercoverage, 0.05 + 1e-12)

    def test_modified_review_image_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "image.jpg"
            image.write_bytes(b"original")
            pilot = {
                "items": [
                    {
                        "image": "image.jpg",
                        "source_sha256": review_pilot.file_hash(image),
                        "review_id": "0001",
                    }
                ]
            }
            review_pilot.verify_images(pilot, root)
            image.write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError, "hash changed"):
                review_pilot.verify_images(pilot, root)

    def test_evidence_inventory_does_not_promote_classification_leads(self):
        coverage = {
            "states": [
                {
                    "state": "menu/main",
                    "scope": "single-player-review-candidate",
                    "reference_leads": [],
                }
            ]
        }
        ledger = review_pilot.evidence_ledger(coverage, "test")
        self.assertFalse(ledger["inventory_complete"])
        self.assertFalse(ledger["temporal_rules_verified_by_this_pilot"])
        self.assertEqual(ledger["state_candidates"][0]["verified_evidence"], [])
        self.assertTrue(
            all(x["status"] == "unverified-in-this-audit" for x in ledger["release_checks"])
        )

    def test_unresolved_and_missing_answers_do_not_become_successes(self):
        assets, predictions = corpus()
        pilot = review_pilot.make_pilot(assets, predictions, 40, "test")
        answers = {
            item["review_id"]: {"outcome": "label", "label": item["screen_state"], "notes": ""}
            for item in pilot["items"]
        }
        heldout = next(
            x for x in pilot["items"] if x["split"] == "heldout" and not x["screen_review"]
        )
        answers[heldout["review_id"]] = {"outcome": "unreadable", "label": "", "notes": ""}
        report = review_pilot.evaluate(pilot, {"pilot_id": pilot["pilot_id"], "answers": answers})
        category = report["categories"][heldout["screen_state"]]
        self.assertGreater(category["heldout_auto_sample_unresolved"], 0)
        self.assertLess(category["heldout_auto_precision_estimate"], 1)
        self.assertFalse(report["automatic_acceptance_enabled"])
        del answers[heldout["review_id"]]
        report = review_pilot.evaluate(pilot, {"pilot_id": pilot["pilot_id"], "answers": answers})
        self.assertEqual(report["missing_annotations"], 1)
        self.assertTrue(all(not x["eligible"] for x in report["categories"].values()))

    def test_import_identity_and_unknown_annotation_are_rejected(self):
        assets, predictions = corpus()
        pilot = review_pilot.make_pilot(assets, predictions, 40, "test")
        with self.assertRaisesRegex(ValueError, "pilot"):
            review_pilot.evaluate(pilot, {"pilot_id": "other", "answers": {}})
        answer = {"outcome": "label", "label": "invented-label", "notes": ""}
        with self.assertRaisesRegex(ValueError, "label"):
            review_pilot.evaluate(
                pilot, {"pilot_id": pilot["pilot_id"], "answers": {"0001": answer}}
            )
        bad = copy.deepcopy(pilot)
        bad["items"][0]["weight"] = 100000
        with self.assertRaisesRegex(ValueError, "identity"):
            review_pilot.evaluate(bad, {"pilot_id": pilot["pilot_id"], "answers": {}})


if __name__ == "__main__":
    unittest.main()

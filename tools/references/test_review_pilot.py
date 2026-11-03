"""Sampling, evidence identity, and conservative scoring for the blind pilot."""

import copy
import math
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

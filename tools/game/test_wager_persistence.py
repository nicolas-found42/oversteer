import copy
import unittest

from verify import restored_career_matches


class RestoredCareerTests(unittest.TestCase):
    def test_interrupted_cash_is_returned_without_changing_ownership_or_losses(self):
        saved = {
            "interrupted_race": {
                "wager": 1000,
                "entrance_fee": 0,
                "event_id": "race",
                "car_id": "car",
            },
            "career": {"cash": 5000, "losses": 0, "garage": {"car": {}}, "transactions": []},
        }
        restored = {
            "career": {
                "cash": 6000,
                "losses": 0,
                "garage": {"car": {}},
                "transactions": [
                    {
                        "sequence": 1,
                        "kind": "RaceRefund",
                        "amount": 1000,
                        "event_id": "race",
                        "car_id": "car",
                        "description": "Interrupted race cancelled; unsettled cash returned and owned car retained",
                    }
                ],
            }
        }
        self.assertTrue(restored_career_matches(saved, restored))
        for key, value in [("cash", 7000), ("losses", 1), ("garage", {})]:
            wrong = copy.deepcopy(restored)
            wrong["career"][key] = value
            self.assertFalse(restored_career_matches(saved, wrong))
        self.assertFalse(restored_career_matches(saved, saved))

    def test_settled_career_must_roundtrip_exactly(self):
        saved = {"career": {"cash": 6000, "losses": 1}}
        self.assertTrue(restored_career_matches(saved, saved))
        self.assertFalse(restored_career_matches(saved, {"career": {"cash": 7000, "losses": 1}}))
        self.assertFalse(restored_career_matches(saved, None))

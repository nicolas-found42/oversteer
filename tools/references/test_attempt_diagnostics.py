import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

import classify_vault_v2 as classifier
from classify_vault import diagnostics


class AttemptTests(unittest.TestCase):
    def test_retry_and_timeout_keep_operation_attempt_without_provider_body(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            journal = diagnostics.Journal(root / "events")
            asset = {"id": "fixture", "sha256": "a" * 64}
            response = json.dumps({"answers": {}, "model": "fixture", "usage": {}}).encode()
            failure = urllib.error.HTTPError(
                "https://fixture", 429, "SECRET", {}, io.BytesIO(b"SECRET")
            )
            with (
                patch.object(classifier, "WORK", root),
                patch.object(classifier, "VAULT", root),
                patch.object(classifier, "prepared_asset", return_value=("image", {})),
                patch.object(classifier, "OFFLINE", False),
                patch.object(classifier, "SPENT", 0),
                patch.object(classifier, "STOP"),
                patch.object(classifier.time, "sleep"),
                patch.object(
                    classifier.urllib.request,
                    "urlopen",
                    side_effect=[failure, io.BytesIO(response)],
                ) as request,
                patch.object(diagnostics, "JOURNAL", journal),
            ):
                classifier.STOP.is_set.return_value = False
                classifier.ask(asset, "detail", {}, "PRIVATE_KEY", 1)
                self.assertEqual(request.call_count, 2)
                with patch.object(
                    classifier.urllib.request, "urlopen", side_effect=TimeoutError("SECRET")
                ):
                    with self.assertRaises(TimeoutError):
                        classifier.ask(asset, "broad", {}, "PRIVATE_KEY", 1)
            result = diagnostics.query(root / "events", 0, 9999999999999)
            rows = result["records"]
            self.assertEqual(
                [r["outcome"] for r in rows if r["event"] == "provider.end"],
                ["error", "ok", "error"],
            )
            self.assertEqual(rows[0]["operation"], rows[3]["operation"])
            self.assertEqual(rows[1]["http_status"], 429)
            self.assertEqual(rows[3]["attempt"], 2)
            self.assertEqual(rows[-1]["category"], "TimeoutError")
            self.assertNotIn("SECRET", json.dumps(result))
            self.assertNotIn("PRIVATE_KEY", json.dumps(result))


if __name__ == "__main__":
    unittest.main()

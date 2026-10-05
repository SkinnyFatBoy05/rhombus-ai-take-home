import io
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'data-validation'))
from s3_output import observe, capture_fresh


class AwsFailure(Exception):
    def __init__(self, code):
        self.response = {'Error': {'Code': code}}


class OutputWitnessTests(unittest.TestCase):
    def setup_client(self):
        client = Mock()
        modified = datetime(2026, 10, 5, 4, 0, 1, tzinfo=timezone.utc)
        client.head_object.return_value = {'VersionId': 'new', 'ContentLength': 4, 'LastModified': modified}
        client.get_object.return_value = {**client.head_object.return_value, 'Body': io.BytesIO(b'a\n1\n')}
        return client

    def test_absent_object_differs_from_denied_lookup(self):
        client = Mock()
        client.head_object.side_effect = AwsFailure('404')
        self.assertFalse(observe(client, 'bucket', 'out.csv')['exists'])
        client.head_object.side_effect = AwsFailure('AccessDenied')
        with self.assertRaises(AwsFailure):
            observe(client, 'bucket', 'out.csv')

    def test_unchanged_or_old_output_cannot_pass(self):
        client = self.setup_client()
        prior = {'bucket': 'bucket', 'key': 'out.csv', 'version_id': 'new'}
        with self.assertRaisesRegex(ValueError, 'stale'):
            capture_fresh(client, 'bucket', 'out.csv', prior, '2026-10-05T04:00:00Z')
        prior['version_id'] = 'old'
        with self.assertRaisesRegex(ValueError, 'predates'):
            capture_fresh(client, 'bucket', 'out.csv', prior, '2026-10-05T04:00:02Z')
        client.get_object.assert_not_called()

    def test_fresh_exact_version_preserves_attribution_gap(self):
        client = self.setup_client()
        prior = {'bucket': 'bucket', 'key': 'out.csv', 'exists': False}
        data, meta = capture_fresh(client, 'bucket', 'out.csv', prior, '2026-10-05T04:00:00Z')
        self.assertEqual(data, b'a\n1\n')
        self.assertEqual(meta['version_id'], 'new')
        self.assertFalse(meta['run_attribution_verified'])
        client.get_object.assert_called_once_with(Bucket='bucket', Key='out.csv', VersionId='new')

    def test_wrong_prior_object_or_unversioned_bucket_rejected(self):
        client = self.setup_client()
        with self.assertRaisesRegex(ValueError, 'same object'):
            capture_fresh(client, 'bucket', 'out.csv', {'bucket': 'other', 'key': 'out.csv'}, '2026-10-05T04:00:00Z')
        client.head_object.return_value['VersionId'] = 'null'
        with self.assertRaisesRegex(ValueError, 'versioning'):
            observe(client, 'bucket', 'out.csv')


if __name__ == '__main__':
    unittest.main()

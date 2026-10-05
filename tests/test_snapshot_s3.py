import io
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'data-validation'))
from snapshot_s3 import MAX_BYTES, read_version


class SnapshotTests(unittest.TestCase):
    def client(self, data=b'a,b\n1,2\n', version='v1', length=None):
        body = io.BytesIO(data)
        client = Mock()
        client.get_object.return_value = {
            'Body': body, 'ContentLength': len(data) if length is None else length,
            'VersionId': version, 'LastModified': datetime(2026, 9, 30, tzinfo=timezone.utc)}
        return client, body

    def test_reads_the_requested_version_and_closes_stream(self):
        client, body = self.client()
        data, meta, time = read_version(client, 'test-only', 'output.csv', 'v1')
        client.get_object.assert_called_once_with(Bucket='test-only', Key='output.csv', VersionId='v1')
        self.assertEqual(data, b'a,b\n1,2\n')
        self.assertEqual(meta['provider'], 's3')
        self.assertNotIn('generation', meta)
        self.assertEqual(meta['version_id'], 'v1')
        self.assertTrue(body.closed)

    def test_unversioned_request_never_reaches_cloud(self):
        client, _ = self.client()
        with self.assertRaises(ValueError):
            read_version(client, 'test-only', 'output.csv', 'null')
        client.get_object.assert_not_called()

    def test_refuses_large_download(self):
        client, body = self.client(length=MAX_BYTES + 1)
        with self.assertRaises(ValueError):
            read_version(client, 'test-only', 'output.csv', 'v1')
        self.assertTrue(body.closed)

    def test_version_mismatch_never_accepted(self):
        client, body = self.client(version='different')
        with self.assertRaises(ValueError):
            read_version(client, 'test-only', 'output.csv', 'v1')
        self.assertTrue(body.closed)


if __name__ == '__main__':
    unittest.main()

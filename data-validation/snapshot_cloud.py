"""Read exact S3/GCS object versions into a new local evidence directory.

Requires optional boto3 and google-cloud-storage packages plus local cloud auth.
No uploads, bucket creation, permission changes, retries or live pipeline actions.
The caller obtains run ID/time/schedule/config hash from actual Rhombus evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('scenario', 'run-id', 'schedule-id', 'configuration-sha256', 'started-at',
                'finished-at', 's3-bucket', 's3-key', 's3-version-id',
                'gcs-bucket', 'gcs-key', 'gcs-generation'):
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--directory', required=True, type=Path)
    parser.add_argument('--aws-profile')
    parser.add_argument('--gcp-project', required=True)
    args = parser.parse_args()
    import boto3
    from google.cloud import storage
    if args.s3_version_id == 'null':
        parser.error('enable source versioning and provide a specific S3 version ID')
    args.directory.mkdir(parents=True, exist_ok=False)  # Never overwrite prior evidence.
    s3 = boto3.Session(profile_name=args.aws_profile).client('s3')
    obj = s3.get_object(Bucket=args.s3_bucket, Key=args.s3_key, VersionId=args.s3_version_id)
    source = obj['Body'].read()
    blob = storage.Client(project=args.gcp_project).bucket(args.gcs_bucket).blob(
        args.gcs_key, generation=int(args.gcs_generation))
    blob.reload()
    output = blob.download_as_bytes(if_generation_match=int(args.gcs_generation))
    (args.directory / 'input.csv').write_bytes(source)
    (args.directory / 'output.csv').write_bytes(output)
    manifest = {
        'scenario': args.scenario,
        'run': {'id': args.run_id, 'schedule_id': args.schedule_id, 'trigger': 'scheduled',
                'status': 'success', 'started_at': args.started_at, 'finished_at': args.finished_at,
                'configuration_sha256': args.configuration_sha256},
        'source': {'bucket': args.s3_bucket, 'key': args.s3_key, 'version_id': obj['VersionId'],
                   'last_modified': obj['LastModified'].isoformat(), 'file': 'input.csv',
                   'sha256': hashlib.sha256(source).hexdigest()},
        'output': {'bucket': args.gcs_bucket, 'key': args.gcs_key, 'generation': str(blob.generation),
                   'updated_at': blob.updated.isoformat(), 'file': 'output.csv',
                   'sha256': hashlib.sha256(output).hexdigest()},
    }
    (args.directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Saved exact-version snapshots to {args.directory}; verify run metadata against platform logs.')


if __name__ == '__main__':
    main()

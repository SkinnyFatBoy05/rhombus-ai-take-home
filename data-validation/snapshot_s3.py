"""Read exact S3 input/output versions for the authorized AWS-only deviation.

Uses local AWS SDK authentication; never creates resources, uploads data, changes
permissions, or calls Google Cloud. Run metadata must come from Rhombus logs.
Optional dependency: boto3. Preserve platform logs alongside these snapshots.
"""
import argparse
import hashlib
import json
from pathlib import Path
from validate_run import instant

MAX_BYTES = 1024 * 1024


def read_version(s3, bucket, key, version):
    if not version or version == 'null':
        raise ValueError('a specific version ID from a versioned bucket is required')
    response = s3.get_object(Bucket=bucket, Key=key, VersionId=version)
    try:
        if response['ContentLength'] > MAX_BYTES:
            raise ValueError('assessment object exceeds the 1 MiB download limit')
        data = response['Body'].read(MAX_BYTES + 1)
    finally:
        response['Body'].close()
    if len(data) > MAX_BYTES or response.get('VersionId') != version:
        raise ValueError('object size or returned version differs from the requested snapshot')
    return data, {'provider': 's3', 'bucket': bucket, 'key': key, 'version_id': version,
                  'sha256': hashlib.sha256(data).hexdigest()}, response['LastModified'].isoformat()


def capture(s3, args):
    start, end = instant(args.started_at), instant(args.finished_at)
    if end < start:
        raise ValueError('run end must be after its start')
    if len(args.configuration_sha256) != 64 or any(c not in '0123456789abcdef' for c in args.configuration_sha256):
        raise ValueError('configuration-sha256 must be a lowercase SHA-256 digest')
    if args.directory.exists():
        raise ValueError('evidence directory already exists; never overwrite earlier evidence')
    source, source_meta, source_time = read_version(s3, args.bucket, args.input_key, args.input_version)
    output, output_meta, output_time = read_version(s3, args.bucket, args.output_key, args.output_version)
    args.directory.mkdir(parents=True, exist_ok=False)
    (args.directory / 'input.csv').write_bytes(source)
    (args.directory / 'output.csv').write_bytes(output)
    manifest = {
        'scenario': args.scenario,
        'requirement_deviation': 'S3 destination replaces GCS at candidate request; GCS acceptance unmet.',
        'run': {'id': args.run_id, 'schedule_id': args.schedule_id, 'trigger': 'scheduled',
                'status': 'success', 'configuration_sha256': args.configuration_sha256,
                'started_at': args.started_at, 'finished_at': args.finished_at},
        'source': dict(source_meta, file='input.csv', last_modified=source_time),
        'output': dict(output_meta, file='output.csv', updated_at=output_time),
    }
    (args.directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('scenario', 'run-id', 'schedule-id', 'configuration-sha256', 'started-at',
                'finished-at', 'bucket', 'input-key', 'input-version', 'output-key', 'output-version'):
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--aws-profile')
    parser.add_argument('--region', default='ap-southeast-2')
    args = parser.parse_args()
    import boto3
    from botocore.config import Config
    s3 = boto3.Session(profile_name=args.aws_profile).client('s3', region_name=args.region,
           config=Config(retries={'total_max_attempts': 1}, connect_timeout=10, read_timeout=30))
    capture(s3, args)
    print(f'Saved two exact S3 versions to {args.directory}. Verify metadata against Rhombus logs.')


if __name__ == '__main__':
    main()

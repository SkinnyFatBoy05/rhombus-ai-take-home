"""Read-only S3 export witness. A fresh version is necessary, not run attribution.

Requires an independently authorized named AWS profile and optional boto3.
Never use the write-only Rhombus credential, create resources, or change access.
"""
import argparse
import json
from pathlib import Path
from snapshot_s3 import MAX_BYTES, read_version
from validate_run import instant


def observe(s3, bucket, key):
    try:
        response = s3.head_object(Bucket=bucket, Key=key)
    except Exception as error:
        # A denied lookup is not evidence of an absent file.
        code = getattr(error, 'response', {}).get('Error', {}).get('Code')
        if str(code) in {'404', 'NoSuchKey', 'NotFound'}:
            return {'exists': False, 'bucket': bucket, 'key': key}
        raise
    version = response.get('VersionId')
    if not version or version == 'null':
        raise ValueError('S3 export witness requires bucket versioning')
    if response['ContentLength'] > MAX_BYTES:
        raise ValueError('export exceeds the 1 MiB assessment limit')
    return {'exists': True, 'bucket': bucket, 'key': key, 'version_id': version,
            'last_modified': response['LastModified'].isoformat(),
            'bytes': response['ContentLength']}


def capture_fresh(s3, bucket, key, prior, since):
    if prior.get('bucket') != bucket or prior.get('key') != key:
        raise ValueError('prior observation must refer to the same object')
    cutoff = instant(since)
    current = observe(s3, bucket, key)
    if not current['exists']:
        raise ValueError('no S3 output exists')
    if current['version_id'] == prior.get('version_id'):
        raise ValueError('S3 output is stale: version did not change')
    if instant(current['last_modified']) < cutoff:
        raise ValueError('S3 output predates schedule activation')
    data, metadata, modified = read_version(s3, bucket, key, current['version_id'])
    if instant(modified) != instant(current['last_modified']):
        raise ValueError('download metadata differs from observed version')
    return data, {**current, **metadata, 'fresh_after': since,
                  'run_attribution_verified': False,
                  'note': 'A fresh exact object version plus its bytes. Correlate with real Rhombus execution records; this alone does not prove the trigger.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['observe', 'capture'])
    for name in ['bucket', 'key', 'aws-profile', 'report']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--region', default='ap-southeast-2')
    parser.add_argument('--prior', type=Path)
    parser.add_argument('--since')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = Path(args.report)
    if report.exists() or (args.output and args.output.exists()):
        parser.error('refusing to overwrite evidence')
    if args.mode == 'capture' and not all([args.prior, args.since, args.output]):
        parser.error('capture requires --prior, --since and --output')
    import boto3
    from botocore.config import Config
    client = boto3.Session(profile_name=args.aws_profile).client(
        's3', region_name=args.region,
        config=Config(retries={'total_max_attempts': 1}, connect_timeout=8, read_timeout=20))
    if args.mode == 'observe':
        evidence = observe(client, args.bucket, args.key)
    else:
        prior = json.loads(args.prior.read_text(encoding='utf-8'))
        data, evidence = capture_fresh(client, args.bucket, args.key, prior, args.since)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

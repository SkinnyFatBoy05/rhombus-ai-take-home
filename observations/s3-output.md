# S3 alternative: connection succeeds, pipeline export fails

Status: LIVE FAILURE OBSERVED — 5 October 2026, workflow 0.

The candidate excluded Google Cloud and authorized this alternative in the
existing private assessment bucket, within an A$5 total project allowance.
Employer acceptance of replacing GCS is unknown.

1. Destination creation twice failed under PutObject restricted to `output/*`.
2. Direct location/list/tiny-marker operations using the same candidate-supplied
   key returned HTTP 200. These were connectivity checks, not pipeline exports.
3. During an explicitly approved temporary write test excluding `input/`,
   destination 0 connected. S3 recorded a 103-byte root connection probe at
   14:55:19 Sydney. The broader grant was immediately removed.
4. The filename UI rejects folders: `output/orders-clean` is invalid. The
   accepted CSV filename is `orders-clean`. With explicit candidate approval,
   the policy was changed to PutObject on only the root `orders-clean.csv`.
5. The 15:01:37–39 manual run failed at orders_output. Its logs simultaneously
   reported "Pipeline execution completed successfully." No CSV was in S3.
6. The diagnostic assistant confirmed destination 0, csv, orders-clean and
   download_local=false. It could not retrieve the actual attempted key, raw
   AWS error or historical job ID. Its key-mismatch explanation was a hypothesis.
7. The candidate approved one further temporary export test with PutObject
   anywhere in the same bucket except input/, expiring at 15:30 at most. After
   AWS confirmed the save, one manual run at 15:08:07–10 again failed at output.
   The exact-file policy was immediately restored and AWS confirmed the save.
   No new CSV appeared. IAM propagation was not independently measured, so the
   trial does not conclusively exclude a permissions issue.

No object-read/delete, ACL, other service or new credential permission was added
for either diagnostic. The connection marker and direct diagnostic marker remain
separate from exported-data evidence. The applied grant expires at 18:30 Sydney.

A supervised Custom five-minute schedule was also activated, re-saved to obtain
a countdown toward 15:05, and inspected after the due time plus a full reload.
History showed No results; S3 showed no output. Both Custom and Hourly schedules
were then verified inactive. This is failed/unverified scheduling evidence, not a
successful scheduled export. Zero credits were visible during this trial, which
is a confounding factor; earlier schedule failures happened with credits present.

The final diagnostic consumed the remaining AI credits. At zero, a manual
pipeline run still started and reached output failure. AI repairs were unavailable
at that point. The later voucher redemption described below restored credits
without a purchase.

The CLI S3 branch now requires an independently authorized read-only AWS profile,
a newly observed exact S3 VersionId after schedule activation, and validation of
that version's actual bytes. A preview cannot substitute for this check. The
freshness helper distinguishes 404 from AccessDenied and rejects stale versions.
Its unit tests pass; live SDK execution remains unverified because no separate
read-only profile is configured. No credential is embedded in the code.

[Redacted diagnostic](evidence/s3-destination-diagnostic-20261005.json) ·
[Applied policy](../config/aws-destination-policy.json)

[Screenshot omitted from public copy; original retained locally.]

## Credit-restored follow-up

The supplied voucher successfully restored 5,000 credits. A manual job
`redacted-evidence-id-025` completed input, cleaning and sort, but
failed at output with the generic destination-permissions message.

Rhombus's [official S3 guide](https://doc.rhombusai.com/docs/Integrations/aws-s3-connection/)
lists GetObject alongside GetBucketLocation, ListBucket and PutObject. With
explicit approval, GetObject was added only to `orders-clean.csv` with the same
18:30 expiry. The 15:22:21–23 Sydney manual retest still failed. The AI builder
then recreated only the output node as `output_node_2`, preserving the existing
source and transformations. Job `redacted-evidence-id-028` again
completed the upstream six rows and failed at output. Neither result exposes
the underlying AWS exception or actual attempted key. These experiments do
not establish the root cause.

At the candidate's request, the platform assistant materialized the existing
`orders_sorted` cache as a Workspace artifact without re-cleaning it. Clicking
Download timed out in browser automation, but the actual 382-byte file arrived
in Downloads at 15:28:19 Sydney. It was copied unchanged into the evidence
folder. Its SHA-256 matches the earlier baseline CSV, and strict validation
again finds four decimal-format failures. This is actual downloaded evidence,
but it is not a successful S3 export and its cache-to-run binding is unverified.

The five-minute schedule was then activated and re-saved, with 4,980 credits
visible. It counted down across the 15:30 Sydney boundary; history remained
`No results.` after the due time and a full reload. Both schedules were then
verified inactive. Restoring credits therefore did not resolve the observable
schedule symptom. No successful scheduled execution is claimed.

[Actual Workspace CSV](evidence/baseline-workspace-c8716e74.csv) ·
[Provenance](evidence/baseline-workspace-c8716e74-provenance.json) ·
[Strict validation](evidence/baseline-workspace-c8716e74-validation.json).

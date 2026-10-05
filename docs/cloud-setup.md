# Cloud setup and spending boundary

## Current AWS output continuation — 5 October afternoon

The candidate explicitly approved the IAM user `assessment-export-example`,
Rhombus as its recipient, bucket list/location access and PutObject only under
the existing assessment bucket's `output/*`, expiring at **18:30 Sydney / 07:30
UTC on 5 October**. AWS confirmed the user and sole inline policy were created;
console access is disabled. The original input-only bucket policy was renewed
to the same expiry, retaining its principals, actions and prefix restrictions.
The candidate created and supplied the existing key and explicitly authorized
its use in Rhombus. Destination 0 connected after a temporary, approved root
probe-write test; that broad grant was immediately removed. Because filenames
reject folders, the candidate then approved writes only to the root
`orders-clean.csv` until the same expiry, then explicitly approved GetObject on that same one file. The exact-file read/write policy is current; it
supersedes `output/*`. Actual pipeline exports still fail. No provider-level
exception or attempted key is exposed. See the redacted S3 diagnostic.

This approval supersedes the historical local-output-only instructions below.
Keep public access blocked, use only synthetic data and supervised runs, and
retain the A$5 total ceiling. No Google Cloud use or publishing is authorized.
The existing US$1 tracking budget showed US$0.00 when checked this afternoon;
that display is rounded and delayed, not an enforceable cap.

## Original storage boundary

On 30 September the candidate authorized **AWS storage only**, with a maximum total project spend of **A$5** and a preference to spend nothing. The AWS account is not eligible for the Free plan. Google Cloud must not be used, funded or reopened. Google billing was closed with no balance due; the candidate ended the card-removal attempt and instructed that Google Cloud not be used. Personal account and payment identifiers must not enter the repository.

The employer brief requires a GCS destination. An S3 destination, if supported by Rhombus, is an explicitly documented deviation and does **not** satisfy GCS integration acceptance. Employer acceptance of the substitution is unknown. No message has been sent to the employer.

The revised design is a private S3 Standard bucket with separate `input/` and `output/` prefixes, versioning, public access blocked and SSE-S3 encryption. Use synthetic CSVs only, <1 MB total, bounded scheduled runs and short-lived scoped connector access where supported. Disable the schedule after the test session. No compute, NAT, database, KMS key, paid support or marketplace resources are authorized. The actual S3 destination form requires an Access Key and Secret Key. This historical no-key state was superseded by the explicitly approved 5 October setup above. [Credential boundary and scoped policy](aws-destination-handoff.md).

Applied: created the dedicated bucket in `ap-southeast-2`; uploaded the 669-byte synthetic baseline as `input/orders.csv`; saved a prefix-scoped Rhombus read-only policy expiring **30 September 2026 at 12:00 UTC**. Created `Rhombus-assessment-total-USD1`, a **US$1 tracking budget for 29 September–8 October**, showing $0 used when inspected. It has no notifications or automatic actions and is **not a spending cap**. The assessment schedule was tested and is now **Inactive**; no successful scheduled execution was observed.

**AWS Budgets alerts do not enforce a hard cap.** Billing data and notifications can lag. Inspect current costs and keep resource usage far below the A$5 ceiling; stop on unexpected usage and never leave recurring work unattended. [AWS limitations](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html). S3 storage, requests and transfers may incur small charges even for console browsing. [S3 pricing](https://aws.amazon.com/s3/pricing/).

## Historical local-output alternative (30 September)

The candidate selected **Download Locally** on 30 September to avoid creating
an AWS key. Applied this output mode; the node now reads **Export to Download
Locally (csv)**. The S3 source remains connected. This is a GCS/cloud-output
deviation, with no employer exception confirmed. No destination IAM user or key
was created. The policy file is a proposal only and must not be applied.

A one-minute assessment schedule was created with **Notify on failure off**,
then retried at five minutes after a successful manual run. Both observation
windows had empty execution history. The schedule is now **Inactive**.
No cloud compute or other storage service was introduced by this change.

## Recheck on 5 October 2026

AWS Budgets displayed **US$0.00 used** (rounded to cents) against the existing
US$1 tracking budget. This is delayed billing visibility, not a hard spending cap.
The candidate signed back into AWS. The same three read-only S3 policy statements
were renewed until **5 October at 03:00 UTC / 14:00 Sydney**. Principals, bucket,
`input/` prefix and permitted actions were unchanged; Block Public Access remains
on. Rhombus then listed the existing baseline `input/orders.csv` as Connected.
No write credentials, new bucket, compute resource or Google Cloud service was
created. Access will expire automatically; later testing needs another bounded
renewal after checking costs.

## Historical local-output run instructions (superseded by AWS approval above)

1. Use only the existing assessment bucket and synthetic `input/orders.csv`.
2. Confirm the current source policy has not expired, then verify the object in
   Rhombus Browse files. A stored Connected badge alone does not prove fresh access.
3. Keep output at **Download Locally**, CSV, `orders-clean`. No GCS or S3-output
   setup is authorized; the old destination-policy file is a superseded proposal.
4. Supervise one schedule and deactivate it after the observation window. Keep
   notification email disabled. Do not leave a schedule running between sessions.
5. Capture real source/output files, run metadata and validation before claiming
   any case passed. A preview or AI narrative cannot establish export provenance.

The employer's GCS acceptance requirement remains unresolved. The unsent support
note asks for an accepted substitute or an employer-provided test destination;
it does not authorize use of Google Cloud.

## Earlier manual-test state, 5 October at 13:26 Sydney

The original 669-byte baseline was restored to input/orders.csv at 02:26:07 UTC,
version redacted-evidence-id-038. Both Rhombus schedules are inactive.
Repairs are retained as separate pipeline snapshots. The scoped Rhombus read
policy expires at 03:00 UTC / 14:00 Sydney on 5 October; it was not extended.

No new cloud services, credentials or output buckets were created in the Chrome
continuation. Tiny versioned source files remain in the existing private S3
bucket; versioning retains earlier test files. Storage can still incur a small
charge, and the US$1 tracking budget is not a hard spending cap. The authorized
project ceiling remains A$5. Google Cloud was not used.

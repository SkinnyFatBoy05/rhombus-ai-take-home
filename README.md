# Rhombus AI — LLM Observability & Quality Assurance

**Submission package; mandatory live acceptance remains incomplete.** All seven drift cases were exercised manually in signed-in Chrome on 5 October. Four AI repairs recovered the expected business values in fresh previews; missing-column cases now fail with an explicit schema error. Scheduled runs, authenticated command-line execution and repeated exported files remain unverified. The repository is public; no submission email has been sent.

[Public redaction notice](docs/public-redaction.md): cloud/workflow identifiers are placeholders; original screenshots remain local.

[GitHub repository](https://github.com/SkinnyFatBoy05/rhombus-ai-take-home) · [Review status](docs/review-start-here.md) · [Exact requirements](docs/requirements.md) · [Runbook](docs/runbook.md) · [Submission checklist](docs/github-submission-checklist.md) · [Video walkthrough](https://raw.githubusercontent.com/SkinnyFatBoy05/rhombus-ai-take-home/refs/heads/codex/submission/demo/rhombus-evidence-walkthrough.mp4)

The brief requires S3 → AI cleaning → **Google Cloud Storage**. On 5 October the candidate approved **S3 output** to replace the earlier local-download workaround. The restricted IAM identity and destination 0 are connected. Reads and writes are limited to `orders-clean.csv` until 18:30 Sydney on 5 October; actual pipeline export still fails. The connection probe succeeds, but is not a pipeline export. [S3 diagnostics](observations/evidence/s3-destination-diagnostic-20261005.json). Neither alternative has an employer-approved exception. Intended GitHub owner: **skinnyfatboy05**. Deadline: **6 October 2026**. [Cloud scope](docs/cloud-setup.md).

## Setup and checks

Requires Python 3.11+ and Node.js 22+. From this folder:

```sh
npm ci
npx playwright install chromium
python -m unittest discover -s tests -p "test_*.py" -v
npm test
npm run test:smoke
npm run test:api
npm run test:list
```

Verified: **41 Python checks, 12 Node checks, 1 public browser test and 4 direct API tests passed**. The 37 unchanged Python checks retain their earlier verification; four new S3 freshness checks passed on 5 October. Node/browser/API checks also passed on 5 October. API tests assert exact HTTP 401 and JSON content on three endpoints observed in real browser traffic. These negative tests do not establish authenticated pipeline success. [Verification](observations/evidence/local-verification.md) · [API provenance](observations/evidence/api-discovery.md).

## Authenticated UI automation

```sh
npm run capture
# Copy config/live.s3.example.json to config/live.json for preprovisioned S3 output.
# Confirm the assessment target and destination; no keys belong in this config.
# Set RHOMBUS_ALLOW_LIVE_WRITES=1 in your shell.
npm run test:ui
```

The Playwright journey implements the observed S3 connection, explicit AI Pipeline mode, configured S3 or local output, a five-minute schedule, fresh execution assertions, data checks and schedule deactivation in cleanup. The S3 branch requires a new exact object version after activation and validates its downloaded bytes; it never substitutes a preview for cloud output. It selects the Custom schedule by project and recurrence, reloads before reading output, and opens the output node's eye control. There are no fixed sleeps or mutation retries. Set `sourceSnapshot` to the captured baseline S3 input. For S3, install the optional `boto3` dependency and configure a separately authorized read-only AWS profile in `awsReadProfile`. This environment has no such profile; no credential was added to this runner; Rhombus access is scoped to its approved destination. GCS is excluded under the current scope.

**Not executed successfully:** Google rejected sign-in in the separate test browser. Normal Chrome sign-in subsequently enabled supervised browser testing, but its authenticated session is not available to the standalone CLI runner through the supported tools. No security warning was bypassed. Preflight fails before mutations if its private storage state is missing. Successful scheduled-row parsing still needs live calibration because no attributable execution-history row was available. [Observed controls](observations/evidence/ui-controls.md).

## Data validation

The strict validator compares input identity/schema with actual output schema, counts, cleaning, duplicate retention, order, semantic canaries and determinism. `validate_run.py` separately checks run/file provenance. Golden files are expectations, never platform exports.

```sh
# Actual captured baseline; expected exit 1 for decimal formatting and missing repeats:
python data-validation/validate.py --scenario baseline --input datasets/baseline.csv --output observations/evidence/baseline-manual-20261005.csv --report artifacts/manual-baseline-recheck.json

# Supplementary preview-only business check; expected exit 0:
python data-validation/validate_preview.py observations/evidence/semantic-cents-repaired-preview.json --report artifacts/cents-preview-check.json
```

The [actual 382-byte CSV](observations/evidence/baseline-manual-20261005.csv) contains six correct numeric records but four amount strings lose required trailing decimal zeros. Its [strict report](observations/evidence/baseline-manual-20261005-validation.json) fails accordingly. The baseline fixture matches the captured S3 source bytes; this does not prove which source version a particular run read. [Source provenance](observations/evidence/baseline-source.json).

Fresh preview checks confirm the repaired business values, while explicitly leaving `csv_bytes_verified`, `scheduled_run_verified` and `determinism_verified` false. Both semantic defects fail these independent checks before repair. Earlier preview downloads were unreliable. A later Workspace artifact download succeeded despite the browser event timing out: the [actual file](observations/evidence/baseline-workspace-c8716e74.csv) is byte-identical to the baseline and independently confirms its formatting defect. Its [provenance](observations/evidence/baseline-workspace-c8716e74-provenance.json) does not establish a fresh independent scheduled run or S3 export.

Once actual independent scheduled exports exist, use:

```sh
python data-validation/validate.py --scenario baseline --input artifacts/baseline/source/input.csv --output artifacts/baseline/1/output.csv --output artifacts/baseline/2/output.csv --output artifacts/baseline/3/output.csv --report artifacts/baseline/validation.json
python data-validation/validate_run.py artifacts/baseline/1/manifest.json artifacts/baseline/2/manifest.json artifacts/baseline/3/manifest.json --report artifacts/baseline/provenance-validation.json
```

These example run/output paths do **not** yet exist. Validate every real drift/post-fix file when captured. File-validator exit codes: **0** complete pass, **1** findings/incomplete coverage, **2** invalid input. Cloud snapshot/freshness helpers have local test coverage but have not been run against live accounts. [Data contract](docs/data-contract.md).

## Observations summary

These are **manual** live results, not scheduled acceptance. Severity is candidate judgement: High means silent business corruption; Medium means blocked processing or poor diagnostics; None means no observed business defect in this fixture. Initial schema runs may overlap a delayed chatbot request; semantic failures were independently repeated with the original snapshot restored and the chatbot idle. [Full chronology](observations/evidence/manual-drift-matrix-20261005.json).

| Change | Pipeline stopped? | Chatbot fix worked? | Severity | Report |
|---|---|---|---|---|
| Drop email | Yes, empty data at sort | Explicit missing-email guard verified; no invented data | Medium | [Drop](observations/schema-drop-column.md) |
| Rename amount | Yes, empty data at sort | Six correct preview records after alias repair | Medium | [Rename](observations/schema-rename-column.md) |
| USD amount prefix | Yes, empty data at sort | Six correct preview records after parser repair | Medium | [Type](observations/schema-change-type.md) |
| Add campaign | No; six correct preview records | Not needed for displayed business values | None observed | [Add](observations/schema-add-column.md) |
| Combined schema changes | Yes, empty data at sort | Explicit missing-email guard verified; processing remains blocked | Medium | [Combined](observations/schema-combined.md) |
| Dollars → cents | No; four wrong records | Six correct preview records after explicit unit repair | High | [Cents](observations/semantic-cents.md) |
| MM/DD → DD/MM | No; six wrong dates | Six correct preview records for the declared date fixture | High | [Dates](observations/semantic-date-order.md) |

**Top three findings:**

1. A success status did not imply business correctness. Cents caused 100× amounts and two lost orders; all six ambiguous dates changed meaning. Independent checks caught both, and AI fixes recovered the controlled fixtures. [Cents](observations/semantic-cents.md) · [Dates](observations/semantic-date-order.md).
2. Custom and Hourly schedule countdowns produced no attributable execution-history records after due times and reloads. Root cause is unknown; this blocks the scheduled baseline. [Schedule evidence](observations/scheduling-blocker.md).
3. Failed runs also logged “Pipeline execution completed successfully.” Cached previews sometimes showed earlier data until a full reload, and a stopped chatbot request continued in the background. These make independent status/freshness checks essential. [Chronology](observations/evidence/manual-drift-matrix-20261005.json) · [Delayed request](observations/evidence/delayed-chatbot-20261005.md).

The baseline CSV's loss of trailing decimal zeros is a separate reproducible formatting finding.

## Usability feedback

The scoped S3 policy instructions and saved pipeline versions were helpful. AI-generated node descriptions and the six-row preview made the cleaning logic easy to inspect. Local output allowed useful testing without another cloud credential.

The S3 continuation connected destination 0, but exports still failed even during one approved broader write diagnostic. Both temporary grants were restored; the exact-file permission remains time-limited. The supplied voucher restored 5,000 AI credits; export still failed after redemption, exact-file read permission and rebuilding the output node. [S3 report](observations/s3-output.md).

Source and history controls need accessible labels. Logs should expose one authoritative run outcome and a stable run ID; preview data should identify the run and source version that produced it. Schedule history should show failed attempts as well as successes. Cancellation should clearly indicate whether backend work has stopped, and chatbot conclusions should distinguish verified results from hypotheses.

## Demo and submission

[Captioned video](https://raw.githubusercontent.com/SkinnyFatBoy05/rhombus-ai-take-home/refs/heads/codex/submission/demo/rhombus-evidence-walkthrough.mp4) (2m40s) · [Transcript](demo/walkthrough-transcript.json) · [Walkthrough notes](docs/demo-script.md). This is an evidence-slide walkthrough, **not** a live screen recording or a passing end-to-end demonstration. The complete MP4 decoded successfully. The video is available from this public repository.

```sh
python scripts/readiness.py
```

This intentionally returns nonzero for unresolved acceptance gaps. The original source and pipeline were restored after manual testing; both schedules were verified inactive again after the AWS-output continuation. The candidate-created credential has connected destination 0; the temporary probe grant was removed, and only the approved root CSV can be read or written. No secret is stored in this project. The supplied voucher restored 5,000 credits without a paid upgrade; 4,980 were last observed. AWS usage must remain near zero within the A$5 allowance; the US$1 tracking budget is **not a hard cap**. Google Cloud remains unused. [Latest handoff](observations/evidence/post-redemption-handoff-20261005.json) · [AWS continuation](observations/evidence/aws-output-setup-20261005.json) · [Unsent support note](docs/support-note-unsent.md).

# Live experiment runbook

Current project: `https://rhombusai.com/workflow/0`, created 30 September 2026. S3 source connected; AI-built input/cleaning/sort/output nodes exist. Manual runs report success, but the captured CSV fails fixed-decimal formatting. Custom one-/five-minute and built-in Hourly trials produced no visible execution records. Both the original custom schedule and the new diagnostic Hourly/minute-22 schedule are now inactive. See [baseline build](../observations/baseline-build.md), [scheduling blocker](../observations/scheduling-blocker.md) and [continued attempt](../observations/evidence/continuation-2026-10-05.md).

**Execution boundary:** AWS only, at most A$5 for the whole project, aiming near zero. Do not open or fund Google Cloud. References below to GCS describe the original acceptance target; an S3 or local-download destination must be labelled as a deviation. The approved source key is `input/orders.csv` in the dedicated Sydney bucket recorded in `cloud-setup.md`.

## Establish the baseline

1. Review `cloud-setup.md` and its actual resources. The AWS account is paid; the tracking budget is not a hard cap. The current source and export permissions expire at 07:30 UTC / 18:30 Sydney on 5 October. Recheck before later runs.
2. Upload `datasets/baseline.csv` to the single S3 key `input/orders.csv`; record VersionId, SHA-256 and upload UTC time. Do not upload multiple scenarios into the source prefix simultaneously.
3. Connect the source through Rhombus's S3 form, with `input/` as Folder/path. Verify bucket, region, policy and file preview.
4. Reuse the original AI-generated baseline snapshot for the supervised continuation. The CLI supports preprovisioned S3 via `config/live.s3.example.json`; live authenticated execution remains unverified. All transformations must remain AI-built. The local Python oracle is only a test tool.
5. Select the connected **Amazon S3** destination and set CSV Custom Filename to `orders-clean`. The UI rejects folders. The candidate approved changing PutObject scope to the exact root `orders-clean.csv`; this is now the applied policy. Destination creation writes a temporary root probe and succeeded during a separately approved, immediately restored permission test. The actual export still fails; do not claim success from the connection probe or widen permissions without approval. Record the GCS deviation. Preserve the complete generated pipeline configuration and its SHA-256 before drift testing; a saved snapshot ID is not a configuration hash.
6. Create a recurring custom cron schedule (initial target `*/5 * * * *`, subject to the actual account's supported minimum). Turn failure notifications off to respect the instruction not to send email. Record schedule ID, cron and timezone from the platform.
7. Wait on observable scheduled-run status with bounded polling/assertions. Never substitute Run Now for scheduled evidence. Record run ID, scheduled trigger, start/end times and log excerpt. Capture the actual S3 output bytes, VersionId and LastModified; correlate these with the execution record. A fresh object alone does not prove which trigger wrote it.
8. Compare actual S3 input/output snapshots with `data-validation/validate.py`. `snapshot_s3.py` supports exact version downloads using an independently configured, authorized read-only SDK session; the Rhombus export credential intentionally cannot read objects and must not be reused for this. Without an SDK session, download the exact versions through the AWS console and preserve their metadata. Run the validator even for a stopped run; an absent output is not a passing result. Google Cloud remains excluded.
9. For successful baseline determinism, collect three distinct scheduled run IDs and actual output versions while input and configuration remain identical. `validate_run.py` accepts S3 version manifests and checks data plus provenance consistency. Its metadata must come from real records. Never invent run IDs, versions, times or configuration hashes. Preserve local-download evidence separately if cloud export remains blocked.

## Execute every drift independently

Order: drop column, rename column, change type, add column, combined schema drift, cents, date order.

For each case:

1. Restore the original pipeline configuration and baseline source; verify a successful scheduled control run. Record its version and configuration hash. A prior chatbot repair must not leak into the next independent experiment.
2. Replace only `input/orders.csv` with the named drift fixture before the next trigger. Confirm the upload completed before run start. Record exact object version/hash.
   The staged copies under ignored `artifacts/source-staging/<scenario>/orders.csv`
   retain each fixture's exact bytes while keeping the object filename constant.
   Rhombus's current S3 documentation requires **Refresh access** after replacing
   a source file. Capture the refreshed input preview before attributing output
   to that fixture. A changed S3 object alone does not prove the pipeline read it.
3. Keep the original pipeline configuration unchanged for the initial drift run. Record stopped/warned/continued, logs, execution time, actual downloaded contents, and next schedule state/time. State that GCS delivery was excluded.
4. Validate every output, even if the UI reports success. Save the report whether it passes or fails. For failed runs, check whether an old destination object remains and identify it as stale.
5. Give the **actual** error/log or validator finding to the chatbot. Save exact diagnosis and proposed fix. If there was no platform warning, explicitly state that and provide the independently detected discrepancy. Apply transformations through the AI builder only.
6. Re-run on the same drifted input on a schedule; record the new configuration hash, resulting data, validation and next-trigger behavior. A plausible chatbot explanation is not proof the fix worked.
7. Collect three outputs per frozen configuration/input where possible. Never group a repaired run with its pre-fix configuration for determinism. Record any missing repetitions as coverage gaps.
8. Fill that case's observation file with redacted evidence links, severity and reproduction steps. Keep initial and post-fix reports separate.

Suggested severity: High = silent financial/date corruption or wrong records; Medium = explicit pipeline failure/recovery or scheduling failure; Low = confusing diagnostics/UI with correct protected data. These are project conventions, not claims about unexecuted cases.

## Capture browser/API evidence

`npm run capture` launches an interactive local Playwright browser. Sign in there, then inspect the assessment project, its sources, schedules and logs. Press Enter in its terminal to save storage state and HAR. Google login may reject automated browsers; use a supported existing sign-in method or perform manual evidence capture rather than bypassing login security.

Raw HAR/storage state can contain cookies, tokens and account data. They are ignored by Git. Produce a redacted endpoint/status/body excerpt in `observations/evidence/`, never copy raw auth artifacts into a submission. The CLI suite now implements observed source, explicit Pipeline mode, preprovisioned S3 or local output, scheduling, fresh-outcome checks and deactivation. It fails its preflight until a separate supported authenticated session is available. Successful execution-row formats still need live verification because the app's history has remained empty.

The API suite currently covers three observed protected backend endpoints in four tests, including an invalid-token variant. Add a positive authenticated run/status test once that endpoint has been captured.

For a supported installed browser, capture also accepts
`RHOMBUS_BROWSER_CHANNEL=chrome` or `msedge`. It does not hide automation or
bypass sign-in warnings. The 5 October Chrome attempt was cancelled after the
candidate reported a security warning; no new state was saved. A normal Chrome
sign-in reported later by the candidate is not yet an authenticated CLI session.

If scheduling remains blocked, supervised manual drift runs may be collected as
**supplementary evidence** using the same source/version and validation controls.
Label their trigger honestly and keep scheduled acceptance incomplete. Save or
restore the AI-generated baseline with Canvas → Toolbox → Version Control;
`redacted-evidence-id-034` / `redacted-evidence-id-027` was saved before drift injection on 5 October.
The version ID is not a full exported configuration hash.

## End the experiment

Disable the assessment schedule after the last run and verify it is disabled. Record remaining free credits. Preserve snapshots/evidence. Complete README findings and usability paragraphs from actual experience, record a short demo, run readiness checks, and review the submission checklist. Do not publish, email or delete cloud resources without the corresponding authorization.

## Verified manual continuation, 5 October

The seven live manual cases are recorded in
[the matrix](../observations/evidence/manual-drift-matrix-20261005.json).
They supplement the blocked scheduled path; they do not satisfy it.

Before switching fixtures, wait for the chatbot response to complete. UI stop
controls did not reliably terminate backend work. Restore the original snapshot
before independent initial experiments, refresh source access after uploading,
and reload the page before reading output: an open preview can retain previous
data. Confirm the source shape as well as the output.

Saved versions in workflow 0:

| Snapshot | ID | Purpose |
|---|---|---|
| redacted-evidence-id-034 | redacted-evidence-id-027 | Original dollar/MM-DD baseline |
| redacted-evidence-id-035 | redacted-evidence-id-022 | Explicit cents-to-dollars repair |
| redacted-evidence-id-036 | redacted-evidence-id-003 | Controlled DD/MM fixture repair |
| redacted-evidence-id-037 | redacted-evidence-id-009 | Alias/USD-prefix adapters and required-field guard |

These are separate scenario configurations, not interchangeable generic parsers.
Snapshot IDs and displayed code_sha values are not full configuration hashes.
The date repair is fixture-specific; validate a declared date contract rather
than guessing formats in future inputs.

The original baseline source/pipeline were restored at final handoff. Both
Custom */5 and Hourly minute-22 schedules are inactive. Do not assume old
time-limited S3 access still works after its expiry. That earlier handoff used
03:00 UTC; the approved afternoon continuation renewed it to 07:30 UTC. No
recurring workload was left active in the earlier handoff. [Earlier state](../observations/evidence/final-handoff-20261005.json) · [AWS continuation](../observations/evidence/aws-output-setup-20261005.json).

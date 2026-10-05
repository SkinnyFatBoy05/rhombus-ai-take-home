# schema-add-column

Status: LIVE MANUAL EVIDENCE; scheduled acceptance and exported-file validation incomplete.

## Change and expectation

Add campaign=spring-2026 as a seventh input column. Input: [schema-add-column.csv](../datasets/schema-add-column.csv). [Fixture hashes](../datasets/manifest.json) · [Cleaning contract](../docs/data-contract.md).

Preserve the declared six-field output and business records; ignore the extra field or make its handling explicit.

## Observed result and logs

At 01:54:44–01:54:46 UTC the pipeline completed. Reloaded source preview showed campaign; output preview had the six correct reference records and six contract columns, excluding campaign.

Initial source: version `redacted-evidence-id-012`, 822 bytes, uploaded `2026-10-05T01:54:13Z` to the same `input/orders.csv` key. Exact timestamps and source metadata are in the [manual matrix](evidence/manual-drift-matrix-20261005.json). No independent execution run ID was exposed for these manual controls.

## Chatbot and repair

No corrective chatbot request was needed for the displayed business values. The later schema-adapter repair also explicitly excluded extra fields, but that claim is not substituted for this original observation.

No business repair indicated. A CSV download attempt produced no captured file in the ten-second wait; serialized precision and repeated output remain unverified.

Stopped: No. Fix: not needed for preview values. Severity: None observed for this controlled fixture.

## Validation and evidence limits

[Initial preview](evidence/schema-add-column-initial-preview.json) · [Preview validation](evidence/schema-add-column-preview-validation.json) · [File coverage](evidence/schema-add-column-live-file-validation.json)

Preview assertions compare schema, row count, unique/sorted IDs and exact business values against an independent reference. A preview pass does not prove CSV formatting, destination delivery, scheduled execution or determinism. No fresh drift CSV was captured. Missing-output file reports retain that gap; golden data were not presented as platform output.

Initial schema experiments followed restoration of the original snapshot, but the first chatbot request continued server-side after UI cancellation. Its timing limits certainty about the exact executable configuration during the initial matrix. Both semantic defects were therefore repeated independently with the original snapshot restored and the chatbot idle. [Cancellation chronology](evidence/delayed-chatbot-20261005.md).

## Reproduction and schedule behavior

1. In assessment workflow 0, wait for all chatbot work to finish, restore `redacted-evidence-id-034/redacted-evidence-id-027`, and keep both schedules off for this manual reproduction.
2. Replace the same private S3 object with this fixture; record version/hash/time. Refresh Rhombus source access and verify the current input after run/reload.
3. Run the pipeline manually, preserve logs, reload the page, and open the output node's eye preview. Independently check values; do not infer freshness from an already-open preview.
4. Give the actual findings to the AI builder and apply the described explicit repair only. Wait for completion; rerun and capture a fresh preview and actual CSV if available.
5. For the original brief, separately establish successful scheduled baseline/drift/recovery records, capture their real output files and validate independent repetitions under identical input/configuration. Those steps remain outstanding.

Both Custom five-minute and Hourly schedules were inactive throughout these manual tests and at final handoff. No post-drift scheduled recovery is claimed. [Earlier scheduling blocker](scheduling-blocker.md) · [Baseline restored and schedules off](evidence/final-handoff-20261005.json).

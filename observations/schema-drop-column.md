# schema-drop-column

Status: LIVE MANUAL EVIDENCE; scheduled acceptance and exported-file validation incomplete.

## Change and expectation

Remove the required email column. Input: [schema-drop-column.csv](../datasets/schema-drop-column.csv). [Fixture hashes](../datasets/manifest.json) · [Cleaning contract](../docs/data-contract.md).

Reject the incomplete schema with a named missing-field error; do not invent source data.

## Observed result and logs

At 01:38:06–01:38:09 UTC the run failed at orders_sorted with “DataFrame should not be empty.” The earlier cleaning step warned that no results remained. A success line appeared at the same timestamp, contradicting the error.

Initial source: version `redacted-evidence-id-018`, 494 bytes, uploaded `2026-10-05T01:37:10Z` to the same `input/orders.csv` key. Exact timestamps and source metadata are in the [manual matrix](evidence/manual-drift-matrix-20261005.json). No independent execution run ID was exposed for these manual controls.

## Chatbot and repair

The first AI request proposed a required-column guard but ran for 21m41s and continued server-side after the stop controls. Its first verification still produced the vague sort error. A later AI schema-adapter repair added an explicit required-column check.

Snapshot__4 was tested with a fresh 494-byte missing-email upload. At 02:22:01–02:22:03 UTC it failed at orders_cleaned naming email as missing. The guard works; this is safe rejection, not data recovery. The contradictory success log remains.

Stopped: Yes. Fix: explicit diagnostic verified. Severity: Medium (blocked processing and poor initial diagnostics).

## Validation and evidence limits

[Initial/repair logs](evidence/schema-drop-column-live-20261005.json) · [Initial file check](evidence/schema-drop-column-initial-validation.json)

Preview assertions compare schema, row count, unique/sorted IDs and exact business values against an independent reference. A preview pass does not prove CSV formatting, destination delivery, scheduled execution or determinism. No fresh drift CSV was captured. Missing-output file reports retain that gap; golden data were not presented as platform output.

Initial schema experiments followed restoration of the original snapshot, but the first chatbot request continued server-side after UI cancellation. Its timing limits certainty about the exact executable configuration during the initial matrix. Both semantic defects were therefore repeated independently with the original snapshot restored and the chatbot idle. [Cancellation chronology](evidence/delayed-chatbot-20261005.md).

## Reproduction and schedule behavior

1. In assessment workflow 0, wait for all chatbot work to finish, restore `redacted-evidence-id-034/redacted-evidence-id-027`, and keep both schedules off for this manual reproduction.
2. Replace the same private S3 object with this fixture; record version/hash/time. Refresh Rhombus source access and verify the current input after run/reload.
3. Run the pipeline manually, preserve logs, reload the page, and open the output node's eye preview. Independently check values; do not infer freshness from an already-open preview.
4. Give the actual findings to the AI builder and apply the described explicit repair only. Wait for completion; rerun and capture a fresh preview and actual CSV if available.
5. For the original brief, separately establish successful scheduled baseline/drift/recovery records, capture their real output files and validate independent repetitions under identical input/configuration. Those steps remain outstanding.

Both Custom five-minute and Hourly schedules were inactive throughout these manual tests and at final handoff. No post-drift scheduled recovery is claimed. [Earlier scheduling blocker](scheduling-blocker.md) · [Baseline restored and schedules off](evidence/final-handoff-20261005.json).

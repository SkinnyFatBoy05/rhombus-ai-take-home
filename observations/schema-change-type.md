# schema-change-type

Status: LIVE MANUAL EVIDENCE; scheduled acceptance and exported-file validation incomplete.

## Change and expectation

Prefix amount text with USD, making ordinary numeric parsing fail. Input: [schema-change-type.csv](../datasets/schema-change-type.csv). [Fixture hashes](../datasets/manifest.json) · [Cleaning contract](../docs/data-contract.md).

Report the unsupported currency representation, or apply a declared parser while preserving dollar values.

## Observed result and logs

At 01:52:58–01:53:00 UTC the run failed at orders_sorted with “DataFrame should not be empty,” alongside a contradictory success line. Reloaded source preview showed USD 120.00, USD 25.50 and USD 9.99.

Initial source: version `redacted-evidence-id-013`, 709 bytes, uploaded `2026-10-05T01:52:43Z` to the same `input/orders.csv` key. Exact timestamps and source metadata are in the [manual matrix](evidence/manual-drift-matrix-20261005.json). No independent execution run ID was exposed for these manual controls.

## Chatbot and repair

The AI schema-adapter repair was asked to strip the declared USD prefix before existing dollar range/precision validation. No other currencies were authorized or tested.

Snapshot__4 processed fresh 709-byte source version redacted-evidence-id-015 at 02:15:17–02:15:21 UTC. After reload, six output records matched the independent business expectation.

Stopped: Yes initially. Fix: business preview passed. Severity: Medium (processing blocked).

## Validation and evidence limits

[Repaired preview](evidence/schema-change-type-repaired-preview.json) · [Preview validation](evidence/schema-change-type-repaired-preview-validation.json) · [Initial file check](evidence/schema-change-type-live-file-validation.json)

Preview assertions compare schema, row count, unique/sorted IDs and exact business values against an independent reference. A preview pass does not prove CSV formatting, destination delivery, scheduled execution or determinism. No fresh drift CSV was captured. Missing-output file reports retain that gap; golden data were not presented as platform output.

Initial schema experiments followed restoration of the original snapshot, but the first chatbot request continued server-side after UI cancellation. Its timing limits certainty about the exact executable configuration during the initial matrix. Both semantic defects were therefore repeated independently with the original snapshot restored and the chatbot idle. [Cancellation chronology](evidence/delayed-chatbot-20261005.md).

## Reproduction and schedule behavior

1. In assessment workflow 0, wait for all chatbot work to finish, restore `redacted-evidence-id-034/redacted-evidence-id-027`, and keep both schedules off for this manual reproduction.
2. Replace the same private S3 object with this fixture; record version/hash/time. Refresh Rhombus source access and verify the current input after run/reload.
3. Run the pipeline manually, preserve logs, reload the page, and open the output node's eye preview. Independently check values; do not infer freshness from an already-open preview.
4. Give the actual findings to the AI builder and apply the described explicit repair only. Wait for completion; rerun and capture a fresh preview and actual CSV if available.
5. For the original brief, separately establish successful scheduled baseline/drift/recovery records, capture their real output files and validate independent repetitions under identical input/configuration. Those steps remain outstanding.

Both Custom five-minute and Hourly schedules were inactive throughout these manual tests and at final handoff. No post-drift scheduled recovery is claimed. [Earlier scheduling blocker](scheduling-blocker.md) · [Baseline restored and schedules off](evidence/final-handoff-20261005.json).

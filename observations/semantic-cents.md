# semantic-cents

Status: LIVE MANUAL EVIDENCE; scheduled acceptance and exported-file validation incomplete.

## Change and expectation

Multiply valid monetary input values by 100 while retaining the same column structure; the declared unit changes from dollars to cents. Input: [semantic-cents.csv](../datasets/semantic-cents.csv). [Fixture hashes](../datasets/manifest.json) · [Cleaning contract](../docs/data-contract.md).

Detect the unit change or fail a business-value contract instead of treating cents as dollars.

## Observed result and logs

The initial run completed at 01:58:09 UTC with only O1002/O1003/O1004/O1010, amounts 2550/999/7500/1230. O1001 and O1009 disappeared after the inflated values exceeded the dollar ceiling. Restoring redacted-evidence-id-034 with the chatbot idle and running again at 02:04:47–02:04:49 reproduced the same defect. No unit warning was observed.

Initial source: version `redacted-evidence-id-032`, 685 bytes, uploaded `2026-10-05T01:57:05Z` to the same `input/orders.csv` key. Exact timestamps and source metadata are in the [manual matrix](evidence/manual-drift-matrix-20261005.json). No independent execution run ID was exposed for these manual controls.

## Chatbot and repair

The first cents request was rejected because an earlier request was still running. After that request completed, the AI was explicitly told the input was cents; it patched executable code to divide Decimal cents by 100 before dollar checks. This was an informed repair, not an inferred currency detector.

A fresh post-repair preview had all six correct dollar amounts and records. Independent preview validation passed. Saved redacted-evidence-id-035/redacted-evidence-id-022 preserves the cents-specific repair. The chatbot job identifier is recorded verbatim as unverified provenance.

Stopped: No; success with wrong values. Fix: controlled business preview passed. Severity: High (silent monetary corruption and row loss).

## Validation and evidence limits

[Independent repeat](evidence/semantic-cents-confirmation-preview.json) · [Repeat validation](evidence/semantic-cents-confirmation-preview-validation.json) · [Repaired preview](evidence/semantic-cents-repaired-preview.json) · [Repair validation](evidence/semantic-cents-repaired-preview-validation.json)

Preview assertions compare schema, row count, unique/sorted IDs and exact business values against an independent reference. A preview pass does not prove CSV formatting, destination delivery, scheduled execution or determinism. No fresh drift CSV was captured. Missing-output file reports retain that gap; golden data were not presented as platform output.

Initial schema experiments followed restoration of the original snapshot, but the first chatbot request continued server-side after UI cancellation. Its timing limits certainty about the exact executable configuration during the initial matrix. Both semantic defects were therefore repeated independently with the original snapshot restored and the chatbot idle. [Cancellation chronology](evidence/delayed-chatbot-20261005.md).

## Reproduction and schedule behavior

1. In assessment workflow 0, wait for all chatbot work to finish, restore `redacted-evidence-id-034/redacted-evidence-id-027`, and keep both schedules off for this manual reproduction.
2. Replace the same private S3 object with this fixture; record version/hash/time. Refresh Rhombus source access and verify the current input after run/reload.
3. Run the pipeline manually, preserve logs, reload the page, and open the output node's eye preview. Independently check values; do not infer freshness from an already-open preview.
4. Give the actual findings to the AI builder and apply the described explicit repair only. Wait for completion; rerun and capture a fresh preview and actual CSV if available.
5. For the original brief, separately establish successful scheduled baseline/drift/recovery records, capture their real output files and validate independent repetitions under identical input/configuration. Those steps remain outstanding.

Both Custom five-minute and Hourly schedules were inactive throughout these manual tests and at final handoff. No post-drift scheduled recovery is claimed. [Earlier scheduling blocker](scheduling-blocker.md) · [Baseline restored and schedules off](evidence/final-handoff-20261005.json).

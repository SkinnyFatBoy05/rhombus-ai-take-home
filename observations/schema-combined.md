# schema-combined

Status: LIVE MANUAL EVIDENCE; scheduled acceptance and exported-file validation incomplete.

## Change and expectation

Drop email, rename amount to total_amount, prefix amounts with USD and add campaign. Input: [schema-combined.csv](../datasets/schema-combined.csv). [Fixture hashes](../datasets/manifest.json) · [Cleaning contract](../docs/data-contract.md).

Clearly reject the missing required field. Renaming/type adaptation cannot reconstruct missing emails.

## Observed result and logs

At 01:56:25–01:56:28 UTC the pipeline failed at orders_sorted with “DataFrame should not be empty,” alongside a contradictory success line. Reloaded input confirmed all four changes.

Initial source: version `redacted-evidence-id-016`, 693 bytes, uploaded `2026-10-05T01:56:04Z` to the same `input/orders.csv` key. Exact timestamps and source metadata are in the [manual matrix](evidence/manual-drift-matrix-20261005.json). No independent execution run ID was exposed for these manual controls.

## Chatbot and repair

The schema-adapter request handled the declared alias/prefix and required an explicit missing-field error rather than manufacturing email values.

Fresh version redacted-evidence-id-020 ran under redacted-evidence-id-037 at 02:18:40–02:18:42 UTC. It failed at orders_cleaned naming email, code_sha=redacted-evidence-id-005. The guard is verified; successful recovery remains impossible without a source correction or explicit fallback contract. A success log still contradicted the failure.

Stopped: Yes. Fix: explicit rejection verified, not successful data recovery. Severity: Medium.

## Validation and evidence limits

[Initial file coverage](evidence/schema-combined-live-file-validation.json) · [Detailed repair log](evidence/manual-drift-matrix-20261005.json)

Preview assertions compare schema, row count, unique/sorted IDs and exact business values against an independent reference. A preview pass does not prove CSV formatting, destination delivery, scheduled execution or determinism. No fresh drift CSV was captured. Missing-output file reports retain that gap; golden data were not presented as platform output.

Initial schema experiments followed restoration of the original snapshot, but the first chatbot request continued server-side after UI cancellation. Its timing limits certainty about the exact executable configuration during the initial matrix. Both semantic defects were therefore repeated independently with the original snapshot restored and the chatbot idle. [Cancellation chronology](evidence/delayed-chatbot-20261005.md).

## Reproduction and schedule behavior

1. In assessment workflow 0, wait for all chatbot work to finish, restore `redacted-evidence-id-034/redacted-evidence-id-027`, and keep both schedules off for this manual reproduction.
2. Replace the same private S3 object with this fixture; record version/hash/time. Refresh Rhombus source access and verify the current input after run/reload.
3. Run the pipeline manually, preserve logs, reload the page, and open the output node's eye preview. Independently check values; do not infer freshness from an already-open preview.
4. Give the actual findings to the AI builder and apply the described explicit repair only. Wait for completion; rerun and capture a fresh preview and actual CSV if available.
5. For the original brief, separately establish successful scheduled baseline/drift/recovery records, capture their real output files and validate independent repetitions under identical input/configuration. Those steps remain outstanding.

Both Custom five-minute and Hourly schedules were inactive throughout these manual tests and at final handoff. No post-drift scheduled recovery is claimed. [Earlier scheduling blocker](scheduling-blocker.md) · [Baseline restored and schedules off](evidence/final-handoff-20261005.json).

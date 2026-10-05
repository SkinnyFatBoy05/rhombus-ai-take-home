# semantic-date-order

Status: LIVE MANUAL EVIDENCE; scheduled acceptance and exported-file validation incomplete.

## Change and expectation

Represent the same intended September dates as DD/MM/YYYY instead of MM/DD/YYYY without changing the schema. Input: [semantic-date-order.csv](../datasets/semantic-date-order.csv). [Fixture hashes](../datasets/manifest.json) · [Cleaning contract](../docs/data-contract.md).

Preserve September 1–6 under a declared date contract or flag the format change; syntactically valid but wrong dates must fail semantic checks.

## Observed result and logs

The initial run completed at 02:00:52 UTC with six dates January 9 through June 9. Restoring redacted-evidence-id-034 with the chatbot idle and repeating at 02:08:31–02:08:33 reproduced those wrong dates. Before full reload, the output panel retained the previous test's correct September dates; reload exposed the current wrong output.

Initial source: version `redacted-evidence-id-010`, 669 bytes, uploaded `2026-10-05T02:00:22Z` to the same `input/orders.csv` key. Exact timestamps and source metadata are in the [manual matrix](evidence/manual-drift-matrix-20261005.json). No independent execution run ID was exposed for these manual controls.

## Chatbot and repair

The AI was explicitly given the DD/MM fixture meaning. It patched raw DD/MM parsing and swapped day/month in connector-inferred ISO dates. Its assumption about unambiguous day>12 values was not independently exercised.

After completed AI repair and page reload, six records showed September 1–6 with unchanged correct dollar amounts. Independent preview validation passed. Saved redacted-evidence-id-036/redacted-evidence-id-003 is fixture-specific; it is not a general safe format detector and must not be blindly applied to unrelated ISO datasets.

Stopped: No; success with wrong dates. Fix: controlled business preview passed. Severity: High (silent date corruption).

## Validation and evidence limits

[Independent repeat](evidence/semantic-date-order-confirmation-preview.json) · [Repeat validation](evidence/semantic-date-order-confirmation-preview-validation.json) · [Repaired preview](evidence/semantic-date-order-repaired-preview.json) · [Repair validation](evidence/semantic-date-order-repaired-preview-validation.json)

Preview assertions compare schema, row count, unique/sorted IDs and exact business values against an independent reference. A preview pass does not prove CSV formatting, destination delivery, scheduled execution or determinism. No fresh drift CSV was captured. Missing-output file reports retain that gap; golden data were not presented as platform output.

Initial schema experiments followed restoration of the original snapshot, but the first chatbot request continued server-side after UI cancellation. Its timing limits certainty about the exact executable configuration during the initial matrix. Both semantic defects were therefore repeated independently with the original snapshot restored and the chatbot idle. [Cancellation chronology](evidence/delayed-chatbot-20261005.md).

## Reproduction and schedule behavior

1. In assessment workflow 0, wait for all chatbot work to finish, restore `redacted-evidence-id-034/redacted-evidence-id-027`, and keep both schedules off for this manual reproduction.
2. Replace the same private S3 object with this fixture; record version/hash/time. Refresh Rhombus source access and verify the current input after run/reload.
3. Run the pipeline manually, preserve logs, reload the page, and open the output node's eye preview. Independently check values; do not infer freshness from an already-open preview.
4. Give the actual findings to the AI builder and apply the described explicit repair only. Wait for completion; rerun and capture a fresh preview and actual CSV if available.
5. For the original brief, separately establish successful scheduled baseline/drift/recovery records, capture their real output files and validate independent repetitions under identical input/configuration. Those steps remain outstanding.

Both Custom five-minute and Hourly schedules were inactive throughout these manual tests and at final handoff. No post-drift scheduled recovery is claimed. [Earlier scheduling blocker](scheduling-blocker.md) · [Baseline restored and schedules off](evidence/final-handoff-20261005.json).

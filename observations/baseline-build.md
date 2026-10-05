# Baseline build — initial manual attempts

Status: IN PROGRESS. These are AI-builder-triggered manual runs, not the required
scheduled baseline. Source is the unmodified 12-row `datasets/baseline.csv`.
Independent expected output is six rows.

At 18:29:47 Sydney / 08:29:47 UTC on 30 September the AI builder started the
first run after creating an input, LLM cleaning node, sort and output. At
18:30:29 the log displayed both:

> Pipeline execution completed successfully.

> Pipeline failed at orders_sorted: DataFrame should not be empty.

The failure's expanded details were:

```json
{
  "kind": "pipeline_summary",
  "status": "error",
  "failure": {
    "message": "Pipeline failed at orders_sorted: DataFrame should not be empty.",
    "reason": "DataFrame should not be empty.",
    "nodeId": "sort_node_1",
    "nodeLabel": "orders_sorted",
    "nodeRef": "sort_node_1"
  },
  "nodeId": "sort_node_1",
  "nodeName": "orders_sorted"
}
```

The chatbot said its cleaning node rejected all 12 rows. Its first diagnosis was
that automatic pandas parsing might have changed amount/date types before text
cleaning. That is the chatbot's hypothesis, not an independently established
cause. It changed the prompt to convert values to strings and started another
run at 18:31:03. At 18:31:31 it failed at `orders_output`:

> A destination is required when remote export is selected.

The log again displayed the generic "Pipeline execution completed successfully."
alongside the failure. The chatbot reported that the first three nodes succeeded;
that statement alone does not establish data correctness. No destination object
or successful scheduled run exists yet.

The chatbot's destination instructions referred to **Settings → Destinations**.
The inspected account settings did not contain that section. The actual route is
the Data Output node → **Add New Destination** → **Amazon S3**. Its form requires
Access Key, Secret Key, Region and Bucket Name, and lists both `s3:PutObject` and
`s3:ListBucket`. The chatbot said only PutObject was needed, which does not match
the form's stated requirements. This is observed setup-guidance inconsistency;
the exact operations required by connection verification remain untested.

Preliminary observability finding: a success message adjacent to a same-time
pipeline failure is ambiguous for an operator. Overall failure should be clear,
and task-level completion should be distinguished from pipeline success.

Reproduce from a fresh project by connecting the baseline S3 input, submitting
`docs/ai-builder-prompt-initial.txt` (historical prompt), then opening Logs after the initial AI run. Generated
LLM code can vary between builds; the same prompt does not guarantee this exact
failure. No schedule had been created at this point and no destination success
is claimed.

## Intermediate preview after the second manual attempt

The `orders_cleaned` Preview table displayed six rows with the expected order
IDs, normalized names/email/country and dates. The captured values are in
[baseline-preview.json](evidence/baseline-preview.json). Amounts are displayed
as numbers (for example `120` and `25.5`), so the preview cannot verify the
contract's two-decimal CSV formatting. Selecting Download → Download as CSV
did not produce a capturable download event within 15 seconds in the inbuilt
browser. This is a capture limitation with an unknown cause, not proof that
Rhombus never produced a download.

The snapshot is explicitly intermediate/manual evidence. It is not used to
satisfy destination delivery, successful scheduled baseline, or determinism.

## Local-output manual success

After the candidate selected the no-new-credentials alternative, the Data
Output node was set to Download Locally. A later manual run completed all four
nodes and produced six visible output rows. The AI run tool and UI completion
toast agreed; the reported job ID is
`redacted-evidence-id-002`. The output-node Preview CSV download also
timed out in the inbuilt capture tool, so exact exported bytes remain missing.
The original S3 input was downloaded successfully and its exact SHA-256 matches
the baseline fixture; see [source provenance](evidence/baseline-source.json).
The separate [scheduling blocker](scheduling-blocker.md) remains unresolved.

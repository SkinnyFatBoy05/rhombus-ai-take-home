# Requirements and acceptance criteria

Source: [Rhombus AI take-home brief](https://ripe-lemur-572.notion.site/Software-Engineer-Intern-LLM-Observability-Quality-Assurance-Rhombus-AI-33dcfd62d0a28093bb96cf7df72a2de7), read 29 September 2026 and rechecked against the candidate-supplied link on 5 October; requirements unchanged. Email: “Technical Assessment Details - Rhombus AI”, received 29 September 2026 at approximately 13:44 Australia/Sydney (03:44 UTC). One week ends **6 October 2026**. The email does not specify a separate cut-off time; submit on 5 October if possible rather than relying on an inferred hour across the daylight-saving change.

## Exact exercise requirements (transcribed from the supplied brief)

### Purpose

“Test Rhombus AI the way a customer uses it: as a scheduled ETL pipeline from a cloud source to a cloud destination. Build the pipeline, then break its input on purpose and find out how the platform responds.”

“We are evaluating your judgement, test quality and how clearly you report what you find. We are not grading the platform. A clear, reproducible write-up of something that goes wrong is a strong result.”

### 1. Build the pipeline

- Sign up for Rhombus AI (https://rhombusai.com/).
- Connect Amazon S3 as the source and upload a messy CSV of your choice (duplicates, missing values, inconsistent formatting, invalid entries).
- Build a cleaning pipeline using the AI builder only. No manual transformations.
- Set Google Cloud Storage as the destination.
- Schedule the pipeline at a regular interval. Wait for one successful scheduled run as your baseline.

### 2. Schema drift

“A change to the structure of the data. Before the next scheduled run, change the source file to drop a column, rename a column, change a data type and add a new column. Test each change on its own, then all together, and find out:”

- Does Rhombus AI stop the pipeline, warn, or carry on? If it carries on, what reaches GCS?
- Do the logs explain the problem clearly?
- When you give the error to the chatbot, does it diagnose it correctly, and does its fix actually work?
- What happens to the schedule afterwards?

### 3. Semantic drift

“A change to the meaning of the data while the structure stays the same, for example dollars becoming cents or month/day dates becoming day/month. Introduce at least two cases. Does Rhombus AI notice? Does your data validation catch it?”

### Deliverables

“One GitHub repository containing:”

- `/ui-tests/`: Playwright or Cypress tests automating the pipeline journey (S3 connection, AI-built pipeline, GCS destination, schedule). Runnable from the command line, no fixed sleeps, with assertions on real outcomes.
- `/api-tests/`: at least two tests that call the backend directly (find the requests in the browser's network tab). At least one negative test, such as invalid credentials or an unauthenticated request. Assert on status codes and response contents.
- `/data-validation/`: a script comparing the GCS output with the S3 input. Check schema, row counts, that cleaning rules were applied, determinism, and your semantic drift cases. Run it on the baseline and every drifted run.
- `/datasets/`: the baseline file and every drifted version.
- `/observations/`: one Markdown file per drift case (e.g. `schema-rename-column.md`), covering what you changed, what you expected, what happened, what the logs and chatbot said, and whether the fix worked. Detailed enough to reproduce. Put screenshots and log excerpts in `/observations/evidence/` and link to them.
- `README.md`, with:
  1. Setup and how to run each test suite.
  2. Observations summary: a table with one row per drift case (change, pipeline stopped?, chatbot fix worked?, severity) linking to its file in `/observations/`, plus your top three findings in a few lines.
  3. Usability feedback. One or two paragraphs: what you found most helpful or enjoyable, what was frustrating or difficult, and how we could make the platform more useful and efficient for you.
  4. Demo video link. A short walkthrough of your UI tests, API tests and data validation.

### Optional Bonus: Observability Dashboard

Build and host a live single-page interactive HTML dashboard at a public link, linked in README. Track pipeline health by scenario; output consistency (same input three times for each configuration, side-by-side diffs if different); capability heat map; execution time and resource tracking. **Optional and excluded from this local-only scope.**

Final note: “There is no expectation of perfection. We are looking at judgement, clarity and trade-offs. Quality over quantity.”

## Email submission instructions

- Start a **new email** to `careers@rhombusai.com`.
- Exact subject: **Rhombus AI – Take-Home Exercise** (en dash).
- Include the GitHub repository link.
- Deadline: one week after receipt, 6 October 2026.
- Candidate authorized public publication to `skinnyfatboy05/rhombus-ai-take-home` on 5 October. Email sending remains unauthorized.

## Derived acceptance checks (our interpretation, not an extra employer rubric)

| ID | Observable acceptance check | Evidence/deliverable |
|---|---|---|
| A1 | A successful run was triggered by a schedule, not only Run Now | Run ID, trigger type, schedule, start/end time, fresh GCS object |
| A2 | All four schema changes run independently, plus combined | Five input CSVs, five observations, five validation reports |
| A3 | At least two semantic cases retain the input structure | Cents and day/month files; independent semantic assertions |
| A4 | Browser journey covers S3, AI-only transformations, GCS, schedule | Executed Playwright suite with state/outcome assertions |
| A5 | Two direct backend tests include a negative case | Captured request provenance, status and body assertions |
| A6 | Baseline and every drift run compared to actual S3/GCS snapshots | SHA-256 hashes, object generations/versions, run manifests |
| A7 | Determinism tested without masking row/value differences | Three independent scheduled outputs under identical config/input |
| A8 | Every drift report covers logs, chatbot diagnosis/fix and schedule | Linked redacted evidence and post-fix revalidation |
| A9 | README has all four required sections and accessible video link | Submission readiness check plus human review |

The brief does not prescribe cleaning rules, schema, test timeouts, severity levels or an exact number of repetitions for the mandatory determinism check. Those choices are documented in `data-contract.md` and `runbook.md`. A mock/local run is never evidence of Rhombus behavior.

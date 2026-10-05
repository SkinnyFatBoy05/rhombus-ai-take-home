# Scheduled baseline produces no visible execution record

Status: REPRODUCED / UNRESOLVED. Severity: provisionally High for this assessment because
it prevents verification of scheduled processing. Root cause is unknown.

## Observed sequence

- Changed the existing output node to **Download Locally**, CSV,
  `orders-clean`, and applied it. Canvas read **Export to Download Locally
  (csv)** before any schedule was created.
- Created a custom `* * * * *` schedule, with **Notify on failure off**.
  The UI reported **Active** and counted down to its next run.
- During the approximately 08:49–08:54 UTC window on 30 September, the history
  showed **No results.**, no execution IDs, and a disabled Export CSV button.
  Reopening history and a full page reload did not reveal records.
- Deactivated the schedule and verified **Inactive** / **Activate schedule**.
- Asked the AI builder to inspect the real schedule and run the pipeline once
  manually. Its run tool reported **Pipeline run complete**; the UI toast
  reported successful completion. The reported manual job ID was
  `redacted-evidence-id-002`, all four nodes completed and six output
  rows were displayed. This is manual evidence, not a scheduled baseline.
- Changed the same schedule to `*/5 * * * *` and activated it for another
  supervised check after manual success. At 09:01 UTC, after the 09:00 due
  time, history still showed **No results.**. At approximately 09:05:50 UTC,
  after the next five-minute due time and a full reload, the history remained
  empty. Deactivated the schedule again; **Inactive** was visibly confirmed.

## Chatbot response and reliability

The chatbot correctly distinguished its own agent CronList from the separate
UI scheduling backend and said it could not query or repair that backend.
It made no pipeline repair. However, it also labelled an incorrect chronology
as verified: that local output was corrected only after deactivating the
schedule. The UI interaction record establishes the opposite order.

It suggested that failures might be rate-limited/backed off or hidden. These
are unverified hypotheses, not diagnosed causes. No backend error was visible
in the schedule history. Do not report the schedule as fixed based on this
answer or the manual run's success.

## Reproduction and acceptance

1. Use the baseline S3 object and AI-built pipeline with local CSV output.
2. Confirm a successful manual run.
3. Create/activate a regular schedule, leave failure notifications off, and
   retain the next due time.
4. After the due time, open schedule history using its history icon; reload
   once to rule out an unchanged client view.
5. Require a new execution ID, status and completed-node count. A countdown,
   Active badge or generic success message does not satisfy acceptance.
6. Deactivate the schedule after the bounded observation window.

At the end of the 30 September trial, the schedule was **Inactive**, failure
notifications were off and 40/50 Rhombus credits remained. No support message
was sent.

[Screenshot omitted from public copy; original retained locally.]

This is a cropped browser screenshot of the actual schedule card; personal
account details are excluded. The displayed final cron is `*/5 * * * *`.

## 5 October recheck

After renewal of the same scoped S3 read policy, a manual run again reported
success. The same five-minute schedule was briefly reactivated; its blank
next-run label recovered after re-saving the cron. A subsequent built-in
**Hourly / At minute 00** trial counted down toward 01:00 UTC, then showed no
execution records after that time and a reload. The schedule was deactivated
and restored to custom `*/5 * * * *` while inactive. After the separate AI
formatting-repair attempt, the switch remained off, notifications off and
30/50 credits remained. No drift source was injected.

[Detailed recheck, limitations and current screenshot](evidence/recheck-2026-10-05.md).

Until a genuine scheduled baseline is available, schema/semantic scheduled
drift tests lack their required control run. Do not upload drift sources and
claim that existing preview rows came from a new scheduled execution.

## S3 destination continuation, 5 October afternoon

A connected S3 destination did not resolve the schedule symptom. Custom */5 was enabled, re-saved, counted down toward 15:05 Sydney, then had No results after the due time and a reload. No cleaned object appeared in S3. Both schedules were deactivated and verified inactive. Zero AI credits were visible; this may affect this trial, but earlier failures occurred with credits available. See [S3 output report](s3-output.md).

After the supplied voucher restored 5,000 credits, a bounded repeat with 4,980
credits visible crossed the 15:30 Sydney five-minute boundary. The empty history
persisted after a full reload, with no execution IDs and Export CSV disabled.
Both schedules were deactivated again. The pipeline still had a separate manual
S3-output failure, so the missing history cannot establish whether the scheduler
never attempted execution or failed without an observable record. Credits alone
do not explain this repeat. No failure-notification email was enabled.

[Screenshot omitted from public copy; original retained locally.]

# Continued assessment attempt — 5 October 2026

## Scheduling

Created one additional Hourly schedule for minute 22 with failure emails off.
The existing custom five-minute schedule remained inactive. The creation form
had no visible timezone field, unlike the current official scheduling docs.
The new card counted down to 01:22 UTC / 12:22 Sydney. Its history showed No
results after the due time and after a reload at approximately 01:23 UTC.
It was deactivated at approximately 01:24 UTC. Both switches were confirmed
false. This establishes missing history, not proof that no backend work ran.

Later the canvas Logs panel contained generic start/completion messages at
12:22:51 Sydney. No execution ID or trigger type was visible, so those messages
cannot be conclusively linked to the new schedule. Manual canvas testing then
showed successful start/completion sequences at 12:25:20–23 and 12:25:30–32.
These messages do not establish independent downloaded outputs.

## Supported CLI authentication attempt

Launched the installed Google Chrome channel through Playwright with ordinary
automation settings (no stealth flags or warning bypasses). The candidate
reported a security warning blocked sign-in. Capture was cancelled; it printed
“No new authentication state saved.” The authenticated CLI journey remains
blocked. The signed-in inbuilt browser remains available for manual checks.

## Preserved pipeline

Saved the current pipeline via Canvas → Toolbox → Version Control → Save
Current Version. The UI confirmed redacted-evidence-id-034, version redacted-evidence-id-027, saved at
12:24:47 Sydney. This is a platform version identifier, not a locally computed
full-configuration hash. The snapshot was saved before injecting any drift.

## Boundaries

Google Cloud remains excluded. iCloud is not a documented Rhombus output
destination and would not satisfy the GCS requirement. No employer exception
has been received, and no message has been sent.

Sources: [Scheduling](https://doc.rhombusai.com/docs/getting-started/basic-concepts/scheduling/),
[S3 integration](https://doc.rhombusai.com/docs/Integrations/aws-s3-connection/).
The latter instructs users to Refresh access after source files are replaced.

## Browser handoff and local checks

The candidate later reported a successful normal Chrome sign-in and asked to
use it. Browser discovery exposed Brave and the inbuilt browser only. An exact
Chrome workflow attachment returned “Browser is not available: chrome”. No
Chrome account state was inspected or transferred; the user was asked to
connect the official extension in that Chrome profile. The original baseline
S3 object remains unchanged, and no drift fixture has been uploaded yet.

Capture now accepts supported installed Chrome/Edge channels without changing
security flags. Schedule helpers target the original custom recurrence when
multiple schedule cards exist, and refuse to start if another schedule is
active. Syntax checks, eight Node journey-guard tests and six-test Playwright
discovery passed. The modified card interactions still need an authenticated
CLI run. Existing Python/output-validation and read-only API evidence is reused
because those files and inputs are unchanged. Markdown links resolve. Readiness
continues to return false; no blocked item was relabelled complete.

## Connected Chrome continuation

The official Chrome connection subsequently became available. The candidate's
existing signed-in Chrome tab opened workflow 0 successfully; no cookies or
storage state were extracted. Chrome output Preview showed the six baseline
orders. Download as CSV again produced no captured download within 20 seconds,
and the Downloads folder still contained only the earlier 01:05:58 UTC file.
This does not establish whether the application, download handling or browser
integration caused the failure. No console errors were returned by the exposed
log interface.

The first real drift fixture was then uploaded to the existing S3 key and
executed manually. See [source version and run log](schema-drop-column-live-20261005.json).
The required scheduled baseline remains unverified, so this is supplementary
manual evidence. Both schedules stayed inactive. The input preview retained the
old schema after Refresh access and a page reload. The next actual run failed
at the sort node and also emitted a contradictory success log at the same time.

## Later Chrome drift testing and final handoff

Normal signed-in Chrome worked. All five schema and two semantic cases were
injected into the same versioned S3 key and run manually. The
[manual matrix](manual-drift-matrix-20261005.json) and seven case reports supersede
the earlier not-run status. Each report distinguishes initial failure, diagnosis,
AI repair, independent preview verification and missing scheduled/file evidence.

Cents and ambiguous dates silently produced wrong business values. Both were
reproduced after restoring the original snapshot with the chatbot idle, then
repaired through explicit AI instructions. Rename/type adaptations yielded six
correct fresh-preview records. Drop/combined fixtures now fail at cleaning with
a named missing-email error. Extra campaign was tolerated.

The first chatbot request continued for 21m41s after UI stop controls; this limits
configuration certainty in the initial schema matrix. See
[delayed request](delayed-chatbot-20261005.md). No such overlap was present in the
semantic confirmation runs.

At the end, original baseline bytes were uploaded as version
redacted-evidence-id-038 (02:26:07 UTC), redacted-evidence-id-034 was restored, and a
manual control completed at 02:26:48 UTC with six correct fresh-preview records.
Both schedules are inactive. Source read policy expires at 03:00 UTC / 14:00
Sydney on 5 October. [Final handoff](final-handoff-20261005.json).

A local captioned video was prepared; no GitHub repository, hosted video or email
was created. Authentication in Chrome does not provide the standalone CLI runner
with a supported session. GCS remains unused and its substitution unapproved.

# Verification record — updated 5 October 2026

This records local tool verification and limited real, read-only platform tests. It is not evidence of scheduled pipeline success or drift handling.

| Check | Actual result |
|---|---|
| Python dataset, cleaning, semantic, determinism, provenance and bounded S3 snapshot tests | 34 passed |
| Node target, scope, fresh-outcome and downloaded-data guards | 10 passed on 5 October |
| Live signed-out browser smoke | 1 passed in Playwright Chromium; rerun 5 October |
| Direct backend API tests | 4 passed; exact 401 and Unauthorized body; rerun 5 October |
| Playwright discovery | Six tests listed across public-smoke, ui and api projects |
| Authenticated S3 → AI → local-download CLI journey | Implemented; preflight blocked by missing separate authenticated session. GCS excluded |
| Inbuilt-browser source connection | S3 Connected; actual 669-byte input/orders.csv listed |
| Separate Playwright authenticated login | Blocked by Google's insecure-browser restriction; not bypassed |
| Inbuilt manual local-output run | Tool and completion toast reported success; six expected records/numeric values in preview |
| Scheduled baseline | One-/five-minute custom and built-in Hourly trials showed no execution records; schedule deactivated |
| Seven scheduled drift cases | Scheduled evidence missing; all seven subsequently exercised manually in Chrome |
| Baseline source download | Exact version downloaded; SHA-256 matches 669-byte fixture |
| Baseline validator | Exit 1 on real 382-byte CSV: schema/count/IDs/order pass; four amount strings fail fixed-decimal formatting; independent repeats missing |
| Eight offline fixture checks | Hash/shape/oracle/canary results saved; not live drift evidence |
| Demo walkthrough | Local captioned evidence video prepared; entire MP4 decoded successfully; not hosted |

Environment: Windows, Python 3.11.0, Node 24.11.1, pinned Playwright 1.58.2 / Chromium 145.0.7632.6. Browser workers required host permission outside the restricted process sandbox. First attempts hit spawn EPERM and missing Chromium; installing the matching official browser and running with appropriate host permission resolved those environment issues. No product defect is inferred from them.

Commands: `python -m unittest discover -s tests -p "test_*.py" -v`; `npm test`; `npm run test:smoke`; `npm run test:api`; `npm run test:list`.

The independent provenance tests reject repeated run IDs/object versions, mixed destination providers, stale output, manually triggered runs, changed configurations, modified snapshots, late source writes, missing output and timestamps without timezones. The S3 snapshot tests verify exact-version requests, a 1 MiB download bound and closed response streams. These use test doubles and make no live cloud calls. The semantic tests demonstrate that a conventional parser can accept wrong amounts/dates and that business canaries catch them.

Additional checks: syntax validation passed for `scripts/capture.mjs`; its
cancellation path now closes resources without saving a new auth state. That
changed interactive path has not been re-run against Google. The proposed S3
write policy was parsed and its output-prefix/expiry constraints verified; it
was **not applied**, because the candidate selected local output instead.

`npm run test:ui` was attempted after implementation. Its preflight exited 1
with "Authenticated CLI session missing" before browser mutation. This is not
an executed authenticated Playwright pass. `scripts/readiness.py` also exited 1
for the documented scope/evidence gaps. The ignored `config/live.json`, `.auth`
state path and raw HAR path were confirmed excluded by Git.

On 5 October, the UI journey gained an actual CSV download step and independent
data assertions against the saved S3 input. Two integration checks launch the
real Python validator: the local golden CSV passes data checks while retaining
determinism gaps; a deliberately corrupted amount fails business correctness.
These synthetic tests are not Rhombus execution evidence. Host process permission
was needed for Node to launch Python (`spawn EPERM` inside the restricted sandbox).
All 10 Node tests then passed. Playwright discovers six tests after the output-download case was added. The
authenticated journey still fails its preflight before any live writes because
its separate storage state is missing. The existing 34 Python checks are reused
from 30 September because their source, fixtures and contract have not changed.

The fourth API test uses the actual output-download endpoint observed on 5 October. Its unauthenticated request returned 401 with the exact Unauthorized JSON body. This does not establish whether an authenticated download succeeds.

The candidate subsequently provided an actual local CSV. Original bytes and
the validator report are saved as `baseline-manual-20261005.csv` and
`baseline-manual-20261005-validation.json` in this directory. Numeric amounts
and the other fields match the six expected records. Four amount strings lack
the required trailing decimal zero. The builder attempted a repair but could
not guarantee export formatting; no post-attempt CSV has been validated.

## Chrome continuation and local preview checks

Normal signed-in Chrome enabled all seven supervised manual drift cases on
5 October. This is browser-tool execution, not an authenticated command-line
Playwright pass. See the manual matrix and each case report. Four repairs passed
fresh-preview business checks; missing email now causes an explicit error.

Three new preview-validator unit tests passed: a numeric display pass cannot
certify CSV/schedule/determinism; inflated amounts with row loss fail; wrong dates
and schemas fail. Together with the unchanged 34 earlier tests, 37 Python checks
are verified. No live cloud call is made by these unit tests.

The CLI UI selector now uses the observed output-node eye control and reloads
before reading a fresh preview. JavaScript syntax and discovery of all six
Playwright tests passed after these changes. The authenticated live journey
remains unexecuted; supported CLI storage state is absent.

The local video is a captioned slide walkthrough, not a live screen recording.
It was encoded as H.264/1280×720/24fps with fast-start metadata, approximately
143.96 seconds; decoding the complete MP4 to a null sink returned exit 0.
Selected frames were visually checked. No hosting was performed.

Final control at 02:26:45–02:26:48 UTC used the restored original pipeline and
baseline source. Fresh preview has all six correct business records. Both
schedule switches read aria-checked=false; the screenshot crop preserves the
two Inactive badges. See [handoff evidence](final-handoff-20261005.json).

## S3 automation update, 5 October afternoon

The CLI now supports either local downloads or a preprovisioned S3 destination.
Two new guards require the same assessment bucket, the exact reviewed root
filename/key, and explicit destination provisioning. It never creates or handles
AWS credentials. All **12 Node tests passed**, including the Python integration
checks, after granting local child-process execution permission. An earlier
sandbox-only attempt failed with spawn EPERM; this was not a validator defect.
The 37 unchanged Python checks retain their earlier evidence. Live authenticated
CLI and scheduled output verification remain incomplete.

Four S3 export-witness tests passed: absence vs denied access, stale/old outputs, exact-version retrieval, and wrong-object/unversioned rejection. The S3 branch now validates actual AWS bytes using a separately authorized named read-only profile. No such SDK profile is present locally, so live S3 witness execution is not claimed. With the 37 unchanged earlier Python checks, 41 are verified. The updated 12 Node tests pass; syntax and all six Playwright test definitions were checked again.

## Final documentation and artifact verification

The downloaded Workspace CSV (382 bytes) has SHA-256
`77ebc0ac020e77086b0eaa758f25131a6db0f03534010512994b670a39adaeeb`.
The existing strict validator was executed against those actual bytes and
returned exit 1 for the expected formatting/repetition findings. The video was
rebuilt with the redeemed-credit state and actual Workspace download, then the
complete new MP4 decoded successfully (exit 0). The updated video is 2m40s.
Unchanged implementation tests retain their evidence above; they were not
rerun merely for documentation edits. Readiness remains deliberately nonzero.

## Public-copy verification

After redacting live infrastructure/workflow identifiers, all 41 Python and 12 Node checks passed against this public copy. Synthetic CSV bytes were preserved unchanged. A first Node attempt lacked the installed Playwright dependency; after supplying the existing locked dependencies, all checks passed. Public Markdown links were checked for missing local targets. Original screenshots and unredacted history are excluded.

# GitHub and email submission checklist

Target owner: **skinnyfatboy05**. Proposed repository: **rhombus-ai-take-home**.
Publication authorized on 5 October 2026: **public repository**, https://github.com/SkinnyFatBoy05/rhombus-ai-take-home. Email has not been sent.

## Before requesting publication

- [x] State the GCS deviation prominently. S3 output is now candidate-approved, but neither S3 nor local output has employer approval; do not claim otherwise.
- [ ] Baseline scheduled run and all seven drift cases have actual evidence.
- [ ] UI journey is calibrated and executed against S3, AI builder, GCS and schedule.
- [x] Four backend tests pass with request-discovery evidence, including negative cases.
- [ ] Validator has been run on baseline, every drifted run and every claimed fix.
- [ ] Determinism evidence uses independent runs under identical input/configuration.
- [x] Seven manual observation files distinguish initial failures from chatbot repairs; absent scheduled evidence is explicit.
- [ ] README contains a complete summary table, three evidence-backed findings, usability feedback and working demo link.
- [x] Local captioned video explains UI/API/data checks and observed failures without account details; full playback decode checked.
- [x] Public repository/video publication authorized; links included in README.
- [ ] `python scripts/readiness.py` passes, then manually review the evidence and video.
- [x] Local review ZIP excludes raw HAR, `.auth`, private live config, runtime files and unrelated job-search files; credential-pattern and ZIP-integrity checks pass. Review staged files again before any later publication.
- [x] Restore baseline source/pipeline and verify both assessment schedules inactive after the earlier manual runs.
- [x] After the AWS-output continuation, verify both schedules inactive and restore exact-file export access.
- [ ] Deactivate the export key after testing with candidate authorization; permission expiry alone does not delete a credential.
- [x] User authorizes creation/push to the exact `skinnyfatboy05/rhombus-ai-take-home` repository and chooses visibility.

## After authorization only

Create a standalone repository containing **only this folder**, not the parent job-search repository. Use the `codex/` branch prefix for any working branch. Review `git status` and staged files before committing. No blanket `git add .` from the job-search root. Authenticate GitHub as `skinnyfatboy05` and verify the remote owner before pushing.

If private, ask Rhombus for the GitHub reviewer username and grant access only when authorized. A private link alone is not readable by a recruiter. If public, review every evidence file first. Do not include the recruitment email, voucher, private account configuration or unrelated company background research.

## Submission (separately authorized; not sent)

- Deadline: **6 October 2026**, one week after receipt. No explicit cut-off hour was provided; aim to submit on 5 October.
- New email to **careers@rhombusai.com**, not a reply to the campaign.
- Exact subject: **Rhombus AI – Take-Home Exercise**.
- Include the **actual created GitHub repository URL**, not the proposed URL.
- Verify reviewer access and demo playback before sending.
- Confirm final email text and send authorization. Nothing in this checklist sends an email.

[Prepared unsent email](submission-email-draft.md) explicitly states unresolved checks. If submitting incomplete work, retain those limitations and the nonzero readiness result; never mark gaps complete to obtain a green check.

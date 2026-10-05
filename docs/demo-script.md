# Local evidence walkthrough

[Play the local MP4](../demo/rhombus-evidence-walkthrough.mp4) · [Caption transcript](../demo/walkthrough-transcript.json)

Prepared 5 October 2026: 1280×720 H.264, 24 fps, approximately 2m40s. The entire file decoded successfully with FFmpeg. This is a captioned evidence-slide walkthrough, not a live screen recording, and it does not portray the authenticated journey as passing.

The ten slides cover scope and the GCS deviation, UI/API/data checks, five schema experiments, cents and date corruption before/after explicit AI repairs, observability defects, strict CSV versus preview validation, and remaining submission gaps. Account identifiers and credentials are excluded.

To rebuild on this Windows environment, install Pillow and imageio-ffmpeg from their normal package registries, then run `python scripts/build_demo.py`. The script uses the Windows Segoe UI font. Its temporary frames and optional local dependency folder are under ignored `artifacts/`; only the MP4 and transcript are deliverables.

The [recruiter-accessible video](https://raw.githubusercontent.com/SkinnyFatBoy05/rhombus-ai-take-home/refs/heads/codex/submission/demo/rhombus-evidence-walkthrough.mp4) is included in the public repository authorized by the candidate. If a live recording is added later, show a real authenticated CLI result, scheduled run IDs and actual file validation only when available; retain the limitation disclosures otherwise.

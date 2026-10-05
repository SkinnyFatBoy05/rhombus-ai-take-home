"""Build a captioned local evidence walkthrough, not a live screen recording.

Requires Pillow and imageio-ffmpeg. Optional local dependencies can reside in
ignored artifacts/demo-deps. All slides cite repository evidence; no publication.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'artifacts/demo-deps'))
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W, H = 1280, 720
OUT = ROOT / 'demo'
FRAMES = ROOT / 'artifacts/demo-frames'
OUT.mkdir(exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)
font = lambda size: ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', size)
TITLE, BODY, SMALL = font(44), font(28), font(19)

slides = [
    ('Rhombus AI take-home', 'Evidence walkthrough | 5 October 2026', [
        'Software Engineer: LLM Observability and Quality Assurance',
        'Seven live manual drift cases, AI repairs and independent validation.',
        'Captioned evidence slides. This is not a recording of a passing end-to-end test.',
        'Live acceptance remains incomplete; limitations are shown explicitly.'
    ], 'README.md | docs/requirements.md'),
    ('Workflow and scope', 'S3 source → AI-built cleaning → configured output', [
        'Twelve messy synthetic orders; six intended cleaned records.',
        'One versioned S3 key is replaced for each controlled fixture.',
        'All platform transformations and repairs were made through the AI builder.',
        'GCS was excluded. Local CSV and the later S3 alternative lack an employer exception.'
    ], 'datasets/manifest.json | docs/cloud-setup.md'),
    ('Automation and checks', 'Real assertions; incomplete authentication is visible', [
        '41 Python checks: 37 retained checks plus 4 new S3 freshness checks.',
        '12 Node checks, 1 public browser test and 4 direct API tests passed.',
        'API checks assert HTTP 401 and response content on three observed endpoints.',
        'The authenticated Playwright journey is implemented but has not passed live.'
    ], 'npm test | npm run test:api | observations/evidence/local-verification.md'),
    ('Structural drift', 'Five schema experiments', [
        'Drop email, rename amount, add a USD prefix, add campaign, combine changes.',
        'Four initial cases failed with an empty dataset at the downstream sort step.',
        'Extra campaign was ignored while preserving the six expected records.',
        'AI schema adapters recovered rename/type cases; missing email now has an explicit error.'
    ], 'observations/evidence/manual-drift-matrix-20261005.json'),
    ('Silent monetary corruption', 'Pipeline success did not imply correct business data', [
        'Cents entered as dollars: 25.50 became 2550; only four records survived.',
        'The defect reproduced after restoring the original saved pipeline.',
        'AI repair: Decimal cents ÷ 100 before dollar range and precision checks.',
        'A fresh output preview then matched all six intended records and amounts.'
    ], 'semantic-cents-confirmation-preview.json | semantic-cents-repaired-preview-validation.json'),
    ('Silent date corruption', 'September 1 became January 9', [
        'DD/MM source values were interpreted under the original MM/DD contract.',
        'All six dates changed meaning while the pipeline reported success.',
        'An explicit fixture-specific date repair restored September 1–6.',
        'This is verified for the controlled fixture, not a general date-format detector.'
    ], 'semantic-date-order-confirmation-preview.json | semantic-date-order-repaired-preview-validation.json'),
    ('Observability findings', 'Status and freshness need independent checks', [
        'Failed runs also logged “Pipeline execution completed successfully.”',
        'Schedule countdowns produced no attributable execution-history records.',
        'The output preview sometimes retained earlier data until a full reload.',
        'A stopped chatbot request continued in the background; affected cases were repeated.'
    ], 'observations/scheduling-blocker.md | observations/evidence/delayed-chatbot-20261005.md'),
    ('Validation boundaries', 'Preview values are not downloaded CSV bytes', [
        'Baseline CSV and a downloaded Workspace copy have six correct numeric records.',
        'Four amounts lose required trailing zeros; strict file validation fails.',
        'Preview validation independently catches missing rows, wrong amounts and dates.',
        'Repeated scheduled exports and run-to-file provenance remain unverified.'
    ], 'python data-validation/validate_preview.py EVIDENCE.json --report REPORT.json'),
    ('S3 output continuation', 'Connected destination; actual export still fails', [
        'A scoped, time-limited AWS identity connected the S3 destination.',
        'The connection probe succeeded; actual CSV export failed even in a temporary test.',
        'Single-file permission was restored. Both schedules are inactive.',
        'Voucher restored 5,000 credits; export still fails. No paid upgrade or GCS use.'
    ], 'observations/evidence/s3-destination-diagnostic-20261005.json'),
    ('Submission status', 'Public repository; submission email remains unsent', [
        'Still needed: scheduled evidence, authenticated CLI execution and repeated CSV exports.',
        'GCS substitution remains unapproved; live acceptance gaps are disclosed in README.',
        'Intended GitHub owner: skinnyfatboy05. Deadline: 6 October 2026.',
        'Required subject: Rhombus AI – Take-Home Exercise. Review readiness before submitting.'
    ], 'python scripts/readiness.py | docs/github-submission-checklist.md'),
]


def wrap(draw, text, face, width):
    line = ''
    for word in text.split():
        candidate = (line + ' ' + word).strip()
        if draw.textlength(candidate, font=face) > width and line:
            yield line
            line = word
        else:
            line = candidate
    if line:
        yield line


for index, (title, subtitle, bullets, evidence) in enumerate(slides):
    im = Image.new('RGB', (W, H), '#101923')
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, W, 8), fill='#53d5c8')
    draw.text((64, 44), 'RHOMBUS AI / ASSESSMENT EVIDENCE', font=SMALL, fill='#8bb7c2')
    draw.text((64, 95), title, font=TITLE, fill='#f5f8fc')
    draw.text((64, 155), subtitle, font=BODY, fill='#53d5c8')
    y = 225
    for bullet in bullets:
        draw.ellipse((66, y + 11, 75, y + 20), fill='#53d5c8')
        for line in wrap(draw, bullet, BODY, 1080):
            draw.text((94, y), line, font=BODY, fill='#e1e8ef')
            y += 38
        y += 17
    draw.line((64, 632, 1216, 632), fill='#344453', width=1)
    for j, line in enumerate(wrap(draw, evidence, SMALL, 1070)):
        draw.text((64, 650 + j * 23), line, font=SMALL, fill='#a4b7c9')
    draw.text((1160, 653), f'{index+1}/{len(slides)}', font=SMALL, fill='#a4b7c9')
    im.save(FRAMES / f'{index:02d}.png')

playlist = FRAMES / 'frames.txt'
lines = []
for i in range(len(slides)):
    lines.extend([f"file '{i:02d}.png'", 'duration 16'])
lines.append(f"file '{len(slides)-1:02d}.png'")
playlist.write_text('\n'.join(lines) + '\n', encoding='utf-8')
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
                '-y', '-f', 'concat', '-safe', '0', '-i', str(playlist),
                '-t', str(16 * len(slides)), '-r', '24', '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                str(OUT / 'rhombus-evidence-walkthrough.mp4')], check=True)
(OUT / 'walkthrough-transcript.json').write_text(json.dumps(slides, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(OUT / 'rhombus-evidence-walkthrough.mp4')

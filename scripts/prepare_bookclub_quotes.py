#!/usr/bin/env python3
"""Create editorial REVIEW candidates from publicly available YouTube captions.

This script does NOT publish unverified quotations. Candidates are original
paraphrases based on captions and must be checked against the video by an editor.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
videos=json.loads((ROOT/"videos.json").read_text(encoding="utf-8"))
out=[]
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    raise SystemExit("Install youtube-transcript-api to generate review candidates.")
for v in videos:
    vid=v.get("id")
    if not vid:continue
    try:
        api=YouTubeTranscriptApi()
        transcript=api.fetch(vid,languages=["ko","en"])
        lines=[re.sub(r"\s+"," ",x.text).strip() for x in transcript if x.text and len(x.text.strip())>15]
    except Exception as exc:
        print("No accessible captions:",vid,str(exc)[:90])
        continue
    # Captions are only research notes, not a quotation or approved summary.
    # Avoid copying full transcript or publishing extracted sentences.
    out.append({
        "videoId":vid,"videoTitle":v.get("title",""),
        "publishedAt":v.get("publishedAt",""),
        "url":"https://www.youtube.com/watch?v="+vid,
        "captionAvailable":bool(lines),"captionSegments":len(lines),
        "reviewStatus":"editorial-review-required",
        "editorialPrompt":"Watch video, identify 1–3 core ideas, write a NEW short Korean reflection, translate to English, verify context, then approve.",
        "korean":"","english":"","category":v.get("major") or v.get("category") or "미분류"
    })
dest=ROOT/"quote_candidates.json"
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Created",len(out),"metadata-only review candidates")

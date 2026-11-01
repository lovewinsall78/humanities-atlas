#!/usr/bin/env python3
"""Sync public YouTube channel uploads metadata; no transcript or copyrighted content copied."""
import json, os, urllib.parse, urllib.request
from pathlib import Path

KEY=os.environ.get("YOUTUBE_API_KEY","")
CHANNEL="UCmBrqo-FoqugP5Q4bmLWAEw"
ROOT=Path(__file__).resolve().parent.parent
if not KEY:
    raise SystemExit("Set YOUTUBE_API_KEY GitHub Actions secret.")
def get(endpoint,**params):
    params["key"]=KEY
    url="https://www.googleapis.com/youtube/v3/"+endpoint+"?"+urllib.parse.urlencode(params)
    with urllib.request.urlopen(url,timeout=30) as r:
        return json.load(r)
channel=get("channels",part="contentDetails",id=CHANNEL)
items=channel.get("items",[])
if not items: raise SystemExit("Channel not found")
playlist=items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
ids=[]
page=None
while True:
    args={"part":"snippet","playlistId":playlist,"maxResults":50}
    if page:args["pageToken"]=page
    result=get("playlistItems",**args)
    for item in result.get("items",[]):
        sn=item.get("snippet",{})
        vid=sn.get("resourceId",{}).get("videoId")
        if vid:ids.append(vid)
    page=result.get("nextPageToken")
    if not page:break
existing={}
dest=ROOT/"videos.json"
if dest.exists():
    for v in json.loads(dest.read_text(encoding="utf-8")):
        if v.get("id"):existing[v["id"]]=v
records=[]
for i in range(0,len(ids),50):
    batch=get("videos",part="snippet,status",id=",".join(ids[i:i+50]),maxResults=50)
    for v in batch.get("items",[]):
        if v.get("status",{}).get("privacyStatus")!="public":continue
        sn=v["snippet"];vid=v["id"];old=existing.get(vid,{})
        records.append({"id":vid,"title":sn["title"],"category":old.get("category","미분류"),"status":old.get("status","자료 확인 중"),"publishedAt":sn.get("publishedAt",""),"description":sn.get("description","")[:250]})
records.sort(key=lambda v:v["publishedAt"],reverse=True)
dest.write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Synced",len(records),"public videos")

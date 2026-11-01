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

def classify(title, description=""):
    """Conservative title-based classification; unrecognized items require review."""
    text=(title+" "+description[:150]).lower()
    rules=[
        ("예술","미술",["미술","그림","화가","명화","전시","반 고흐","피카소"]),
        ("예술","음악",["음악","클래식","작곡","베토벤","모차르트"]),
        ("예술","영화",["영화","시네마","감독"]),
        ("과학","뇌과학",["뇌과학","뇌","신경과학"]),
        ("과학","생명과학",["진화","유전자","생물학","다윈","생명과학"]),
        ("과학","천문학",["우주","천문","별","블랙홀"]),
        ("과학","물리학",["양자","물리학","상대성이론"]),
        ("철학","서양철학",["철학","니체","소크라테스","플라톤","칸트","아리스토텔레스","쇼펜하우어","정의란 무엇인가"]),
        ("철학","동양철학",["공자","맹자","노자","장자","논어","도덕경"]),
        ("인문학","역사",["역사","중동","유대","이스라엘","팔레스타인","전쟁","고대","제국"]),
        ("인문학","종교",["종교","불교","기독교","이슬람","성경"]),
        ("인문학","신화",["신화","그리스 신","북유럽 신"]),
        ("문학","고전문학",["오디세이","일리아스","고전문학","노인과 바다","죄와 벌","데미안","그리스 신화","오디세이아"]),
        ("문학","현대문학",["소설","작가","문학","모순","시집","시인","앤 카슨"]),
        ("사회","경제",["경제","돈","부자","투자","자본","레버리지","금융","주식"]),
        ("사회","심리학",["심리","마음","관계","감정","불안","행복"]),
        ("사회","정치",["정치","민주주의","사회문제","국가"]),
        ("삶과 지혜","자기계발",["습관","자기계발","독서 방법","성장","성공","동기부여","루틴","목표"]),
        ("삶과 지혜","인물",["인물","전기","인터뷰","대화"]),
        ("문학","독서",["독서","책 읽기","북클럽","책 추천"]),
    ]
    # Title first, because description may mention unrelated books.
    for major,sub,words in rules:
        if any(word in title.lower() for word in words):
            return major,sub,"제목 기반 자동 분류 · 검수 필요"
    return "미분류","미분류","수동 분류 필요"

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
        major,subcategory,classification_status=classify(sn["title"],sn.get("description",""))
        # Preserve only editor-confirmed classifications.
        if old.get("classificationStatus")=="검수 완료" and old.get("major"):
            major=old["major"]
            subcategory=old.get("subcategory","미분류")
            classification_status="검수 완료"
        record=dict(old)
        record.update({"id":vid,"title":sn["title"],"category":major,"major":major,"subcategory":subcategory,"classificationStatus":classification_status,"status":old.get("status","자료 확인 중"),"publishedAt":sn.get("publishedAt",""),"description":sn.get("description","")[:250]})
        # Preserve editorial summaries, key points, reflection questions and approvals
        # when refreshing metadata. A sync must never erase reviewed learning content.
        records.append(record)
records.sort(key=lambda v:v["publishedAt"],reverse=True)
dest.write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Synced",len(records),"public videos")

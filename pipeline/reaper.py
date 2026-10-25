# Safety: terminate thru-unreal-1 at 17:50 PT even if the lane is not resumed.
import time,json,pathlib,urllib.request,datetime,zoneinfo
POD="<POD_ID>"; tz=zoneinfo.ZoneInfo("America/Los_Angeles")
dl=datetime.datetime.now(tz).replace(hour=17,minute=50,second=0,microsecond=0)
while datetime.datetime.now(tz)<dl: time.sleep(30)
k=[l.split("=",1)[1].strip().strip("\"\x27") for l in (pathlib.Path.home()/".config/runpod.env").read_text().splitlines() if l.strip().removeprefix("export ").startswith("RUNPOD_API_KEY=")][0]
q={"query":"mutation{ podTerminate(input:{podId:\"%s\"}) }"%POD}
r=urllib.request.Request("https://api.runpod.io/graphql",data=json.dumps(q).encode(),headers={"Content-Type":"application/json","Authorization":"Bearer "+k,"User-Agent":"thru-unreal"})
print(datetime.datetime.now(tz),"terminate:",urllib.request.urlopen(r,timeout=60).read()[:200])

import os,json,pathlib,urllib.request,sys
H=pathlib.Path.home()
def envf(p,k):
    for l in pathlib.Path(p).read_text().splitlines():
        l=l.strip().removeprefix("export ")
        if l.startswith(k+"="): return l.split("=",1)[1].strip().strip('"').strip("'")
rk=envf(H/".config/runpod.env","RUNPOD_API_KEY"); gk=envf(H/".config/gemini/hackathon.env","GEMINI_API_KEY")
assert rk and gk
pub=(H/".ssh/id_ed25519.pub").read_text().strip()
def q(query,v):
    r=urllib.request.Request("https://api.runpod.io/graphql",data=json.dumps({"query":query,"variables":v}).encode(),headers={"Content-Type":"application/json","Authorization":"Bearer "+rk,"User-Agent":"thru-unreal"})
    return json.load(urllib.request.urlopen(r,timeout=90))
M="""mutation($i: PodFindAndDeployOnDemandInput){ podFindAndDeployOnDemand(input:$i){ id name machineId costPerHr gpuCount machine{ gpuDisplayName } } }"""
for gpu,cloud in [("NVIDIA GeForce RTX 4090","COMMUNITY"),("NVIDIA RTX A6000","COMMUNITY"),("NVIDIA L40S","COMMUNITY"),("NVIDIA GeForce RTX 4090","SECURE")]:
    i={"name":"thru-unreal-1","imageName":"runpod/base:0.6.2-cuda12.4.1","gpuTypeId":gpu,"gpuCount":1,"cloudType":cloud,
       "containerDiskInGb":250,"volumeInGb":0,"minVcpuCount":8,"minMemoryInGb":32,"ports":"22/tcp","startSsh":True,
       "allowedCudaVersions":["12.4","12.5","12.6","12.7","12.8","12.9"],
       "env":[{"key":"PUBLIC_KEY","value":pub},{"key":"GEMINI_API_KEY","value":gk},{"key":"NVIDIA_DRIVER_CAPABILITIES","value":"all"}]}
    d=q(M,{"i":i})
    p=(d.get("data") or {}).get("podFindAndDeployOnDemand")
    if p: print(json.dumps(p)); sys.exit(0)
    print(gpu,cloud,"fail:",[e.get("message","")[:160] for e in d.get("errors",[])])
sys.exit(1)

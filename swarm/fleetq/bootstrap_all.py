import json,concurrent.futures as cf,sys
sys.argv=["x"];import importlib.util
spec=importlib.util.spec_from_file_location("d","dispatch.py");d=importlib.util.module_from_spec(spec)
src=open("dispatch.py").read().split("if __name__==")[0];exec(compile(src,"dispatch.py","exec"),d.__dict__)
pods=[p for p in json.load(open("fleet-now.json"))["pods"] if p["status"]=="RUNNING" and not p["gpu"] and p["ssh"]]
def go(p):
    try:ok,info=d.bootstrap(p["id"],p["name"]);return p["name"],ok,info.strip()[-160:]
    except Exception as e:return p["name"],False,type(e).__name__+str(e)[:100]
with cf.ThreadPoolExecutor(12) as ex:
    for r in ex.map(go,pods):print(*r,flush=True)

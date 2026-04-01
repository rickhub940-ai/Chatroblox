import os, time, hashlib, requests

URL = os.getenv("UPSTASH_REDIS_REST_URL")
TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
SECRET = "supersecret123"

def r(cmd):
    return requests.post(URL, headers={"Authorization": f"Bearer {TOKEN}"}, json=cmd).json()

def valid(k):
    t = str(int(time.time()/10))
    real = hashlib.sha256((t+SECRET).encode()).hexdigest()
    return k == real

def handler(req):
    if req.method == "POST":
        d = req.json()
        if not valid(d.get("key")): return {"statusCode":403}

        u, t = d.get("user"), d.get("text")
        if not t or len(t)>120: return {"statusCode":400}

        now = int(time.time())
        cd = r(["GET", f"cd:{u}"]).get("result")
        if cd and now-int(cd)<1: return {"statusCode":429}
        r(["SET", f"cd:{u}", now])

        r(["LPUSH","chat",f"{u}: {t}"])
        r(["LTRIM","chat",0,50])

        return {"statusCode":200}

    if req.method == "GET":
        msgs = r(["LRANGE","chat",0,50]).get("result",[])
        return {"statusCode":200,"body":msgs}

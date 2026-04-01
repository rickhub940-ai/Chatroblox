import time, hashlib

SECRET = "supersecret123"

def handler(request):
    t = str(int(time.time() / 10))
    key = hashlib.sha256((t + SECRET).encode()).hexdigest()
    return {"statusCode": 200, "body": {"key": key}}

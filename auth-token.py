import os
import requests
import json

def get_token(request):
    redirect_uri = os.environ.get("REDIRECT_URL")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")


    if "code" in request.args:
        code = request.args.get("code")
        r = requests.post(
                "https://accounts.spotify.com/api/token",
                data= {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri, "client_id":client_id, "client_secret":client_secret},
                headers= {"content-type": "application/x-www-form-urlencoded"}
            )
        return r.json()

    elif "refresh_token" in request.args:
        refresh_token = request.args.get("refresh_token")
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id":client_id, "client_secret":client_secret},
            headers= {"content-type": "application/x-www-form-urlencoded"}
        )
        return r.json()


    data = request.get_json(force=True)

    if "code" in data:
        code = data["code"]
        r = requests.post(
                "https://accounts.spotify.com/api/token",
                data= {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri, "client_id":client_id, "client_secret":client_secret},
                headers= {"content-type": "application/x-www-form-urlencoded"}
            )
        return r.json()

    elif "refresh_token" in data:
        refresh_token = data["refresh_token"]
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id":client_id, "client_secret":client_secret},
            headers= {"content-type": "application/x-www-form-urlencoded"}
        )
        return r.json()

    else:
        return {"message":"error"}

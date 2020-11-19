import os
import base64
import json
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'phirst-e425b',
})

db = firestore.client()


def hello_world(request):
    data = request.get_json(force=True)
    user_id = data["user_id"]
    params = {"code": data["code"]}
    refresh_token = requests.get(
        url="https://us-central1-phirst-e425b.cloudfunctions.net/auth-token",
        params=params
    ).json()["refresh_token"]

    user_ref = db.collection(u'users').document(u'{0}'.format(user_id))
    user_ref.set({"refresh_token": refresh_token}, merge=True)

    params = {"user_id": user_id}

    set_user_albums = requests.get(
        url="https://us-central1-phirst-e425b.cloudfunctions.net/set_user_artists",
        params=params
    ).json()["message"]

    enqueue_user_albums = requests.get(
        url="https://us-central1-phirst-e425b.cloudfunctions.net/enqueue_albums",
        params=params
    ).json()["message"]

    if (enqueue_user_albums != "success"):
        return {"message": "error in enqueue_user_albums"}

    elif (set_user_albums != "success"):
        return {"message": "error in set_user_albums"}

    return {"message": "success"}





import os
import base64
import json
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from google.cloud import tasks_v2

from google.oauth2 import service_account

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': 'phirst-e425b',
})

db = firestore.client()

client = tasks_v2.CloudTasksClient()
parent = client.queue_path('phirst-e425b', 'us-central1', 'update-all-albums')

def update_albums(request):
    docs = db.collection(u'artists').stream()
    # print(len(artist_ids))
    artist_ids = [doc.id for doc in docs]
    for artist in artist_ids:
        payload = {"artist": artist}
        # print(len(all_albums))
        task = {
                "http_request":{
                    "http_method":'POST',
                    "url":'https://us-central1-phirst-e425b.cloudfunctions.net/add_albums',
                    "headers":{"Content-Type": "application/json"},
                    "body": json.dumps(payload).encode()
                }
            }
        # print(task)
        client.create_task(parent=parent, task=task)

    return {"enqueued":artist_ids, "message":"success"}

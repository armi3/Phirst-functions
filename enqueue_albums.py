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
parent = client.queue_path('phirst-e425b', 'us-central1', 'update-artist-albums-queue')


def diff_users_artists_db(user_artists):
    doc_ref = db.collection(u'artists').stream()
    db_artists = {doc.id for doc in doc_ref}
    user_artists = {artist for artist in user_artists}
    return list(user_artists.difference(db_artists))


def get_artists_by_user(userid):
    doc_ref = db.collection(u'users').document(u'{0}'.format(userid))
    doc = doc_ref.get()
    if doc.exists:
        doc = doc.to_dict()
        if 'followed_artists' in doc.keys():
            return diff_users_artists_db(artist for artist in doc["followed_artists"])


def auth():
    CLIENT_ID = "5a1f81af466646cc80d5280641e4b609"
    CLIENT_SECRET = "f1fd209e815048d4a775c8e8c8432633"
    auth_str = bytes('{}:{}'.format(CLIENT_ID, CLIENT_SECRET), 'utf-8')
    b64_auth_str = base64.b64encode(auth_str).decode('utf-8')
    authorization = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {b64_auth_str}"}
    )
    return authorization.json()


def get_artist_albums(artist_id, access_token, offset):
    artist_albums = requests.get(
        url=f"https://api.spotify.com/v1/artists/{artist_id}/albums",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": 50, "include_groups": "album,single", "offset": f"{offset}", "country": "US"}
    )
    return artist_albums.json()


def eliminate_duplicate_albums(albums):
    helping_set = set()
    filtered_albums = []
    for album in albums:
        if (album["name"] not in helping_set):
            helping_set.add(album["name"])
            filtered_albums.append(album)
    return filtered_albums


def enqueue_albums(userid):
    artist_ids = get_artists_by_user(userid)
    # print(len(artist_ids))
    if (len(artist_ids) == 0):
        return {"message": "No diff in artists"}
    access_token = auth()["access_token"]
    for artist in artist_ids:
        # get_albums = get_artist_albums(artist,access_token,0)
        # artist_albums = get_albums["items"]
        # total = get_albums["total"]
        # # print(artist)
        # # print(total)
        # off = 50
        # while(off<total):
        #     artist_albums.extend(get_artist_albums(artist,access_token,off)["items"])
        #     off = off+50
        # # print(len(all_albums))
        # artist_albums=eliminate_duplicate_albums(artist_albums)

        payload = {"artist": artist}
        # print(len(all_albums))
        task = {
            "http_request": {
                "http_method": 'POST',
                "url": 'https://us-central1-phirst-e425b.cloudfunctions.net/add_albums',
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode()
            }
        }
        # print(task)
        response = client.create_task(parent=parent, task=task)

    return {"enqueued": artist_ids, "message": "success"}


def get_albums(request):
    user_id = request.args.get('user_id')
    x = enqueue_albums(user_id)
    return x


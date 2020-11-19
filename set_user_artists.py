import os
import base64
import json
import requests
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': 'phirst-e425b',
})

db = firestore.client()

#artists-----------------------------------------------------------------------------------------------------------------------------------------------------------
def refresh_token(user_id):
    doc_ref = db.collection(u'users').document(u'{0}'.format(user_id))
    doc = doc_ref.get()
    if doc.exists:
        doc = doc.to_dict()
        if 'refresh_token' in doc.keys():
            refresh_token = doc['refresh_token']
    token = requests.get(
        url="https://us-central1-phirst-e425b.cloudfunctions.net/auth-token",
        params={"refresh_token": refresh_token}
    ).json()["access_token"]
    return token


def get_followed_artists(access_token,after=None):
    if after is not None:
        params = {"type":"artist", "limit":50,"after":after}
    else:
        params = {"type":"artist", "limit":50}

    artists = requests.get(
        url="https://api.spotify.com/v1/me/following",
        params=params,
        headers = {"Authorization": f"Bearer  {access_token}"}
    )
    return artists.json()["artists"]["items"]


def add_users_followed_artists_to_db(user_id,artists):
    batch = db.batch()
    user_ref = db.collection(u'users').document(u'{0}'.format(user_id))

    i = 0
    for artist in artists:
        i= i+2
        if i <500:
            batch.set(user_ref,{
                'followed_artists': firestore.ArrayUnion([artist["id"]])},
                merge=True)
        else:
            i = 1
            batch.commit()
            batch.set(user_ref,{
                'followed_artists': firestore.ArrayUnion([artist["id"]])},
                merge=True)
    return batch.commit()

def set_users_followed_artists(request):
    user_id = request.args.get('user_id')
    access_token = refresh_token(user_id)
    followed_artists = get_followed_artists(access_token)
    while ((len(followed_artists)%50)==0):
        followed_artists.extend(get_followed_artists(access_token,followed_artists[-1]["id"]))
    add_users_followed_artists_to_db(user_id,followed_artists)
    return{"message":"success"}




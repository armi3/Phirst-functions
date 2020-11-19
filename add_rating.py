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

def add_rating(request):
    data = request.get_json(force=True)
    user_id = data["user_id"]
    album_id = data["album_id"]
    rating = data["rating"]
    doc_ref = db.collection("ratings").document(f"{user_id}_{album_id}")
    doc_ref.set({
        "rating": rating,
        "user_id":user_id,
        "album_id":album_id
    })
    return {"message":"success"}



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

def get_rating(request):
  data = request.get_json(force=True)
  album_id = data["album_id"]
  query = db.collection("ratings").where("album_id","==",album_id)
  albums = query.get()
  avg = sum(album.to_dict()["rating"] for album in albums) / len(albums)
  return {"avg_rating":avg}



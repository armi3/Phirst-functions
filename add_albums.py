import os
import base64
import json
import requests
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import colorgram
from io import BytesIO
from PIL import Image

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'phirst-e425b',
})

db = firestore.client()


class Empty:
    pass


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


def try_parsing_date(text):
    for fmt in ('%Y-%m-%d', '%Y', '%Y-%m'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    return text


def try_parsing_strftime(text):
    fmt = '%A, %-d %b %Y'
    try:
        return datetime.datetime.strftime(text, fmt)
    except ValueError:
        return "no se puede nmms"


def add_albums_to_db(albums):
    batch = db.batch()

    i = 0

    for album in albums:
        if i < 500:
            i = i + 2
            album_ref = db.collection(u'albums').document(u'{0}'.format(album["id"]))

            if len(album["images"]) > 0:
                thumnail = album["images"][0]["url"]
            else:
                thumnail = "https://images-ext-1.discordapp.net/external/TVT_OEAMIkem05Tonr-UHAivk64yqa_-FTb7Plh0uEo/https/i.scdn.co/image/ab67616d0000b2735bef8a701236e399198d9cf6"

            image = requests.get(thumnail)
            img = Image.open(BytesIO(image.content))
            color = colorgram.extract(img, 1)[0].rgb

            batch.set(album_ref, {
                "album_group": album["album_group"],
                "external_url": album["external_urls"]["spotify"],
                "image": thumnail,
                "name": album["name"],
                "uri": album["uri"],
                "release_date": try_parsing_date(album["release_date"]),
                "release": try_parsing_strftime(try_parsing_date(album["release_date"])),
                "local_created": datetime.datetime.now(),
                "total_tracks": album["total_tracks"],
                "red": color.r,
                "green": color.g,
                "blue": color.b
            }, merge=True)
            artists_refs = []
            artists = []
            for artist in album["artists"]:
                if i < 500:
                    i = i + 3
                    artist_ref = db.collection(u'artists').document(u'{0}'.format(artist["id"]))
                    artists_refs.append(artist_ref)
                    artists.append(artist["name"])
                    batch.set(artist_ref, artist, merge=True)
                    batch.set(artist_ref, {
                        'albums': firestore.ArrayUnion([album_ref])
                    }, merge=True)
                else:
                    i = 3
                    batch.commit()
                    batch = db.batch()
                    artist_ref = db.collection(u'artists').document(u'{0}'.format(artist["id"]))
                    artists_refs.append(artist_ref)

                    batch.set(artist_ref, artist, merge=True)
                    batch.set(artist_ref, {
                        'albums': firestore.ArrayUnion([album_ref])
                    }, merge=True)

            batch.set(album_ref, {
                "artists": artists_refs,
                "artists_names": artists
            }, merge=True)

        else:
            i = 2
            batch.commit()
            batch = db.batch()
            album_ref = db.collection(u'albums').document(u'{0}'.format(album["id"]))

            if len(album["images"]) > 0:
                thumnail = album["images"][0]["url"]
            else:
                thumnail = "https://images-ext-1.discordapp.net/external/TVT_OEAMIkem05Tonr-UHAivk64yqa_-FTb7Plh0uEo/https/i.scdn.co/image/ab67616d0000b2735bef8a701236e399198d9cf6"

            image = requests.get(thumnail)
            img = Image.open(BytesIO(image.content))
            color = colorgram.extract(img, 1)[0].rgb

            image = requests.get(album["images"][0]["url"])
            img = Image.open(BytesIO(image.content))
            color = colorgram.extract(img, 1)[0].rgb
            batch.set(album_ref, {
                "album_group": album["album_group"],
                "external_url": album["external_urls"]["spotify"],
                "image": thumnail,
                "name": album["name"],
                "uri": album["uri"],
                "release_date": try_parsing_date(album["release_date"]),
                "release": try_parsing_strftime(try_parsing_date(album["release_date"])),
                "local_created": datetime.datetime.now(),
                "total_tracks": album["total_tracks"],
                "red": color.r,
                "green": color.g,
                "blue": color.b
            }, merge=True)
            artists_refs = []
            artists = []

            for artist in album["artists"]:
                if i < 500:
                    i = i + 3
                    artist_ref = db.collection(u'artists').document(u'{0}'.format(artist["id"]))
                    artists_refs.append(artist_ref)
                    artists.append(artist["name"])

                    batch.set(artist_ref, artist, merge=True)
                    batch.set(artist_ref, {
                        'albums': firestore.ArrayUnion([album_ref])
                    }, merge=True)
                else:
                    i = 3
                    batch.commit()
                    batch = db.batch()
                    artist_ref = db.collection(u'artists').document(u'{0}'.format(artist["id"]))
                    artists_refs.append(artist_ref)
                    artists.append(artist["name"])

                    batch.set(artist_ref, artist, merge=True)
                    batch.set(artist_ref, {
                        'albums': firestore.ArrayUnion([album_ref])
                    }, merge=True)

            batch.set(album_ref, {
                "artists": artists_refs,
                "artists_names": artists

            }, merge=True)

    return batch.commit()


def add_albums(request):
    artist = request.get_json()["artist"]

    access_token = auth()["access_token"]

    get_albums = get_artist_albums(artist, access_token, 0)
    total = get_albums["total"]
    if (total == 0):
        return {"message": "artist has no albums"}
    artist_albums = get_albums["items"]

    # print(artist)
    # print(total)
    off = 50
    while (off < total):
        artist_albums.extend(get_artist_albums(artist, access_token, off)["items"])
        off = off + 50
    # print(len(all_albums))
    artist_albums = eliminate_duplicate_albums(artist_albums)
    new_albums = [album for album in artist_albums if
                  try_parsing_date(album["release_date"]) >= try_parsing_date("2019")]
    if (len(new_albums) == 0):
        return {"message": "no new albums"}
    did_update_db = add_albums_to_db(new_albums)
    if did_update_db:
        return {"message": "success"}


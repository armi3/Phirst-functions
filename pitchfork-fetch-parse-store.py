import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import base64
import datetime
import feedparser
import requests
from bs4 import BeautifulSoup

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'phirst-e425b',
})

db = firestore.client()
batch = db.batch()


def try_parsing_date(text):
    fmt = '%a, %d %b %Y %H:%M:%S %z'
    try:
        return datetime.datetime.strptime(text, fmt)
    except ValueError:
        return "no se puede nmms"


def try_parsing_strftime(text):
    fmt = '%A, %-d %b %Y'
    try:
        return datetime.datetime.strftime(text, fmt)
    except ValueError:
        return "no se puede nmms"


def get_albums_reviews():
    albums_reviews = feedparser.parse("https://pitchfork.com/rss/reviews/albums/")

    for entry in albums_reviews.entries:
        URL = entry.link
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        result = soup.find(class_='score')
        body = soup.find(class_='contents dropcap')
        date_published = try_parsing_date(entry.published)
        published = try_parsing_strftime(date_published)

        if len(entry.title.split(': ')) < 2:
            album_title = entry.title.split(': ')[0]
            html_title = soup.find('title').string
            artists = html_title.split(': ')[0].split(' / ')
        else:
            album_title = entry.title.split(': ')[1]
            artists = entry.title.split(': ')[0].split(' / ')

        doc_ref = db.collection(u'takes').document(entry.id)
        doc_ref.set({
            u'album_title': album_title,
            u'artists': artists,
            u'thumbnail': entry.media_thumbnail[0]['url'],
            u'source': 'Pitchfork',
            u'author': entry.author,
            u'date_published': date_published,
            u'published': published,
            u'score': result.text,
            u'link': entry.link,
            u'summary': entry.summary,
            u'body': body.text,
            u'local_created': datetime.datetime.now()
        })


def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    get_albums_reviews()
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)

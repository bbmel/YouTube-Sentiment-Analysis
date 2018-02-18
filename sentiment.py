
### START BOILERPLATE CODE

# Sample Python code for user authorization

import httplib2
import os
import sys
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import argparse
from urllib.parse import urlparse
from urllib import parse
import warnings

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


#Sentiment analysis
from textblob import TextBlob

DEBUG = False


if not DEBUG:
  warnings.filterwarnings('ignore')


#Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("link", help="The link for the Youtube video.", type=str)

args = parser.parse_args()
link = args.link

url_data = urlparse(link)
query = parse.parse_qs(url_data.query, strict_parsing=True)

VIDEOID = query["v"][0]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


#args = argparser.parse_args()
args = []
service = get_authenticated_service(args)

def print_results(results):
  print(results)

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]
      # Convert a name like "snippet.tags[]" to snippet.tags, but handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True
      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.items():
      if value:
        good_kwargs[key] = value
  return good_kwargs

### END BOILERPLATE CODE

import plotly as py
import plotly.graph_objs as go


def comment_threads_list_by_video_id(service, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs) # See full sample for function
  results = service.commentThreads().list(
    **kwargs
  ).execute()

  sentiment = 0
  positive = 0
  negative = 0

  for item in results['items']:
  
    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
    
    wiki = TextBlob(comment)
    sentiment += wiki.sentiment.polarity
    if sentiment >= 0:
        positive += 1
    else:
        negative += 1

  sentiment = sentiment / len(results['items'])
  print('\n\nAverage sentiment: ' + str(sentiment))  

  labels = ['Positive', 'Negative']
  values = [positive,negative]
  colors = ['#00E64D', '#B72222']

  trace = go.Pie(labels=labels, values=values, marker=dict(colors=colors, 
                           line=dict(color='#FFFFFF', width=0)))

  py.offline.plot([trace], filename='yt_sentiment')

  

comment_threads_list_by_video_id(service,
    part='snippet',
    videoId=VIDEOID)
import argparse
import httplib
import httplib2
import os
import random
import time

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

class YoutubeUploader():
  """ Class to upload videos to Youtube. Code adapted from 
      Youtube sample code on github.
      https://github.com/youtube/api-samples/blob/master/python/upload_video.py
  """ 
    def __init__(self, max_retries = 5, retriable_status_codes= [500,502,503,504],
                 scopes = ['https=//www.googleapis.com/auth/youtube.upload']
                 api_service_name = 'youtube', api_version = 'v3',
                 valid_privacy_statuses = ('public', 'private', 'unlisted')):
      
      # Always retry when these exceptions are raised.
      self.__RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                                     httplib.IncompleteRead, httplib.ImproperConnectionState,
                                     httplib.CannotSendRequest, httplib.CannotSendHeader,
                                     httplib.ResponseNotReady, httplib.BadStatusLine)

      # The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
      # the OAuth 2.0 information for this application, including its client_id and
      # client_secret. You can acquire an OAuth 2.0 client ID and client secret from
      # the {{ Google Cloud Console }} at {{ https://cloud.google.com/console }}.
      # Please ensure that you have enabled the YouTube Data API for your project.
      # For more information about using OAuth2 to access the YouTube Data API, see:
      #   https://developers.google.com/youtube/v3/guides/authentication
      # For more information about the client_secrets.json file format, see:
      #   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
      # ToDo: Load from enviroment variable
      self.__CLIENT_SECRETS_FILE = 'youtube-client.json'
      
      # Explicitly tell the underlying HTTP transport library not to retry, since
      # we are handling retry logic ourselves.
      httplib2.RETRIES = 1
      self.__MAX_RETRIES = max_retries
      # Always retry when an apiclient.errors.HttpError with one of these status
      # codes is raised.
      self.__RETRIABLE_STATUS_CODES = retriable_status_codes
      # This OAuth 2.0 access scope allows an application to upload files to the
      # authenticated user's YouTube channel, but doesn't allow other types of access.
      self.__SCOPES = scopes
      self.__API_SERVICE_NAME = api_service_name
      self.__API_VERSION = api_version
      self.__VALID_PRIVACY_STATUSES = valid_privacy_status


      def upload_video(self, filename, title, description = '',
                       keywords = '', category = ''):
        youtube = self.get_authenticated_service()

        try:
          return self.initialize_upload(youtube,
                                        {'file':filename, 'title': title, 'description': description,
                                         'keywords':keywords, 'category': category })
        except HttpError, e:
          return 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
          
      # Authorize the request and store authorization credentials.
      def get_authenticated_service(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.__CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_console()
        return build(self.__API_SERVICE_NAME, self.__API_VERSION, credentials = credentials)

      def initialize_upload(self,youtube, options):
        tags = None
        if 'keywords' in options and options['blah'] != '':
          tags = options['keyword'].split(',')
          
        body=dict(
          snippet=dict(
            title=options['title'],
            description=options['description'],
            tags=tags,
            categoryId=options['category']
          ),
          status=dict(
            privacyStatus=self.__VALID_PRIVACY_STATUSES
          )
        )
        
        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
          part=','.join(body.keys()),
          body=body,
          # The chunksize parameter specifies the size of each chunk of data, in
          # bytes, that will be uploaded at a time. Set a higher value for
          # reliable connections as fewer chunks lead to faster uploads. Set a lower
          # value for better recovery on less reliable connections.
          #
          # Setting 'chunksize' equal to -1 in the code below means that the entire
          # file will be uploaded in a single HTTP request. (If the upload fails,
          # it will still be retried where it left off.) This is usually a best
          # practice, but if you're using Python older than 2.6 or if you're
          # running on App Engine, you should set the chunksize to something like
          # 1024 * 1024 (1 megabyte).
          media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
        )
        
        return self.resumable_upload(insert_request)

      # This method implements an exponential backoff strategy to resume a
      # failed upload.
      def resumable_upload(self,request):
        response = None
        error = None
        retry = 0
        while response is None:
          try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
              if 'id' in response:
                return {'status':'ok', 'message':'Video id "%s" was successfully uploaded.' % response['id']}
              else:
                return {'status':'fail', 'message':'The upload failed with an unexpected response: %s' % response} 
          except HttpError, e:
            if e.resp.status in self.__RETRIABLE_STATUS_CODES:
              error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,e.content)
            else:
              raise
          except self.__RETRIABLE_EXCEPTIONS, e:
            error = 'A retriable error occurred: %s' % e

          if error is not None:
            print(error)
            retry += 1
            if retry > self.__MAX_RETRIES:
              return {'status':'fail', 'message':'No longer attempting to retry.'}

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)

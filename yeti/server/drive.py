import httplib2
import os

from apiclient import discovery
from apiclient.http import MediaFileUpload
import oauth2client
from oauth2client import client
from oauth2client import tools

import logging
logger = logging.getLogger(__name__)

class Authorize:
    def __init__(self, callback):
        self.callback = callback
        self.flow = client.flow_from_clientsecrets(
            'client_secret.json',
            scope='https://www.googleapis.com/auth/drive',
            redirect_uri=callback)
        self.flow.params['access_type'] = 'offline'

    def start(self):
        return self.flow.step1_get_authorize_url()

    def complete(self, auth_code):
        store = get_credential_store()
        credentials = self.flow.step2_exchange(auth_code)

        store.put(credentials)


def get_credential_store():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir,'drive-yeti-cam.json')
    store = oauth2client.file.Storage(credential_path)

    return store

def get_credentials():

    store = get_credential_store()
    credentials = store.get()

    return credentials

def upload(filename, event, folder_id):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    media_body = MediaFileUpload(filename, mimetype='image/jpeg', resumable=True)
    body = {
      'name': os.path.basename(filename),
      'description': 'Event: %s' % event,
    }

    if folder_id:
        body['parents'] = [folder_id]

    try:
        upload = service.files().create(
        body=body,
        media_body=media_body).execute()
        logger.debug("Uploaded image to Drive (Id: %s)" % upload['id'])
    except:
        logger.exception("Could not upload image to Drive")
        

def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()

    if not credentials or credentials.invalid:
        print('Invalid credentials. Reauthorize Google API account access')
        return

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(
        pageSize=10,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))
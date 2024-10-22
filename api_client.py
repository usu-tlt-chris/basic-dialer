import base64
import sys

import requests

from api_endpoints import Rooms

class ZoomSession(object):
    def __init__(self, instance_address, account_id, base64_encoded_credentials):
        self.instance_address = instance_address
        self.account_id = account_id
        self.base64_encoded_credentials = base64_encoded_credentials
        self.session = requests.Session()
        response = requests.post(f'https://api.zoom.us/oauth/token?grant_type=account_credentials&account_id={self.account_id}',
            headers={'Authorization': f'Basic {self.base64_encoded_credentials}'})
        if response.status_code == 200:
            response_json = response.json()
            self.session.headers.update({'Authorization': f'Bearer {response_json["access_token"]}'})
        else:
            sys.exit(1)

    def base_request(self, method, uri, data=None):
        uri = self.instance_address + uri
        if method == 'GET':
            response = self.session.get(uri)
            if int(str(response.status_code)[0]) == 2:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                sys.exit(1)
        elif method == 'PATCH':
            response = self.session.patch(uri, json=data)
            if int(str(response.status_code)[0]) == 2:
                return
            else:
                sys.exit(1)

    def get(self, url):
        return self.base_request('GET', url)

    def patch(self, url, data=None):
        return self.base_request('PATCH', url, data=data)

class ZoomClient(object):
    def __init__(self, instance_address, account_id, client_id, client_secret):
        client_id_and_secret = client_id + ':' + client_secret
        client_id_and_secret_base64_encoded_bytes = base64.b64encode(bytes(client_id_and_secret, 'ascii'))
        base64_encoded_credentials = client_id_and_secret_base64_encoded_bytes.decode('ascii')
        self.instance_address = instance_address
        self.account_id = account_id
        self.base64_encoded_credentials = base64_encoded_credentials
        self.client = ZoomSession(self.instance_address, self.account_id, self.base64_encoded_credentials)
        self.rooms = Rooms(self.client)

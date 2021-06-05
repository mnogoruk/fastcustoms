import base64
import hashlib
import hmac
import time
import uuid
from urllib.parse import quote_plus

import requests


class SimpleOAuth:

    def __init__(self, client_id, secret_key, auth_url, **kwargs):
        self.client_id = client_id
        self.secret_key = secret_key
        self.nonce = uuid.uuid4().hex
        self.time_stamp = int(time.time())
        self.auth_url = auth_url
        self.version = kwargs.pop('version', None) or '1.0'
        self.oauth_signature_method = kwargs.pop('oauth_signature_method', None) or 'HMAC-SHA256'
        self.grant_type = kwargs.pop('grant_type', None) or 'client_credentials'

        self._signature = None
        self._access_token = None

    @property
    def access_token(self):
        if self._access_token is None:
            self.refresh_token()
        return self._access_token

    def refresh_token(self):
        self._access_token = self.authenticate()['access_token']

    def authenticate(self):
        self.refresh_temporal_data()
        response = requests.post(self.auth_url, headers=self.to_header(), data={'grant_type': self.grant_type})
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Authentication error")

    def to_header(self) -> dict:
        header = {
            "Authorization": f'OAuth oauth_consumer_key="{self.client_id}", '
                             f'oauth_nonce="{self.nonce}", '
                             f'oauth_signature="{quote_plus(self.signature)}", '
                             f'oauth_signature_method="{self.oauth_signature_method}", '
                             f'oauth_timestamp="{self.time_stamp}", '
                             f'oauth_version="{self.version}"'}
        return header

    @property
    def signature(self) -> bytes:
        if self._signature is None:
            hmc = hmac.new(f'{self.secret_key}&'.encode(), self.create_base_string().encode(), hashlib.sha256)
            self._signature = base64.b64encode(hmc.digest())
        return self._signature

    def create_base_string(self) -> str:
        method = 'POST'
        url = self.auth_url
        params = f'grant_type={self.grant_type}' \
                 f'&oauth_consumer_key={self.client_id}' \
                 f'&oauth_nonce={self.nonce}' \
                 f'&oauth_signature_method={self.oauth_signature_method}' \
                 f'&oauth_timestamp={self.time_stamp}' \
                 f'&oauth_version={self.version}'

        return f'{quote_plus(method)}&{quote_plus(url)}&{quote_plus(params)}'

    def refresh_temporal_data(self):
        self.nonce = uuid.uuid4().hex
        self.time_stamp = int(time.time())
        self._signature = None

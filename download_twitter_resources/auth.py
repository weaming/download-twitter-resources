import base64
import logging

import requests

from .exceptions import *

lg = logging.getLogger("downloader")


class TwitterAuth:
    def __init__(self, api_key, api_secret):
        self.bearer_token = self.bearer(api_key, api_secret)
        lg.info("Bearer token is " + self.bearer_token)

    def bearer(self, key, secret):
        """Receive the bearer token and return it.

        Args:
            key: API key.
            secret: API string.
        """

        # setup
        credential = base64.b64encode(
            bytes("{}:{}".format(key, secret), "utf-8")
        ).decode()
        url = "https://api.twitter.com/oauth2/token"
        headers = {
            "Authorization": "Basic {}".format(credential),
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        payload = {"grant_type": "client_credentials"}

        # post the request
        r = requests.post(url, headers=headers, params=payload)

        # check the response
        if r.status_code == 200:
            return r.json()["access_token"]
        else:
            raise BearerTokenNotFetchedError()

    def auth_headers(self):
        return {"Authorization": "Bearer {}".format(self.bearer_token)}

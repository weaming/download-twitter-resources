import base64
import logging

import requests
from rauth import OAuth1Service

from .exceptions import *

lg = logging.getLogger("downloader")


class TwitterAuth:
    def __init__(
        self,
        consumer_key,
        consumer_secret,
        access_token=None,
        access_token_secret=None,
        private=False,
    ):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.private = private
        if not private:
            self.bearer_token = self.bearer(consumer_key, consumer_secret)
            lg.info("Bearer token is " + self.bearer_token)
        else:
            self.bearer_token = None

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

    def session(self):
        if self.private:
            return self.oauth1a_session(
                self.consumer_key, self.consumer_secret, callback='oob'
            )
        else:
            headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
            s = requests.Session()
            s.headers = headers
            return s

    def oauth1a_session(
        self,
        consumer_key,
        consumer_secret,  # , access_token=None, access_token_secret=None
        callback=None,
    ):
        twitter = OAuth1Service(
            name='twitter',
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            base_url='https://api.twitter.com/1.1/',
        )

        request_token, request_token_secret = twitter.get_request_token(
            params=callback and {'oauth_callback': callback}
        )
        authorize_url = twitter.get_authorize_url(request_token)
        print('Visit this URL in your browser: {url}'.format(url=authorize_url))
        pin = input('Enter PIN from browser: ')

        session = twitter.get_auth_session(
            request_token,
            request_token_secret,
            method='POST',
            data={'oauth_verifier': pin},
        )
        return session

import base64
import json
import logging

import requests

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
            if access_token and access_token_secret:
                self.access_token = access_token
                self.access_token_secret = access_token_secret
            else:
                # get access_token through API
                self.access_token, self.access_token_secret = (
                    self.pin_based_access_token()
                )

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

    def auth_headers(self, url=None, params=None, method=None):
        if self.private:
            if not (url and method):
                raise Exception(f'missing url, params, method')
            headers = self.oauth1a(
                url,
                params,
                method,
                self.consumer_key,
                self.consumer_secret,
                self.access_token,
                self.access_token_secret,
            )
            print(headers)
            return headers
        else:
            return {"Authorization": "Bearer {}".format(self.bearer_token)}

    def pin_based_access_token(self,) -> tuple:
        return 1, 1

    def oauth1a(
        self,
        url,
        params,
        method,
        consumer_key,
        consumer_secret,
        access_token=None,
        access_token_secret=None,
    ) -> dict:
        """
        https://gist.github.com/awojnowski/3044890
        """
        import random
        import string
        import time
        from urllib.parse import quote_plus, urlparse
        import hmac
        import hashlib

        def timestamp():
            return int(round(time.time()))

        def generateNonce():
            nonce = ''.join(
                random.choice(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits
                )
                for x in range(32)
            )
            return nonce

        def signatureBaseForRequest(url, params, method):
            param_string = ""
            for key in sorted(params.keys()):
                string = key + "=" + json.dumps(params[key])
                if param_string.__len__() > 0:
                    param_string += "&" + string
                else:
                    param_string = string

            params = quote_plus(param_string)
            url = urlparse(url)
            url = "https://api.twitter.com" + url.path
            url = quote_plus(url)
            method = method.upper()
            signature_base = method + "&" + url + "&" + params
            return signature_base

        def signingKey():
            return consumer_secret + "&" + access_token_secret

        def signSignature(signature_base, signing_key):
            digest = hmac.new(
                signing_key.encode('utf8'), signature_base.encode('utf8'), hashlib.sha1
            ).digest()
            signature = base64.b64encode(digest).decode('utf8')
            signature = signature[:-1]  # remove newline
            print('oauth_signature', signature)
            return signature

        def signatureForRequest(url, params, method):
            signature_base = signatureBaseForRequest(url, params, method)
            signature = signSignature(signature_base, signingKey())
            return signature

        def headerDictionaryWithoutSignature():
            headers = {}
            headers["oauth_consumer_key"] = consumer_key
            headers["oauth_nonce"] = generateNonce()
            headers["oauth_signature_method"] = "HMAC-SHA1"
            headers["oauth_timestamp"] = str(timestamp())
            headers["oauth_token"] = access_token
            headers["oauth_version"] = "1.0"
            return headers

        def headerStringForRequest(url, params, method):
            headers = headerDictionaryWithoutSignature()
            for key in headers.keys():
                params[key] = headers[key]
            headers["oauth_signature"] = signatureForRequest(url, params, method)

            headers_keys = sorted(headers.keys())
            headerString = "OAuth "
            for key in headers_keys:
                value = headers[key]
                string = quote_plus(key) + "=\"" + quote_plus(value) + "\", "
                headerString += string

            headerString = headerString[:-2]  # remove the ", "
            return headerString

        return {"Authorization": headerStringForRequest(url, params, method)}

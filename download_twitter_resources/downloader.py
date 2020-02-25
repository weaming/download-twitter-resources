import logging
import os
import json
import subprocess

from download_twitter_resources.auth import TwitterAuth, lg
from .async_executor import AsyncDownloader, prepare_dir
from .exceptions import *

DEBUG = os.getenv("DEBUG")
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)


def get_terminal_size():
    rows, columns = subprocess.check_output(['stty', 'size']).split()
    return int(rows), int(columns)


rows, columns = get_terminal_size()


class Downloader:
    def __init__(
        self,
        consumer_key,
        consumer_secret,
        access_token=None,
        access_token_secret=None,
        thread_number=4,
        private=False,
    ):
        self.auth = TwitterAuth(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            private=private,
        )
        self.session = self.auth.session()
        self.last_tweet = None
        self.count = 0
        self.d = AsyncDownloader(100)
        self.d.start(thread_number)

    def download_images_of_user(
        self,
        user,
        save_dest,
        size="large",
        limit=3200,
        rts=False,
        include_video=False,
        keys_included=[],
        keys_excluded=[],
    ):
        """Download and save images that user uploaded.

        Args:
            user: User ID.
            save_dest: The directory where images will be saved.
            size: Which size of images to download.
            rts: Whether to include retweets or not.
        """

        if not os.path.isdir(save_dest):
            try:
                prepare_dir(save_dest)
            except Exception as e:
                raise InvalidDownloadPathError(str(e))

        num_tweets_checked = 0
        tweets = self.get_tweets(user, self.last_tweet, limit, rts)
        if not tweets:
            lg.info("Got an empty list of tweets")

        while len(tweets) > 0 and num_tweets_checked < limit:
            for tweet in tweets:
                self.process_tweet(
                    tweet,
                    save_dest,
                    include_video=include_video,
                    keys_included=keys_included,
                    keys_excluded=keys_excluded,
                )
                num_tweets_checked += 1

            tweets = self.get_tweets(user, self.last_tweet, count=limit)

        lg.info(
            f"no more tweets or the number of tweets checked reach the limit {limit}"
        )

    def process_tweet(
        self,
        tweet,
        save_dest,
        size="large",
        include_video=False,
        keys_included=[],
        keys_excluded=[],
    ):
        id_str = tweet["id_str"]
        preview_mode = bool(keys_included or keys_excluded)
        self.last_tweet = tweet["id"]
        if preview_mode:
            text = tweet['text']
            if any(x in text for x in keys_excluded):
                return 0

            if any(x in text for x in keys_included):
                print(tweet['created_at'], tweet['id'])
                print(json.dumps(tweet, ensure_ascii=False))
                print('-' * columns)
                images = self.extract_media_list(tweet, include_video)
                return len(images)
            return 0
        else:
            # save the image
            images = self.extract_media_list(tweet, include_video)
            for i, image in enumerate(images, 1):
                self.save_media(image, save_dest, f"{id_str}-{i}", size)
            return len(images)

    def get_tweets(self, user, start=None, count=200, rts=False):
        """Download user's tweets and return them as a list.

        Args:
            user: User ID.
            start: Tweet ID.
            rts: Whether to include retweets or not.
        """

        # setup
        url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        payload = {"screen_name": user, "count": count, "include_rts": rts}
        if start:
            payload["max_id"] = start

        # get the request
        r = self.session.get(url, params=payload)

        # check the response
        if r.status_code == 200:
            tweets = r.json()
            if len(tweets) == 1:
                return []
            else:
                lg.info("Got " + str(len(tweets)) + " tweets")
                return tweets if not start else tweets[1:]
        else:
            lg.error(
                f"An error occurred with the request, status code was {r.status_code}"
            )
            lg.error(r.text)
            return []

    def get_tweet(self, id):
        """Download single tweet

        Args:
            id: Tweet ID.
        """

        url = "https://api.twitter.com/1.1/statuses/show.json"
        payload = {"id": id, "include_entities": "true"}

        # get the request
        r = self.session.get(url, params=payload)

        # check the response
        if r.status_code == 200:
            tweet = r.json()
            lg.info(f"Got tweet with id {id} of user @{tweet['user']['name']}")
            return tweet
        else:
            lg.error(
                f"An error occurred with the request, status code was {r.status_code}"
            )
            lg.error(r.text)
            return None

    def extract_media_list(self, tweet, include_video):
        """Return the url of the image embedded in tweet.

        Args:
            tweet: A dict object representing a tweet.
        """
        rv = []

        extended = tweet.get("extended_entities")
        if not extended:
            return rv

        if "media" in extended:
            for x in extended["media"]:
                if x["type"] == "photo":
                    url = x["media_url"]
                    rv.append(url)
                elif x["type"] in ["video", "animated_gif"]:
                    if include_video:
                        variants = x["video_info"]["variants"]
                        variants.sort(key=lambda x: x.get("bitrate", 0))
                        url = variants[-1]["url"].rsplit("?tag")[0]
                        rv.append(url)
                # else:
                #     import pdb
                #
                #     pdb.set_trace()
        return rv

    def save_media(self, image, path, name, size="large"):
        """Download and save an image to path.

        Args:
            image: The url of the image.
            path: The directory where the image will be saved.
            name: It is used for naming the image.
            size: Which size of images to download.
        """
        if image:
            # image's path with a new name
            ext = os.path.splitext(image)[1]
            save_dest = os.path.join(path, name + ext)
            if ext not in [".mp4"]:
                real_url = image + ":" + size
            else:
                real_url = image

            # save the image in the specified directory (or don't)
            prepare_dir(save_dest)
            if not (os.path.exists(save_dest)):
                self.d.add_url(real_url, save_dest)
            else:
                lg.info(f"Skipping downloaded {image}")

import os
import sys
import argparse
import json
import re
from . import Downloader
from .exceptions import *


def get_tweet_id(url):
    """
    https://twitter.com/KittenYang/status/1067790621375516673
    """
    return re.match(r"(https://.+?status/)?([0-9]{10,})", url).group(2)


def main():
    parser = argparse.ArgumentParser(
        description="Download all images uploaded by a twitter user you specify"
    )
    parser.add_argument(
        "resource_id",
        help="An ID of a twitter user. Also accept tweet url or tweet id.",
    )
    parser.add_argument("dest", help="Specify where to put images")
    parser.add_argument(
        "-c",
        "--confidential",
        help="a json file containing a key and a secret",
        default=os.getenv("TWITTER_AUTH", os.path.expanduser("~/.twitter.json")),
    )
    parser.add_argument(
        "-s",
        "--size",
        help="specify the size of images",
        default="orig",
        choices=["large", "medium", "small", "thumb", "orig"],
    )
    parser.add_argument(
        "--tweet",
        help="indicate you gived a tweet url or tweet id",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--video", help="include video", default=False, action="store_true"
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        help="the maximum number of tweets to check (most recent first)",
        default=3200,
    )
    parser.add_argument(
        "--rts", help="save images contained in retweets", action="store_true"
    )
    parser.add_argument("--thread-number", type=int, default=4)
    parser.add_argument(
        "--private", help="download private resources", action='store_true'
    )
    parser.add_argument("--keys-included", help="filter tweets", nargs='*')
    parser.add_argument("--keys-excluded", help="filter tweets", nargs='*')
    args = parser.parse_args()
    print(args)

    if args.confidential:
        with open(args.confidential) as f:
            confidential = json.loads(f.read())
        if "consumer_key" not in confidential or "consumer_secret" not in confidential:
            raise ConfidentialsNotSuppliedError()

        consumer_key = confidential["consumer_key"]
        consumer_secret = confidential["consumer_secret"]
        access_token = confidential["access_token"]
        access_token_secret = confidential["access_token_secret"]
    else:
        raise ConfidentialsNotSuppliedError(args.confidential)

    downloader = Downloader(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        args.thread_number,
        args.private,
    )
    if args.tweet:
        try:
            args.resource_id = get_tweet_id(args.resource_id)
        except Exception as e:
            print(e)
            sys.exit(1)

        tweet = downloader.get_tweet(args.resource_id)
        downloader.process_tweet(tweet, args.dest, args.size, args.video)
        downloader.d.join()
    else:
        downloader.download_images_of_user(
            args.resource_id,
            args.dest,
            args.size,
            args.limit,
            args.rts,
            args.video,
            keys_included=args.keys_included or [],
            keys_excluded=args.keys_excluded or [],
        )
        downloader.d.join()
    print('finished!')


if __name__ == "__main__":
    main()

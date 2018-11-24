import os
import argparse
import json
from . import Downloader
from .exceptions import *


def main():
    parser = argparse.ArgumentParser(
        description="Download all images uploaded by a twitter user you specify"
    )
    parser.add_argument("user_id", help="an ID of a twitter user")
    parser.add_argument("dest", help="specify where to put images")
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
    args = parser.parse_args()

    if args.confidential:
        with open(args.confidential) as f:
            confidential = json.loads(f.read())
        if "consumer_key" not in confidential or "consumer_secret" not in confidential:
            raise ConfidentialsNotSuppliedError()
        api_key = confidential["consumer_key"]
        api_secret = confidential["consumer_secret"]
    else:
        raise ConfidentialsNotSuppliedError(args.confidential)

    downloader = Downloader(api_key, api_secret, args.thread_number)
    downloader.download_images(
        args.user_id, args.dest, args.size, args.limit, args.rts, args.video
    )


if __name__ == "__main__":
    main()

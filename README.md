# Download twitter resources

Download tweet images and videos. Run threads which has a event loop to download resources asynchronously.

```
pip3 install download-twitter-resources
```

```
usage: download-twitter-resources [-h] [-c CONFIDENTIAL]
                                  [-s {large,medium,small,thumb,orig}]
                                  [--tweet] [--video] [-l LIMIT] [--rts]
                                  [--thread-number THREAD_NUMBER]
                                  resource_id dest

Download all images uploaded by a twitter user you specify

positional arguments:
  resource_id           An ID of a twitter user. Also accept tweet url or
                        tweet id.
  dest                  Specify where to put images

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIDENTIAL, --confidential CONFIDENTIAL
                        a json file containing a key and a secret
  -s {large,medium,small,thumb,orig}, --size {large,medium,small,thumb,orig}
                        specify the size of images
  --tweet               indicate you gived a tweet url or tweet id
  --video               include video
  -l LIMIT, --limit LIMIT
                        the maximum number of tweets to check (most recent
                        first)
  --rts                 save images contained in retweets
  --thread-number THREAD_NUMBER
```

About API rate limits: https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits
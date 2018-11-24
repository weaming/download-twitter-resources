# Download twitter resources

Download tweet images and videos

```
pip3 install download-twitter-resources
```

```
usage: download-twitter-resources [-h] [-c CONFIDENTIAL]
                                  [-s {large,medium,small,thumb,orig}]
                                  [--video] [-l LIMIT] [--rts]
                                  user_id dest

Download all images uploaded by a twitter user you specify

positional arguments:
  user_id               an ID of a twitter user
  dest                  specify where to put images

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIDENTIAL, --confidential CONFIDENTIAL
                        a json file containing a key and a secret
  -s {large,medium,small,thumb,orig}, --size {large,medium,small,thumb,orig}
                        specify the size of images
  --video               include video
  -l LIMIT, --limit LIMIT
                        the maximum number of tweets to check (most recent
                        first)
  --rts                 save images contained in retweets
```

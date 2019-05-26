import os
import asyncio
from queue import Queue
from threading import Thread
import aiohttp
import logging
import time


def run_async_func_in_loop(future):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(future)
    return result


def run_in_thread(fn, *args, **kwargs):
    thread = Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def prepare_dir(path):
    path = os.path.abspath(path)
    if not path.endswith("/"):
        path = os.path.dirname(path)

    if not os.path.isdir(path):
        os.makedirs(path)


def get_proxy():
    for k in ["http_proxy", "https_proxy"]:
        for kk in [k, k.upper()]:
            v = os.getenv(kk)
            if v:
                return v


class AsyncDownloader:
    def __init__(self, maxsize=1000):
        self.q = Queue(maxsize)
        self.finish_q = Queue(maxsize)
        self.logger = logging.getLogger("async.downloader")
        self.threads = []

    def start(self, n=4):
        for _ in range(n):
            thread = run_in_thread(run_async_func_in_loop, self.run())
            self.threads.append(thread)
            self.logger.debug(thread)

    def join(self):
        while not self.q.empty() or not self.finish_q.empty():
            self.logger.info('waiting to empty queue')
            time.sleep(5)

    def add_url(self, url, dest):
        self.q.put((url, dest))
        self.logger.debug(f"added ({url}, {dest})")

    async def run(self):
        while 1:
            url, dest_path = self.q.get()
            # add one running task
            self.finish_q.put(url)
            await self.download(url, dest_path)
            # finished one task
            self.finish_q.get()

    async def download(self, url, dest):
        prepare_dir(dest)
        async with aiohttp.ClientSession() as session:
            proxy = get_proxy()
            self.logger.debug(f"got proxy {proxy}")
            async with session.get(url, proxy=proxy) as response:
                if response.status == 200:
                    data = await response.read()
                    with open(dest, "wb") as f:
                        f.write(data)
                        self.logger.info(f"{url} ==> {dest}")
                else:
                    self.logger.warning(
                        f"url {url} reponse status code is {resonse.status}"
                    )

import sys
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

import redirect

import multiprocessing as mp
import youtube_dl

# User changable variables

redirectionPort = 8000
videoFormat = "mp4"
url = "https://www.youtube.com/watch?v="
# url = "https://www.youtube.com/playlist?list="

# ------------------------

urls = []
downloads = []
downloadData = []


class Download:

    def __init__(self, url):
        self.url = url
        self.output = ""

        def enqueue_output(out, queue):
            for line in iter(out.readline, b""):
                queue.put(line)
            out.close()

        ON_POSIX = 'posix' in sys.builtin_module_names

        process = Popen(['axel', "-c", self.url],
                        stdout=PIPE,
                        close_fds=ON_POSIX)

        self.queue = Queue()
        thread = Thread(target=enqueue_output,
                        args=(process.stdout, self.queue))
        thread.daemon = True
        thread.start()

    def progress(self):
        while (True):
            try:
                line = self.queue.get_nowait()
            except Empty:
                break
            else:
                self.output = line

        return self.output


def main():
    ydl_opts = {'format': videoFormat}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)

    if 'entries' in result:
        for video in result['entries']:
            urls.append(video['url'])
    else:
        video = result
        urls.append(video['url'])

    redirector = mp.Process(target=redirect.redirect,
                            args=(urls, redirectionPort))
    redirector.daemon = True
    redirector.start()

    i = 0
    while i < len(urls):
        downloads.append(Download(f"127.0.0.1:{redirectionPort}/{str(i)}"))
        i += 1

    print("enter 'Exit' to close")

    while (True):
        select = input(f"Press Key 0-{len(urls)-1}: ")
        if (select == "Exit" or select == "exit"):
            redirector.terminate()
            print("Done")
            exit()
        if int(select) < len(urls):
            print(downloads[select].progress())
        else:
            print(
                f"enter number within range: 0-{len(urls)-1}, [or 'Exit' to exit]"
            )


if __name__ == "__main__":
    main()

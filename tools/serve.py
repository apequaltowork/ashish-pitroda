"""
Local preview server that never lets the browser cache anything.

    python tools/serve.py            http://localhost:5180
    python tools/serve.py 8000       another port

`python -m http.server` sends no cache headers, so browsers keep old copies
of pages and journal.css and a change seems not to have happened. This sends
Cache-Control: no-store on every response, so a plain refresh always shows
the files as they are on disk.
"""
import functools
import http.server
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Expires", "0")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5180
    handler = functools.partial(NoCache, directory=ROOT)
    with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
        print("serving " + ROOT + " at http://localhost:" + str(port) + " (no cache)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

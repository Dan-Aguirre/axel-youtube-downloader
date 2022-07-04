#!/bin/python3

import http.server
import socketserver

def redirect(urls, port):
        class myHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                        path = self.path

                        self.send_response(301)
                        self.send_header('Location', urls[int(path[1:])])
                        self.end_headers()

                def log_message(self, format, *args):
                        return

        Handler = myHandler

        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", port), Handler)

        print("serving at port", port)
        httpd.serve_forever()
# encoding: utf-8
# Copyright (C) 2013 John Törnblom
#
# This file is part of LLVM-P86.
#
# LLVM-P86 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LLVM-P86 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LLVM-P86.  If not, see <http://www.gnu.org/licenses/>.

'''
Simple web server that serves mutation data.
'''

import os
import json
from argparse import ArgumentParser

try:
    # Python 2
    import SimpleHTTPServer
    import SocketServer
except:
    # Python 3
    from http.server import SimpleHTTPServer
    from socketserver import SocketServer


class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith(".mut"):
            self.do_mutation('data' + self.path[:-4])

        elif self.path.startswith('/search?id='):
            self.do_search(self.path[11:])

        elif self.path == "/":
            self.do_index()

        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_search(self, query):
        prefix = "<html><body>"
        s = ''
        postfix = "</body></html>"
        hits = 0

        for f in os.listdir("data"):
            if not f.endswith(".json"):
                continue

            ds = json.load(open('data/' + f))

            for m in ds['mutants']:
                if str(m['id']) == query:
                    s += '<a href="%s.mut#%s">%s</a><br>' % (f[:-5],
                                                             query,
                                                             f[:-5])
                    hits += 1

        if hits == 0:
            s = "<p>Mutant %s not found!</p>" % query
            self.wfile.write(prefix + s + postfix)
        elif hits == 1:
            self.send_response(301)
            self.send_header('Location', '%s.mut#%s' % (f[:-5], query))
            self.end_headers()
        else:
            html = prefix + s + postfix
            self.send_response(200)
            self.send_header('Content-Length', len(html))
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html)

    def do_index(self):
        source_files = []
        data_files = []

        for f in os.listdir("data"):
            if f.endswith(".p"):
                source_files.append(f[:-2])
            elif f.endswith(".json"):
                data_files.append(f[:-5])

        html = "<html><body>"

        for f in sorted(data_files):
            if f in source_files:
                html += '<a href="%s.mut">%s</a><br>' % (f, f)

        html += "</body></html>"

        self.send_response(200)
        self.send_header('Content-Length', len(html))
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html)

    def do_mutation(self, name):
        html = '''
                <html>
                <head>
                <script type="text/javascript" src="js/xx.js"></script>
                <script type="text/javascript" src="js/jquery-1.10.1.min.js">
                </script>
                <script type="text/javascript" src="js/sh_main.js"></script>
                <script type="text/javascript" src="js/sh_pascal.js"></script>
                <link type="text/css" rel="stylesheet" href="css/sh_style.css">
                <link type="text/css" rel="stylesheet" href="css/xx.css">
                </head>

                <body onload="xx_load('%s');">
                  <div id="info_wrapper">
                    <div id="info" style="display: none;" class="fixed">
                      <table>
                      <tr>
                        <td>
                          <span class="xx_label">Mutation: </span>
                        </td>
                        <td>
                          <span id="report"></span>
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <span class="xx_label">Source file: </span>
                        </td>
                        <td>
                          <span id="filename"></span>
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <span class="xx_label">Mutant: </span>
                        </td>
                        <td>
                          <select id="current_mutant" style="display: none;">
                            <option value="0">Original</option>
                          </select>
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <span class="xx_label">MD5: </span>
                        </td>
                        <td>
                          <span id="md5"></span>
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <span class="xx_label">Time stamp: </span>
                        </td>
                        <td>
                          <span id="timestamp"></span>
                        </td>
                      </tr>
                      </table>
                    </div>
                  </div>
                  <div id="popup" style="display: none;"></div>
                  <pre id="code" class="sh_pascal"></pre>
                </body>
                </html>''' % name

        self.send_response(200)
        self.send_header('Content-Length', len(html))
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html)


class MyTCPServer(SocketServer.TCPServer):
    allow_reuse_address = True


def run():
    try:
        parser = ArgumentParser()
        parser.add_argument("-p", "--port", dest="port", action="store", default="8000", help="selects the port that the http server will bind to")
        parser.add_argument("-r", "--root", dest="root", action="store", default="wwwroot", metavar="PATH", help="path pointing at the www root")

        args = parser.parse_args()

        httpd = MyTCPServer(("", int(args.port)), MyHandler)
        httpd.allow_reuse_address = True
        if args.root:
            os.chdir(args.root)

        print(("Serving mutation reports at http://localhost:%s" % args.port))
        httpd.serve_forever()

        return 0

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0

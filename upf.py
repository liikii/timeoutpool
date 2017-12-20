#!/usr/bin/python3
"""
you'll need to parse this to get the filename and the embedded data. 
I think the mime-related tools in the standard library's email package 
are probably the best way to parse this once you've gotten it saved to a file.
# https://stackoverflow.com/questions/25529804/tornado-mime-type-of-the-stream-request-body-output/25584849
"""
import tornado.ioloop
import tornado.web
from tornado import options
from tornado.httpserver import HTTPServer

from urllib.parse import unquote


page = """<!DOCTYPE html>
<html>
<body>

<form action="/" method="post" enctype="multipart/form-data">
  Select images: <input type="file" name="files" multiple/>
  <input type="submit" value='up it'>
</form>

<p>Try selecting more than one file when browsing for files.</p>

<p><strong>Note:</strong> The multiple attribute of the input tag is not supported in Internet Explorer 9 and earlier versions.</p>

</body>
</html>"""


@tornado.web.stream_request_body
class PUTHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.bytes_read = 0

    def data_received(self, chunk):
        print('get chunk haha')
        self.bytes_read += len(chunk)

    def post(self):
        mtype = self.request.headers.get('Content-Type')
        print('post "%s" "%s" %d bytes', 'file_name', mtype, self.bytes_read)
        self.write('OK')
        self.redirect("/")

    def get(self):
        self.write(page)


def make_app():
    return tornado.web.Application([
        (r"/.*", PUTHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    max_buffer_size = 10 * 1024 ** 4  # 10 GB
    http_server = HTTPServer(
        app,
        max_buffer_size=max_buffer_size,
    )
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()


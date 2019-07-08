import socket
import urllib.parse
import _thread

from utils import log

from routes import (
    error,
    route_static,
    route_dict,
    # login_required,
)

# 用 from import as 来避免重名
from routes_todo import route_dict as routes_todo



class Request(object):
    def __init__(self, raw_data):

        log('这是你的rawdata:\n', raw_data)
        m = raw_data.split('\r\n\r\n', 1)
        for i in m:
            log('这是你的rawdata拆分后：\n', i, '拆分结束')
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        path = parts[1]
        self.path = ""
        self.query = {}
        self.parse_path(path)
        log('Request: path 和 query', self.path, self.query)

        self.headers = {}
        self.cookies = {}
        self.add_headers(h[1:])
        log('Request: headers 和 cookies', self.headers, self.cookies)

    def add_headers(self, header):

        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            k, v = cookies.split('=', 1)
            self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f

    def parse_path(self, path):

        index = path.find('?')
        if index == -1:
            self.path = path
            self.query = {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            self.path = path
            self.query = query


def response_for_path(request):

    r = route_dict()
    r.update(routes_todo())
    response = r.get(request.path, error)
    return response(request)


def process_connection(connection):
    with connection:
        r = connection.recv(1024)
        log('线程：走到这一步了！'.format(r.decode()))
        r = r.decode()
        log('线程：这到这两步获得request了！', r)
        request = Request(r)
        response = response_for_path(request)
        log("http response:<\n{}\n>".format(response))
        connection.sendall(response)


def run(host, port):

    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            _thread.start_new_thread(process_connection, (connection,))


if __name__ == '__main__':
    config = dict(
        host='localhost',
        port=3000,
    )
    run(**config)

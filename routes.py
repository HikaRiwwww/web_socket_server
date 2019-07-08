import time

from utils import log
from models.message import Message
from models.user import User
from models.session import Session

import random


def random_string():
    seed = 'sdfsdafasfsdfsdwtfgjdfghfg'
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def template(name):

    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def current_user(request):
    log('cookies:', request.cookies)
    log('???***', 'session_id' in request.cookies)
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        s = Session.find_by(session_id=session_id)
        log('session is here', s)
        if s is None or s.expired():
            return User.guest()
        else:
            user_id = s.user_id
            u = User.find_by(id=user_id)
            if u is None:
                return User.guest()
            else:
                return u
    else:
        return User.guest()


def error(request):

    return b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>'


def response_with_headers(headers, code=200):

    header = 'HTTP/1.x {} VERY OK\r\n'.format(code)
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def redirect(url):

    headers = {
        'Location': url,
    }

    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode()


def route_index(request):

    header = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    u = current_user(request)
    log('current_user:', u)
    body = body.replace('{{username}}', u.username)
    r = header + '\r\n' + body
    return r.encode()


def route_login(request):
    headers = {
        'Content-Type': 'text/html',
    }
    user_current = current_user(request)
    if request.method == 'POST':
        form = request.form()
        user_login = User.login_user(form)
        if user_login is not None:

            session_id = random_string()
            form = dict(
                session_id=session_id,
                user_id=user_login.id,
            )
            s = Session.new(form)
            s.save()
            headers['Set-Cookie'] = 'session_id={}'.format(session_id)
            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''

    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', user_current.username)

    header = response_with_headers(headers)
    r = '{}\r\n{}'.format(header, body)
    return r.encode()


def route_register(request):
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    r = header + '\r\n' + body
    return r.encode()


def route_message(request):
    if request.method == 'POST':
        data = request.form()
    else:
        data = request.query

    if len(data) > 0:
        m = Message.new(data)
        log('post', data)
        m.save()

    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('messages.html')
    ms = '<br>'.join([str(m) for m in Message.all()])
    body = body.replace('{{messages}}', ms)
    r = header + '\r\n' + body
    return r.encode()


# @login_required
def route_static(request):

    filename = request.query['file']
    path = 'static/{}'.format(filename)
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
        r = header + b'\r\n' + f.read()
        return r


def route_dict():

    d = {
        '/': route_index,
        '/static': route_static,
        '/login': route_login,
        '/register': route_register,

    }
    return d


from datetime import datetime
from models.todo import Todo
from models.user import User
from routes import (
    redirect,
    template,
    current_user,
    response_with_headers,
)
    # login_required)
from utils import log


def formatted_time():
    dt = datetime.utcnow()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')
    return ds


def index(request):
    """
    todo 首页的路由函数
    """
    # u = current_user(request)
    todos = Todo.all()
    # todos = Todo.find_all(user_id=u.id)

    # 修改后后带创建时间和修改时间的html
    todo_html = """
        <h3>
            {} : {}  创建时间:{}  修改时间:{}
            <a href="/todo/edit?id={}">编辑</a>
            <a href="/todo/delete?id={}">删除</a>
        </h3>

    """
    todo_html = ''.join([
        todo_html.format(
            t.id, t.title, t.created_time, t.updated_time, t.id, t.id
        ) for t in todos
    ])

    # 替换模板文件中的标记字符串
    body = template('todo_index.html')
    body = body.replace('{{todos}}', todo_html)

    # 下面 3 行可以改写为一条函数, 还把 headers 也放进函数中
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode()


def add(request):
    """
    用于增加新 todo 的路由函数
    """
    form = request.form()
    u = current_user(request)

    t = Todo.new(form)
    t.user_id = u.id
    t.created_time = formatted_time()
    t.save()
    return redirect('/todo')
    # return index(request)


def delete(request):
    todo_id = int(request.query['id'])
    Todo.delete(todo_id)
    return redirect('/todo')


def edit(request):
    u = current_user(request)
    # 获取当前用户
    if u.is_guest():
        return redirect('/login')
    # 判断是游客则返回登陆界面
    else:
        todo_id = int(request.query['id'])
        t = Todo.find_by(id=todo_id)
        log('编辑函数下查找todo对象时：', t.created_time, t.updated_time)
        # 通过todo_id获取todo对象
        if t.user_id == u.id:
            # 如果todo对象的用户id和当前用户id一致
            body = template('todo_edit.html')
            body = body.replace('{{todo_id}}', str(todo_id))
            body = body.replace('{{todo_title}}', str(t.title))
            # 下面 3 行可以改写为一条函数, 还把 headers 也放进函数中
            headers = {
                'Content-Type': 'text/html',
            }
            header = response_with_headers(headers)
            r = header + '\r\n' + body
            return r.encode()
        else:
            # 当前用户非todo创建用户则返回/todo路径
            return redirect('/todo')


# @login_required
def update(request):
    u = current_user(request)
    # 获取当前用户
    if u.is_guest():
        return redirect('/login')
    # 判断是游客则返回登陆界面
    else:
        form = request.form()
        todo_id = int(form['id'])
        # 获取todo_id
        t = Todo.find_by(id=todo_id)
        log('拿到todo对象时：', t.created_time, t.updated_time)
        if t.user_id == u.id:
            t.title = form['title']
            t.updated_time = formatted_time()
            t.save()
            return redirect('/todo')
        else:
            return redirect('/todo')


def admin_users(request):
    u = current_user(request)
    log('判断是否为鹳狸猿：', u.is_admin())
    if u.is_admin():
        users = User.all()
        admin_users_html = """
                <h3>
                   id: {} 用户名：{}  密码：{} 
                </h3>
    
            """
        admin_users_html = ''.join([
            admin_users_html.format(
                user.id, user.username, user.password
            ) for user in users
        ])

        # 替换模板文件中的标记字符串
        body = template('admin_users.html')
        body = body.replace('{{users}}', admin_users_html)
        headers = {
            'Content-Type': 'text/html',
        }
        header = response_with_headers(headers)
        r = header + '\r\n' + body
        return r.encode()
    else:
        return redirect('/')


def admin_update(request):
    u = current_user(request)
    if u.is_admin():
        form = request.form()
        log(form)
        edit_user_id = int(form['id'])
        edit_user = User.find_by(id=edit_user_id)
        edit_user.password = form['newpwd']
        edit_user.save()
        return redirect('/admin/users')
    else:
        return redirect('/login')








def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/todo': index,
        '/todo/add': add,
        '/todo/delete': delete,
        '/todo/edit': edit,
        '/todo/update': update,
        '/admin/users': admin_users,
        '/admin/users/update': admin_update
    }
    return d

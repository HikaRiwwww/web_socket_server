import json

from models.user_role import DmEncoder, dm_decode
from utils import log
from datetime import datetime


def save(data, path):
    s = json.dumps(data, indent=2, ensure_ascii=False, cls=DmEncoder)
    with open(path, 'w+', encoding='utf-8') as f:
        log('save', path, s, data)
        f.write(s)


def load(path):

    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        log('load', s)
        return json.loads(s, object_hook=dm_decode)


class Model(object):
    def __init__(self, form):
        self.id = form.get('id', None)
        # self.id = None

    @classmethod
    def db_path(cls):
        classname = cls.__name__
        path = 'db/{}.txt'.format(classname)
        return path

    @classmethod
    def new(cls, form):
        m = cls(form)
        return m

    @classmethod
    def delete(cls, id):
        ms = cls.all()
        for i, m in enumerate(ms):
            if m.id == id:
                del ms[i]
                break
        l = [m.__dict__ for m in ms]
        path = cls.db_path()
        save(l, path)


    @classmethod
    def all(cls):
        path = cls.db_path()
        models = load(path)
        log('models in all', models)
        ms = [cls(m) for m in models]
        return ms

    @classmethod
    def find_by(cls, **kwargs):
        log('find_by kwargs', kwargs)

        for m in cls.all():
            exist = True
            for k, v in kwargs.items():
                if not hasattr(m, k) or not getattr(m, k) == v:
                    exist = False
            if exist:
                return m

    @classmethod
    def find_all(cls, **kwargs):
        log('find_all kwargs', kwargs)
        models = []

        for m in cls.all():
            exist = True
            for k, v in kwargs.items():
                log('for loop in find all', m, k, v, hasattr(m, k), getattr(m, k), getattr(m, k) == v)
                if not hasattr(m, k) or not getattr(m, k) == v:
                    exist = False
            if exist:
                models.append(m)

        return models

    def save(self):
        models = self.all()
        log('models', models)

        if self.id is None:
            # 加上 id
            if len(models) > 0:
                log('不是第一个元素', models[-1].id)
                self.id = models[-1].id + 1
            else:
                log('第一个元素')
                self.id = 0
            models.append(self)
        else:

            for i, m in enumerate(models):
                if m.id == self.id:
                    models[i] = self

        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)

    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(classname, s)

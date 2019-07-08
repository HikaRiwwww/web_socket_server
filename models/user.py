from models import Model
from models.user_role import UserRole


class User(Model):
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """

    def __init__(self, form):
        super().__init__(form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.role = form.get('role', UserRole.normal)
        # self.role = form.get('role', 'normal')
        # self.admin = form.get('admin', False)

    @staticmethod
    def guest():
        form = dict(
            role=UserRole.guest,
            username='【游客】',
            id=-1,
        )
        u = User(form)
        return u

    def is_guest(self):
        return self.role == UserRole.guest

    def is_admin(self):
        return self.role == UserRole.admin


    @classmethod
    def login_user(cls, form):
        u = User.find_by(username=form['username'], password=form['password'])
        return u

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2

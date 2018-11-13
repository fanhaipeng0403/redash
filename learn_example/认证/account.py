import os

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import EmailType
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='./')


class BaseModel(Model):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(True), default=func.now(), onupdate=func.now(), nullable=False)

    @classmethod
    def create(cls, **kw):
        session = db.session
        if 'id' in kw:
            obj = session.query(cls).get(kw['id'])
            if obj:
                return obj
        obj = cls(**kw)
        session.add(obj)
        session.commit()
        return obj

    def to_dict(self):
        columns = self.__table__.columns.keys()
        return {key: getattr(self, key) for key in columns}


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../cnblogblog.db'
db = SQLAlchemy(app, model_class=BaseModel)


####User Model
class User(db.Model):
    __tablename__ = 'users'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(320))
    email = Column(EmailType)
    password_hash = Column(db.String(128), nullable=True)
    disabled_at = Column(db.DateTime(True), default=None, nullable=True)

    def verify_password(self, password):
        return self.password_hash and check_password_hash(self.password, password)

    def hash_password(self, password):
        self.encrypt_password = generate_password_hash(password,
                                                       method='pbkdf2:sha512',
                                                       salt_length=64)

    @property
    def is_disabled(self):
        return self.disabled_at is not None

    def disable(self):
        self.disabled_at = db.func.now()

    def enable(self):
        self.disabled_at = None


###

# 第一步
##### 基于cookie的session实现，并且使用secret_key加密
####  Flask-Login uses sessions for authentication.
app.secret_key = os.urandom(16)

# 第二步
# 注册
######
login_manager = LoginManager()
login_manager.init_app(app)


# 第三步
# 储存user_id到session里，可以从中获取current_user对象
@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.query.get(user_id)
        if user.is_disabled:
            return None
        return user
    except NoResultFound:
        return None


@app.route('/')
def index():
    return '我是主页'


# 第四部

@app.route('/login', methods=['GET', 'POST'])
def login():
    index_url = url_for("index")
    # 对next_path的处理
    next_path = request.args.get('next', index_url)
    if current_user.is_authenticated:
        return redirect(next_path)

    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email'])
            if user and not user.is_disabled and user.verify_password(request.form['password']):
                remember = ('remember' in request.form)
                login_user(user, remember=remember)
                return redirect(next_path)
            else:
                flash("Wrong email or password.")
        except NoResultFound:
            flash("Wrong email or password.")

    return render_template("login.html",
                           next=next_path,
                           email=request.form.get('email', ''))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

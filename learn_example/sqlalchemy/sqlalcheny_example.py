# coding:utf-8
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ***************************
# 初始化数据库连接
engine = create_engine('sqlite:///./cnblogblog.db', echo=True)
# 参数 sqlite:///foo.db 解释为： sqlite://<nohostname>/<path>
# 其中foo.db是相对路径。也可写成： sqlite:///./foo.db

# 创建对象的基类
Base = declarative_base()
# 创建会话类
DBSession = sessionmaker(bind=engine)


# ******************
# 定义User对象
class User(Base):
    """Users table"""
    # 表的名字
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}
    # 表结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    age = Column(Integer, default=0)
    password = Column(String(64), unique=True)


class Blog(Base):
    """docstring for Blog"""
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    desc = Column(String(500))


class Tips(Base):
    """docstring for Tips"""

    __tablename__ = 'tips'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))


# ***********************
# 添加一条数据
def newUser():
    # 创建会话对象
    session = DBSession()
    new_user = User(name='Jery', password='123')
    session.add(new_user)
    session.commit()
    session.close()


# 添加一条数据
def addUserForZhCn():
    session = DBSession()
    new_user = User(name=u'关羽2', password='12322233')
    session.add(new_user)
    session.commit()
    session.close()


# 新增多条数据
def addmoreUser():
    session = DBSession()
    session.add_all([
        User(name='guanyu', age=4, password='11111'),
        User(name='zhangfei', password='2233'),
        User(name='zhenji', password='44556')
    ])
    session.commit()
    session.close()


# 查询
def queryUser():
    session = DBSession()
    quser = session.query(User).filter(User.id == 4).one()
    print('name:', quser.name)
    session.close()


# 删除
def deleteUser():
    session = DBSession()
    duser = session.query(User).filter(User.id == 2).delete()
    session.commit()
    session.close()


# 执行sql语句
def SQlUser():
    s = DBSession()
    # 不能用 `?` 的方式来传递参数 要用 `:param` 的形式来指定参数
    # s.execute('INSERT INTO users (name, age, password) VALUES (?, ?, ?)',('bigpang',2,'1122121'))
    # 这样执行报错

    # s.execute('INSERT INTO users (name, age, password) VALUES (:aa, :bb, :cc)',({'aa':'bigpang2','bb':22,'cc':'998'}))
    # s.commit()
    # 这样执行成功
    res = s.execute('select * from users where age=:aaa', {'aaa': 4})
    # print(res['name'])  # 错误
    # print(res.name)    # 错误
    # print(type(res))   # 错误
    for r in res:
        print(r['name'])
    s.close()


# 执行sql语句
def SQlUser2():
    # **传统 connection方式**
    # 创建一个connection对象，使用方法与调用python自带的sqlite使用方式类似
    # 使用with 来创建 conn，不需要显示执行关闭连接
    # with engine.connect() as conn:
    # 	res=conn.execute('select * from users')
    # 	data=res.fetchone()
    # 	print('user is %s' %data[1])
    # 与python自带的sqlite不同，这里不需要 cursor 光标，执行sql语句不需要commit。如果是增删改，则直接生效，也不需要commit.

    # **传统 connection 事务**
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            r1 = conn.execute("select * from users")
            print(r1.fetchone()[1])
            r2 = conn.execute("insert into users (name,age,password) values (?,?,?)", ('tang', 5, '133444'))
            trans.commit()
        except:
            trans.rollback()
            raise
    # **session**
    session = DBSession()
    session.execute('select * from users')
    session.execute('insert into users (name,age,password) values (:name,:age,:password)',
                    {"name": 'dayuzhishui', 'age': 6, 'password': '887'})
    # 注意参数使用dict，并在sql语句中使用:key占位
    # 如果是增删改，需要 commit
    session.commit()
    # 用完记得关闭，也可以用 with
    session.close()


# 更多操作
def TestUser():
    session = DBSession()


# test1
# 使用merge方法，如果存在则修改，如果不存在则插入（只判断主键，不判断unique列）
# t1=session.query(User).filter(User.name=='zhenji').first()
# t1.age=34
# session.merge(t1)
# session.commit()
# test2
# merge方法，如果数据库中没有则添加
# t2=User()
# t2.name='haha'
# session.merge(t2)
# session.commit()
# test3
# 获取第2-3项
# tUser=session.query(User)[1:3]
# for u in tUser:
# 	print(u.id)
# test4
#
if __name__ == '__main__':
    # 删除全部数据库
    Base.metadata.drop_all(engine)

    # 初始化数据库
    Base.metadata.create_all(engine)
    # 删除全部数据库
    # Base.metadata.drop_all(engine)
    # 删除指定的数据库
    # 如删除 Blogs表
    # 详见 ：http://stackoverflow.com/questions/35918605/how-to-delete-a-table-in-sqlalchemy
    # Blog.__table__.drop(engine)

    # 新增数据
    newUser()
    # 新增多条数据
    addmoreUser()
    # 新增数据含中文
    addUserForZhCn()
    # 查询数据
    queryUser()

    # 删除
    # deleteUser()
    # 测试
    # TestUser()

    # 执行sql语句
    SQlUser()

    # 执行sql语句2
    SQlUser2()
    print('ok')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy import Column, Integer, String, DateTime, func


# 定制model基类
# https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/mixins.html
# http://flask-sqlalchemy.pocoo.org/2.3/customizing/

# 2.1版本之后才可以

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


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./cnblogblog.db'

db = SQLAlchemy(app, model_class=BaseModel)


class MyDataClass3(db.Model):
    __tablename__ = 'my_data3'
    id = Column(Integer, primary_key=True)
    data = Column(Integer)
    name = Column(String(50))


if __name__ == '__main__':
    # db.create_all()
    # data = MyDataClass3(data=1, name='xxx')
    # db.session.add(data)
    # db.session.commit()
    #
    # data = db.session.query(MyDataClass3).first()
    #
    # print(MyDataClass3.query.first().to_dict())

###################### flask sqlalchemy 的分页函数
    data = db.session.query(MyDataClass3)

    #总共多少行
    total =data.paginate(2, 5).total
    # 5表示5个5个的分，2表示去第二页
    items =data.paginate(2, 5).item # 返回的[6,7,8,9,10]






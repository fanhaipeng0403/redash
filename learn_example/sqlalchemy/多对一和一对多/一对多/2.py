# (backref ="parent")
"""
https://docs.sqlalchemy.org/en/latest/orm/relationships.html

    # last_modified_by = db.relationship(User, backref="modified_queries", foreign_keys=[last_modified_by_id])
    # visualizations = db.relationship("Visualization", cascade="all, delete-orphan")
    # user = db.relationship(User, backref='favorites')
    # grantor = db.relationship(User, backref='grantor', foreign_keys=[grantor_id])
    # grantor = db.relationship(User, backref='grantor', foreign_keys=[grantor_id])
    # user = db.relationship(User, backref='changes')
    # user = db.relationship(User, backref='changes')
    # org = db.relationship(Organization, back_populates="events")


主要学习RelationShip

"""
# https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html
from flask import Flask
from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy import Column, Integer, DateTime, func, ForeignKey, String

# 2.1版本之后才可以
from sqlalchemy.orm import relationship


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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../cnblogblog.db'

db = SQLAlchemy(app, model_class=BaseModel)


######################################################################################################

class Parent(db.Model):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))


class Child(db.Model):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))

    parent_id = Column(Integer, ForeignKey('parent.id'))
    parent = relationship("Parent", backref='child')  # Parent大写类名或者类名的字符串. child小写表名


if __name__ == '__main__':
    db.create_all()
    Parent.create(name='ZhangTian')
    Parent.create(name='LiTian')
    Child.create(name='ZhangDi', parent_id=1)
    Child.create(name='LiDi', parent_id=2)

    parent = db.session.query(Parent).first()
    db.session.delete(parent)
    db.session.commit()

    ###################################################################
    # parent = db.session.query(Child).first().parent
    # print(parent.name)
    # for child in parent.child:
    #     print(child.name)

    ###################################################################
    # children = db.session.query(Parent).first().child
    #
    # for child in children:
    #     print(child.name)

    # 当使用 uselist=False, 将从多对一或者一对多，变为1对于1
    # 其实就是 children = db.session.query(Parent).first().child, 不在取出的是list,而是list[0]
    # parent = relationship("Parent", backref=backref("child", uselist=False))

import json

from sqlalchemy import Column, Integer, String
# https://segmentfault.com/a/1190000004288061
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, VARCHAR

# ***************************
engine = create_engine('sqlite:///./cnblogblog.db', echo=False)
Base = declarative_base()
DBSession = sessionmaker(bind=engine)


class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


#
# class MutableDict(Mutable, dict):
#     @classmethod
#     def coerce(cls, key, value):
#         "Convert plain dictionaries to MutableDict."
#
#         if not isinstance(value, MutableDict):
#             if isinstance(value, dict):
#                 return MutableDict(value)
#
#             # this call will raise ValueError
#             return Mutable.coerce(key, value)
#         else:
#             return value
#
#     def __setitem__(self, key, value):
#         "Detect dictionary set events and emit change events."
#
#         dict.__setitem__(self, key, value)
#         self.changed()
#
#     def __delitem__(self, key):
#         "Detect dictionary del events and emit change events."
#
#         dict.__delitem__(self, key)
#         self.changed()


class MyDataClass2(Base):
    __tablename__ = 'my_data2'
    id = Column(Integer, primary_key=True)
    data = Column(JSONEncodedDict)
    name = Column(String(50))


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = DBSession()

    m1 = MyDataClass2(data={'value1': 'foo1'}, name='xiaohong')
    session.add(m1)
    session.commit()

    m1.name = 'xiaolang'
    #######session 提交后，name 关联到了query
    # assert m1 in session.dirty

    #######session 提交后， data将不再关联到query(解决方法，按着JsonEncodeDict-demo-1.py来）

    m1.data['value1'] = 'bar'
    session.commit()
    # assert m1 in session.dirty

    # my_data= session.query(MyDataClass).filter_by(id=1).one()
    # a= my_data.data
    # print (type(a))
    # print (a)
    # print (a["value1"])
    #
    # my_data.data["value1"] = "foo2"
    #
    # session.commit()

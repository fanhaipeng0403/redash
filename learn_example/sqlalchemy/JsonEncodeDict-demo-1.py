import json

# https://segmentfault.com/a/1190000004288061
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import Mutable
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


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()


class MyDataClass1(Base):
    __tablename__ = 'my_data1'
    id = Column(Integer, primary_key=True)
    data = Column(MutableDict.as_mutable(JSONEncodedDict))
    name = Column(String(50))




if __name__ == '__main__':

    def row_to_dict(row):
        result = {}
        for column in row.__table__.columns:
            result[column.name] = getattr(row, column.name)

        return result


    Base.metadata.create_all(engine)
    session = DBSession()

    m1 = MyDataClass1(data={'value1': 'foo1'}, name='xiaohong')
    session.add(m1)
    session.commit()

    #######session 提交后， data 可以关联到query

    m1.name = 'xiaolang'

    m1.data['value1'] = 'bar'#数据库的值，将被改变

    # assert m1 in session.dirty
    session.commit()

    my_data= session.query(MyDataClass1).filter_by(id=1).one()

    print (row_to_dict(my_data))


    # a= my_data.data
    # print (type(a))
    # print (a)
    # print (a["value1"])
    #
    # my_data.data["value1"] = "foo2"
    #
    # session.commit()



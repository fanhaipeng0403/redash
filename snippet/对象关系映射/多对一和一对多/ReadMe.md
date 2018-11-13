https://www.xncoding.com/2016/03/07/python/sqlalchemy02.html

# 对于一对多和多对一采用这种设计方法

# 推荐这种设计    D:\redash-master\learn_example\sqlalchemy\多对一和一对多\一对多\2.py
记录少的parent_id（即一对多和多对一中的一），并且放置到多的表里，（child)

class Parent(db.Model):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))


class Child(db.Model):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    parent_id = Column(Integer, ForeignKey('parent.id'))
    parent = relationship("Parent", backref='child')  


if __name__ == '__main__':
    db.create_all()
    Parent.create(name='ZhangTian')
    Parent.create(name='LiTian')
    Child.create(name='ZhangDi', parent_id=1)
    Child.create(name='LiDi', parent_id=2)
    
    parent = db.session.query(Child).first().parent
    print(parent.name)
    for child in parent.child:
        print(child.name)
    children = db.session.query(Parent).first().child
    for child in children:
        print(child.name)
        
        
1.确定关系类型,比如孩子和父母，是一父母多个孩子，多个孩子一个父母
2.选择外键，最好是少的那个 parent_id
3.放置到多的那个表里,这个是child， parent_id = Column(Integer, ForeignKey('parent.id'))
4.紧跟着 parent = relationship("Parent", backref='child')  



# D:\redash-master\learn_example\sqlalchemy\多对一和一对多\一对多\1.py
也可以。。

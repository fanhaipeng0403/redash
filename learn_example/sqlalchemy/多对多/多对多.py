# (backref ="parent")
"""
https://docs.sqlalchemy.org/en/latest/orm/relationships.html

主要学习RelationShip

"""
# https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html
from learn_example.sqlalchemy.sqlalcheny_example import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy import Table, Text
from sqlalchemy.orm import relationship

post_keywords = Table('post_keywords', Base.metadata,
                      Column('post_id', Integer, ForeignKey('posts.id')),
                      Column('keyword_id', Integer, ForeignKey('keywords.id'))
                      )


class BlogPost(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    body = Column(Text)
    keywords = relationship('Keyword', secondary=post_keywords, backref='posts')


class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True)
    keyword = Column(String(50), nullable=False, unique=True)




# 2个外键
# 外键定义于中间表
# keywords = relationship('Keyword', secondary=post_keywords, backref='posts')
# 通过sencodary指明中间表




    last_modified_by = db.relationship(User, backref="modified_queries", foreign_keys=[last_modified_by_id])
    visualizations = db.relationship("Visualization", cascade="all, delete-orphan")
    grantor = db.relationship(User, backref='grantor', foreign_keys=[grantor_id])


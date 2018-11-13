# 一对多
物理层次保存一的id
# 对应关系
一个父母多个孩子
# 物理设计
parent_id 放置于child表里

# 1.py 

` children = relationship("Child", backref ="parent") `
relationship放置于Parent类里, Child大写类名或其字符串, 且back_ref反向引用parent(小写表名)

# 2.py 



` parent = relationship("Parent", backref='child') `
relationship放置于Child类里, Parent大写 且back_ref反向引用child(小写表名)

# 3.py 

` children = relationship("Child", back_populates="parent") `
` parent = relationship("Parent", back_populates='children') `
relationship放置于于两侧，使用back_populates






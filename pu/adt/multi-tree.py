# -*- coding: utf-8 -*-
'''多叉树: 
eg. 可以存储层级结构 
[{'id':1,'title':'xx','parent_id':0},
{'id':2,'title':'yy','parent_id':0},
{'id':3,'title':'zz','parent_id':2},
{'id':4,'title':'mm','parent_id':2},
{'id':5,'title':'nn','parent_id':1},]
'''

class Node:
    
    max_children = 100
    
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.children = []
        
    def __str__(self):
        return '%s: %s' % (self.name, self.data)
    
    def __repr__(self):
        return '%s: %s' % (self.name, self.data)
 
    def add_child(self, node):
        self.children.append(node)
 
    def go(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None


class Tree:
 
    def __init__(self):
        self._head = Node('header', None)
 
    def link_to_head(self, node):
        self._head.add_child(node)
 
    def insert(self, path, node):
        '''按照路径插入节点
        @param path: 节点name组成的序列eg. ['A', 'B']
        '''
        cur = self._head
        for step in path:
            if cur.go(step) == None:
                return False
            else:
                cur = cur.go(step)
        cur.add_child(node)
        return True
 
    def search(self, path):
        '''
        @param path: 节点name组成的序列eg. ['A', 'B']
        '''
        cur = self._head
        for step in path:
            if cur.go(step) == None:
                return None
            else:
                cur = cur.go(step)
        return cur


if __name__ == '__main__':
    a = Node('A', 'aa')
    b = Node('B', 'bb')
    c = Node('C', 'cc')
    d = Node('D', 'dd')
    e = Node('E', 'ee')
    # f = Node('F', 'ff')
    g = Node('G', 'gg')
    h = Node('H', 'hh')
    
    a.add_child(b)
    a.add_child(g)
    
    b.add_child(c)
    b.add_child(e)
    
    c.add_child(d)
    
    tree = Tree()
    tree.link_to_head(a)
    tree.insert(['A', 'B'], h)
    
    print tree.search(['A', 'B']).name
    print tree.search(['A', 'B']).data
    print tree.search(['A', 'B']).children
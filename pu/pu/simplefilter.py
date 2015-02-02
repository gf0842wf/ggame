# -*- coding: utf-8 -*-
import binascii
import fnmatch
import re


class Filter:
    def __init__(self, string=None):
        if string:
            self.parse(string)

    def __repr__(self):
        return '{name}{op}{pattern}'.format(**self.__dict__)

    def parse(self, string):
        name, op, pattern = re.split('([#!~=]*)', string, 1)

        self.name = name.strip()
        self.op = op.strip()
        self.pattern = pattern.strip()

    def __call__(self, ob):
        '''过滤对象
        检查顺序:
        - 优先检查对象属性: getattr(ob, name)
        - 其次用 [] 检查: ob[name] 
        '''
        name = self.name
        op = self.op
        pattern = self.pattern

        if hasattr(ob, name):
            value = getattr(ob, name)
        else:
            try:
                value = ob[name]
            except KeyError:
                if '!' in op:
                    return True
                return False

        if isinstance(value, int):
            value = str(value)

        if op.startswith('#'):
            if isinstance(value, str):
                value = value.encode('latin1', 'replace')
            op = op[1:]
            value = binascii.hexlify(value)
            pattern = pattern.lower()

        if isinstance(value, bytes):
            value = value.decode('latin1', 'replace')

        if op == '=':
            return value == pattern
        elif op == '!=':
            return value != pattern
        elif op == '~=':
            return fnmatch.fnmatchcase(value, pattern)
        elif op == '!~=':
            return not fnmatch.fnmatchcase(value, pattern)
        else:
            assert False


class FilterGroup(list):
    def __init__(self, string=None):
        if string:
            self.parse(string)


class AndFilterGroup(FilterGroup):
    def parse(self, string):
        self.extend(map(Filter, string.split('&&')))

    def __repr__(self):
        return ' && '.join(map(str, self))

    def __call__(self, ob):
        for f in self:
            if not f(ob):
                return False

        return True


class OrFilterGroup(FilterGroup):
    def parse(self, string):
        self.extend(map(AndFilterGroup, string.split('||')))

    def __repr__(self):
        return ' || '.join(map(str, self))

    def __call__(self, ob):
        if not self:
            return True

        for f in self:
            if f(ob):
                return True

        return False


if __name__ == '__main__':
    f = OrFilterGroup('a=a && b=b || a=A && b=B')
    print(f)
    assert f(dict(a='a', b='b')) == True
    assert f(dict(a='A', b='B')) == True
    assert f(dict(a='a', b='B')) == False
    assert f(dict(a=1, b=2)) == False

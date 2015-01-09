# -*- coding: utf-8 -*-
'''字典树实现敏感词过滤'''

import codecs


class TrieNode(object):
    
    def __init__(self, value=None):
        self._end = False
        self._child = dict()
        self._value = value

    def add(self, ch):
        if not self._child.has_key(ch):
            node = TrieNode(ch)
            self._child[ch] = node
            return node
        else:
            return self._child.get(ch)

    def is_end(self):
        return self._end

    def set_end(self, end):
        self._end = end

    def get_child(self, ch):
        if self._child.has_key(ch):
            return self._child.get(ch)
        else:
            return None

    def get_value(self):
        return self._value


class TrieCheck(object):
    
    def __init__(self):
        self._root = TrieNode('')

    def add_word(self, text):
        node = self._root
        for i in text:
            node = node.add(i)
        node.set_end(True)

    def get_bad_word(self, text, offset=0):
        if not isinstance(text, str) or offset >= len(text):
            raise Exception('%s is not a string' % str(str))
        i = offset
        text = unicode(text[offset:], 'utf-8')
        for ch in text[offset:]:
            node = self._root
            index = i
            node = node.get_child(ch)
            path = []
            while node is not None:
                if node.is_end():
                    path.append(text[i:index+1])
                    yield (i, ''.join(path))
                if len(text) == index + 1:
                    break
                index += 1
                node = node.get_child(text[index])
            i += 1

    def replace_bad_word(self, text, offset=0, mark='*'):
        if not isinstance(text, str) or offset >= len(text):
            raise Exception('%s is not a string' % str(str))
        i = offset
        text = unicode(text[offset:], 'utf-8')
        li = list(text)
        for ch in text[offset:]:
            node = self._root
            index = i
            node = node.get_child(ch)
            while node is not None:
                if node.is_end():
                    for m in xrange(i, index + 1):
                        li[m] = mark
                    break
                if len(text) == index + 1:
                    break
                index += 1
                node = node.get_child(text[index])
            i += 1
        return ''.join(li)


def load(path, checker):
    with codecs.open(path, 'r', encoding='utf-8-sig') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith(u'#'):
                continue
            checker.add_word(line)


def main():
    check = TrieCheck()
    load('sensitive.txt', check)
    print list(check.get_bad_word('反对一切血腥和色情游戏。'))
    print check.replace_bad_word('反对一切血腥和色情游戏。')

if __name__ == '__main__':
    main()

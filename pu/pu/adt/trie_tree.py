# -*- coding: utf-8 -*-
'''字典树实现敏感词过滤'''

import codecs


class Check(object):
    
    def __init__(self):
        pass

    def add_word(self, text):
        pass

    def get_bad_word(self, text, offset=0):
        pass

    def replace_bad_word(self, text, offset=0, mark='*'):
        pass


class TrieNode(Check):
    
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
                path.append(text[index])
                if node.is_end():
                    return i, ''.join(path)
                if len(text) == index + 1:
                    break
                index += 1
                node = node.get_child(text[index])
            i += 1
        return -1, None

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
                    print 'sensitive word:', ''.join(li[i:index + 1])
                    for m in range(i, index + 1):
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
    print check.replace_bad_word('反对一切博彩和色情游戏。')

if __name__ == '__main__':
    main()

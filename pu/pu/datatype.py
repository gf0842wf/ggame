# -*- coding: utf-8 -*-
import binascii


class pretty_bytes(bytes):
    r'''提供自定义格式
    >>> pb = pretty_bytes(b'\xaa\xbb\xcc\xdd\xee\xff')
    >>> '{0:hex}'.format(pb)
    'aabbccddeeff'
    >>> '{0:HEX}'.format(pb)
    'AABBCCDDEEFF'
    >>> '{0:hex+}'.format(pb)
    'aa bb cc dd ee ff'
    >>> '{0:HEX+}'.format(pb)
    'AA BB CC DD EE FF'
    >>> '{0}'.format(pb)
    '\xaa\xbb\xcc\xdd\xee\xff'
    '''
    def __format__(self, format_spec):
        if format_spec == 'hex':
            return binascii.hexlify(self).decode()
        elif format_spec == 'HEX':
            return ''.join('%02X' % ord(b) for b in self)
        elif format_spec == 'hex+':
            return ' '.join('%02x' % ord(b) for b in self)
        elif format_spec == 'HEX+':
            return ' '.join('%02X' % ord(b) for b in self)
        else:
            return str(self)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

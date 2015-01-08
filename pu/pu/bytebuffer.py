# -*- coding: utf-8 -*-
import io


class ByteBuffer:
    rptr = 0
    wptr = 0
    max_size = 1024 * 1024

    def __init__(self):
        self._buffer = io.BytesIO()

    def write(self, data):
        self._buffer.seek(0, 2)
        self._buffer.write(data)
        self.wptr += len(data)
        if self.wptr > self.max_size:
            self.compress()

    def read(self, size=-1):
        self._buffer.seek(self.rptr)
        data = self._buffer.read(size)
        self.rptr += len(data)
        if self.empty():
            self.clear()
        return data

    def peek(self, size=-1):
        self._buffer.seek(self.rptr)
        data = self._buffer.read(size)
        return data

    def readline(self):
        self._buffer.seek(self.rptr)
        line = self._buffer.readline()
        self.rptr += len(line)
        return line

    def length(self):
        return self.wptr - self.rptr

    def empty(self):
        return self.wptr == self.rptr

    def compress(self):
        data = self.read()
        dlen = len(data)
        if dlen:
            self._buffer.seek(0)
            self._buffer.write(data)
            self._buffer.truncate()
        self.wptr = dlen
        self.rptr = 0

    def clear(self):
        self._buffer.seek(0)
        self._buffer.truncate()
        self.wptr = 0
        self.rptr = 0

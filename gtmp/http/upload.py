# -*- coding: utf-8 -*-
'''
只使用标准库,模拟表单post上传文件
'''
import urllib2
import mimetools
import os

def request_add_file(url, filename):
    request = urllib2.Request(url)
    data = open(filename, 'rb').read()
    basename = os.path.basename(filename)
    boundry = mimetools.choose_boundary() # "------------"
    
    body = '''\
--%s
Content-Disposition: file; name="name"; filename="%s"
Content-Type: text/plain

--%s
%s''' % (boundry, basename, data, boundry)
    
    print repr(body)
    
    request.add_header('Content-type', 'multipart/form-data; boundary=%s' % boundry)
    request.add_header('Content-length', len(body))
    request.add_data(body)
    
    return request


if __name__ == '__main__':
    url = 'http://127.0.0.1:6001/api/game/upload/image'
    request = request_add_file(url, 'requirements.txt')
    response = urllib2.urlopen(request)
    print response.read()

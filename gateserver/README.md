# 网关服务器

通用信息
--
- `=>`服务器发往客户端, `<=`客户端发往服务器
- resp一般都有 code 字段

	code

		0-成功

		1-握手失败
		2-认证失败

功能
--
- 连接 负责保持连接所有客户端
- 握手
- 均衡连接负载

协议
--
头部: 固定4bytes. 消息体采用json,加密和压缩只针对消息体部分,不包括头部

- 握手

		=>
		{"type":"SHAKE", "key":uint32}
		后续消息客户端需要根据key来加密
		<=
		{"type":"SHAKE"} # 服务器根据这个消息来判断是否握手成功,成功不回应,失败发送{"type":"SHAKE", "code":1}后关闭连接

- 登录

		<=
		{"type":"LOGIN", "username":"", "password":""}
		=>
		成功
		{"type":"LOGIN", "userid":uint32, "code":0}
		失败 (发送后关闭连接)
		{"type":"LOGIN", "code":2}

- 心跳

		<=
		{"type":"NOP"}
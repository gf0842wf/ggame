# HTTP服务器


通用信息
--
- 请求响应头: `Content-Type`: `application/json`, 如果是上传文件采用 `multipart/form-data`. 传输采用http(s)
- url prefix: `http(s)://ip:port/api/v1/game`
- 接口返回值都有 code 字段,如果code不等于0,还会有 msg 字段,内容时错误信息

	code

		0-成功
		1-认证错误(用户名密码错误/认证过期)
		2-该用户已注册
		
		99-未知错误
		
		400-无效请求
		404-找不到
		500-内部错误

登录服务器
==

功能
--
- 分配网关服务器
- 用户排队

认证
--

	认证具体是采用 cookie还是采用 http basic auth 待定

协议
--
- 获取服务器

		METHOD: POST
		URL: /check
	
		REQ:
		{
			"game_name":"", # 游戏名
			"region":"", # 分服
			#"username":"",
			#"password":"",
		}
	
		RESP:
	    {
	        "code":0,
	        "gate_servers":[["127.0.0.1", 6011], ["127.0.0.1", 6012]], # 按照可连接性逆序排序
			"chat_servers":[["127.0.0.1", 6021], ["127.0.0.1", 6022]], # 按照可连接性逆序排序
			"stand_code":"" # 排队获得的排队码,根据这个码来登陆网关
			
			"code":1, # 排队
			"delay":uint32, # 排队时间, 客户端轮询调用  /game/check 接口,来获取delay,当delay>10时,轮询时间间隔为10s;当delay<10时轮询时间间隔为5s.服务端根据是否轮询来判断用户是否放弃排队
	    }

API服务器
==

功能
--
- 提供短连接和websocket接口

认证
--

	认证采用 secure cookie

- 发送注册短信验证码
		

		METHOD: POST
		URL: /sms-auth

		REQ:
		{
			"username":"", # 手机号
			"isp":0, # 运营商 0-联通, 1-电信, 2-移动, 9-未知
			"platform":0, # 0-ios, 1-android, 2-web, 9-未知
		}
		
		RESP:
		{
			"code":0, 
		}

- 注册

		METHOD: POST
		URL: /register
		REQ:
		{
			"username":"", # 手机号
			"password":"", 
			"auth_code":"",
			"nickname":""
		}

		RESP:
		{	
			"code": 0,
			"uid":""
		}

- 登陆  

		METHOD: POST
		URL: /login

		REQ:
		{
			"username":"", # 手机号
			"password":"", # 密码的md5值, 全部小写
		}
		
		RESP:
		{
			"code":0, 
			"uid":"",
			# TODO: 其它用户信息待定
		}

- 注销  

		METHOD: POST
		URL: /logout

		RESP:
		{
			"code":0
		}


静态文件
--
- 上传文件

		上传语音日志等

		METHOD: POST
		URL: /upload/file
		type => file # 必须指定为"file"
		name => name # 必须指定为"name"
		Headers:
		{
			"x-id":"", # 文件标识
			"x-sn":"", # 文件序号
			"x-mk":"", # 备注
			"x-ext":"", # 扩展名,eg. "txt", "war"
		}
		RESP:
		{	
			"code": 0,
			"md5":"",
			"url": "", # 文件下载url
		}

- 上传图片

		上传图片

		METHOD: POST
		URL: /upload/image
		type => file # 必须制定为"file"
		name => name # 必须制定为"name"
		Headers:
		{
			"x-id":"", # 文件标识
			"x-sn":"", # 文件序号
			"x-mk":"", # 备注
			"x-ext":"", # 扩展名,eg. "png", "jpg"
			"x-thumbWidth":"", # 缩略图宽 eg. "200"
			"x-thumbHeight":"" # 缩略图高 eg. "200"
		}
		RESP:
		{	
			"code": 0,
			"md5":"", # 原图md5, 不返回缩略图md5
			"image": "", # 原图url
			"thumb":"", # 缩略图url
		}

- 下载文件

		通过上传接口获取的url来下载文件


试衣间
--

- 获取试衣间

		METHOD: GET
		URL: /fitting

		REQ:
		{
		}
		
		RESP:
		{
			"code":0, 
            "wearing": # 穿着的
            [ 
                {
                    "id":0,
                    "type":"top" # 上衣
                },
                {
                    "id":1,
                    "type":"skirt" # 裙子
                },
                {
                    "id":2,
                    "type":"pants" # 裤子
                },
                {
                    "id":3,
                    "type":"bag" # 包包
                },
                {
                    "id":4,
                    "type":"hair" # 发型
                },
                {
                    "id":5,
                    "type":"shoes" # 鞋子
                },
                {
                    "id":6,
                    "type":"eardrop" # 耳饰
                },
                {
                    "id":7,
                    "type":"nechlace" # 颈饰
                },
                {
                    "id":8,
                    "type":"bracelet" # 手饰
                },
                {
                    "id":9,
                    "type":"leglet" # 腿饰
                },
                {
                    "id":10,
                    "type":"topknot" # 头饰
                },
                {
                    "id":11,
                    "type":"makeup" # 化妆
                }
            ],
            "backpack": # 背包(里面不包含身上穿着的)
            [

            ]
		}

- 换装

		METHOD: POST
		URL: /cosplay

		REQ:
		{
			"src_id":uint32, 
			"dst_id":uint32
		}
		
		RESP:
		{
			"code":0
		}


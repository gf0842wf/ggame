# HTTP服务器

说明
--
恰巧在自己的框架里面TODO这个功能, 所以新建一个分支`taihe-test`, 单独实现了排队服务器功能. 登陆注销采用普通http接口, 排队采用websocket接口.


通用信息
--
- 请求响应头: `Content-Type`: `application/json`, 如果是上传文件采用 `multipart/form-data`. websocket数据体也采用json
- url prefix: `http://ip:port/api/v1/game`
- 接口返回值都有 code 字段,如果code不等于0,还会有 msg 字段,内容时错误信息
- 符号说明: `@authorize` - 必须登陆的接口

	code

		0-成功
		1-认证错误(用户名密码错误/认证过期)
		2-该用户已注册
        3-服务期满,需要排队
		
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

	认证采用 secure cookie

协议
--

- 登陆  

		METHOD: POST
		URL: /login

		REQ:
		{
			"username":"",
			"password":"",
		}
		
		RESP:
		{
			"code":0,
			"uid":"",
		}

- 注销  

		METHOD: POST
		URL: /logout

		RESP:
		{
			"code":0
		}

- 获取服务器/排队(websocket) `@authorize`

		METHOD: WS
		URL: /ws/check
	
		REQ:
		{
			"game_name":"", # 游戏名
			"region":"", # 分服
		}
	
		RESP:
	    {
	        "code":0,
	        "gate_servers":[{"host":"", "port":uint32}], # 按照可连接性逆序排序
			"chat_servers":[{"host":"", "port":uint32}], # 按照可连接性逆序排序
			-------------上面是成功情况,下面是服务器满情况-------------
			"code":3, # 排队
            "front_users":uint32, # 队列前面的人数
	    }




测试
==

- 依赖安装(需要安装启动mongodb)
    
        # 下载项目
        git clone https://github.com/gf0842wf/ggame.git

        # 进入ggame目录,切换到 taihe-test 分支
        git checkout taihe-test
        
        # 进入ggame/webserver,安装依赖包
        pip install cython
        pip install -r requirements-taihe-test.txt

        # 配置webserver监听端口、游戏允许最大人数(为了测试方便,默认是2)、mongodb数据库等
        默认使用配置见 ggame/webserver/etc/web/taihe_test.json

        # 自定义包安装

        # 进入ggame/pu目录, 安装pu
        python setup.py install
        
        # 进入ggame/gnet目录, 安装gnet
        python setup.py install

        # 导入测试用户(进入dbdump.py可以看到测试账户)

        # 进入ggame/webserver目录
        python dbdump.py

    
- 服务器端

        # 进入ggame目录:
        python webserver --settings etc/web/taihe_test.json


- 客户端
        
    
        用浏览器打开 http://127.0.0.1:6001

        1.使用 dbdump.py 里面的账户登录
        2.排队中的用户可以关闭浏览器来表示退出排队
        3.进入游戏的用户可以在浏览器打开 http://127.0.0.1:6001/api/v1/game/offline/<uid> 来让某个uid下线 (uid在登陆成功后有返回)
        4.可以在一台机子上用多个浏览器来进行测试(默认部署的是127.0.0.1, 如果想多台机子测试需要把 ggame/webserver/tpl/index.tpl文件的ws的ip改为服务器ip, 测试时也要把127.0.0.1改为相应的服务器ip)

        
优化/说明
==

1. 核心部分(gnet)采用的是gevent框架, io性能较高, web框架选用的是bottle, 结构简单, 和gevent配合性能较高
2. 排队部分这里采用websocket长连接, 可用nginx代理扩展性能
3. 用户在线列表和排队列表应该是全局的(可用redis队列)
4. 对于并发量,在普通阿里云机器上面测试单进程有4000qps,并发可以可以使用nginx扩展
5. 依赖包安装较为复杂,暂时未写成一键安装形式

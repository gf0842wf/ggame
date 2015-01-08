# ggame数据库设计文档 #

> **采用MongoDB数据库**

- user

        {
            "_id": OID,

            "username":"",
            "password":"",
            "nickname":"",

            "platform":9,
            "isp":9,

            "login_date":"",
            "create_date":"",

            "backpack": # 物品(包括身上穿的)
            [ 
                {
                    "wearing":1,
                    "id":1,
                    "type":11 # 上衣
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":8 # 裙子
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":7 # 裤子
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":12 # 包包
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":6 # 发型
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":10 # 鞋子
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":1 # 耳饰
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":2 # 颈饰
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":3 # 手饰
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":9 # 腿饰
                },
                {
                    "wearing":1,
                    "id":1,
                    "type":4 # 头饰
                },
                {
                "wearing":1,
                    "id":1,
                    "type":5 # 化妆
                }
            ]
        }
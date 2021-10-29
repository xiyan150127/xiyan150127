# -*- coding: utf-8 -*-
"""
Created on Wed May 26 21:06:39 2021

@author: DELL
"""
#需要安装pycrypto: pip install pycryptodome
#网易云音乐加密过程
"""  
    function a(a=16) {#随机的16位字符串
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)#循环16次
            e = Math.random() * b.length,#随机数
            e = Math.floor(e),#取整
            c += b.charAt(e);#取字符串中的xxx位置
        return c
    }
    function b(a, b) {#a是要加密的内容
        var c = CryptoJS.enc.Utf8.parse(b)#b是密钥
          , d = CryptoJS.enc.Utf8.parse("0102030405060708")
          , e = CryptoJS.enc.Utf8.parse(a)#e是数据
          , f = CryptoJS.AES.encrypt(e, c, { #c 加密的密钥
            iv: d,#偏移量
            mode: CryptoJS.mode.CBC #模式=CBC
        });
        return f.toString()
    }
    function c(a, b, c) {
        var d, e;
        return setMaxDigits(131),
        d = new RSAKeyPair(b,"",c),
        e = encryptedString(d, a)
    }
    function d(d, e, f, g) { d:数据     e：010001    f:很长     g:"0CoJUm6Qyw8W8jud"
        var h = {} #空对象
          , i = a(16);#i就是一个16位的随机值，把i设置成定值
        h.encText = b(d, g)#g是密钥
        h.encText = b(h.encText, i)#返回的就是params i也是密钥
        h.encSecKey = c(i, e, f)#得到的就是encSecKey, e和f是固定值 把i固定了，
        return h
    }
    
    两次加密：
    数据+g=>b=>第一次加密+i=>b=params
"""
from Crypto.Cipher import AES
from base64 import b64encode
import requests
import json 
import time

#网易云加密过程传递的为定值的参数e,f,g
e = "010001"
f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
g = "0CoJUm6Qyw8W8jud"#密钥

#AES加密算法
def AES_encrypt(data, key, iv): 
    pad = 16 - len(data) % 16
    data = data + pad * chr(pad)#加密，加密内容的长度必须是16的倍数，就是这样规定的
    data = data.encode("utf-8")
    temp = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    encrypt_data = temp.encrypt(data)
    encrypt_data = b64encode(encrypt_data)
    return encrypt_data.decode('utf-8')

#反加密过程,参考网易云加密过程
def get_params(data1, e, f, g):
    dic = {}#存放两个重要参数的字典
    i="oA7mEkL2pnQk61fT"#每次随机生成的参数，把它固定住
    iv = b"0102030405060708"
    h_encText = AES_encrypt(data1, g, iv)#参考网易云第一次加密
    h_encText = AES_encrypt(h_encText,i, iv)#第二次加密
    dic["encText"] = h_encText
    dic["encSecKey"] = "840d2ab19d30b7187e924caf063565be6ccc2dd354a461c520fe0c6a9e15fdb774d81e1e83d6b15b137d719cb840d95856aa9b637bda4a7749651563de5caa7388ffb78ff23b680bad49b298b5818435b6c738dc45c238a8b9c98cdca168bf2fc8147d4fa0c01fe2a489da8b947733bb2c5829db2570aca8a0847bb3ebcca7d2"
    return dic#每次动态加载时返回这两个参数

#参数注释：
"""csrf_token 空字符串
cursor 当前时间错(毫秒)
offset json需要的参数，位移量，是动态加载评论的变化参数，变化规律为页码*20
orderType 1 评论排序方式的参数 1：按最新评论展示 2：按热度排序 3：按推荐排序
pageNo 页码
pageSize 每页返回多少条评论，默认设定为20
rid 固定"R_SO_4_" + 歌曲id(就是网页最上方https那一行末尾的数字串)
threadId 固定"R_SO_4_" + 歌曲id  """


#爬虫开始！！！
print('开始爬虫')
 
#n = int(input('Please input the page_number that you want scratch:'))

try:
    for i in range(50):
         
        data1 = json.dumps({"csrf_token": "", "cursor": "-1", "offset": str(i*20), "orderType": "3", "pageNo": str(i+1),
                             "pageSize": "20", "rid": "R_SO_4_1890044606", "threadId": "R_SO_4_1890044606"})
    
        result = get_params(data1, e, f, g)
    
        url='https://music.163.com/weapi/comment/resource/comments/get?csrf_token='
    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        }
    
        param_data = {"params": result["encText"],
                      "encSecKey": result["encSecKey"]}
    
        response = requests.post(url,data=param_data, headers=headers)
        #转换格式并抽取指定列写入csv文件中
        items = json.loads(response.text)['data']['comments']
    
        for item in items:  
    
        #用户昵称
            user_name = item['user']['nickname'].replace(',', '，')
        # 用户ID
            user_id = str(item['user']['userId'])
     
        # 评论内容
            comment = item['content'].strip().replace('\n', '').replace(',', '，')
        # 评论ID
            comment_id = str(item['commentId'])
        # 评论点赞数
            praise = str(item['likedCount'])
        # 评论时间
            date = time.localtime(int(str(item['time'])[:10]))
            date = time.strftime("%Y-%m-%d %H:%M:%S", date) 
            print(user_name, user_id,comment,comment_id, praise,date) 
            with open('D:\\冬梦飞扬.csv', 'a', encoding='utf-8-sig') as fp:
         
                fp.write(user_name + ',' + user_id + ',' + comment + ',' + comment_id + ',' + praise + ',' + date + '\n')
                fp.close()
except Exception :
    
        print('\n'+'This is not an Error.')  
        
finally:
    
        print('\n'+'爬取完毕')
     
 
         
           
           
   
"""
for i in range(11):
     
    data1 = json.dumps({"csrf_token": "", "cursor": "-1", "offset": str(i*20), "orderType": "1", "pageNo": str(i+1),
                         "pageSize": "20", "rid": "R_SO_4_1398764652", "threadId": "R_SO_4_1398764652"})

    result = get_params(data1, e, f, g)

    url='https://music.163.com/weapi/comment/resource/comments/get?csrf_token='

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    param_data = {"params": result["encText"],
                  "encSecKey": result["encSecKey"]}

    response = requests.post(url,data=param_data, headers=headers)
    items = json.loads(response.text)['data']['comments']

    for item in items:

    #用户昵称
        user_name = item['user']['nickname'].replace(',', '，')
    # 用户ID
        user_id = str(item['user']['userId'])
 
    # 评论内容
        comment = item['content'].strip().replace('\n', '').replace(',', '，')
    # 评论ID
        comment_id = str(item['commentId'])
    # 评论点赞数
        praise = str(item['likedCount'])
    # 评论时间
        date = time.localtime(int(str(item['time'])[:10]))
        date = time.strftime("%Y-%m-%d %H:%M:%S", date) 
        print(user_name, user_id,comment,comment_id, praise,date) 

        with open('D:\\mysongcomment4.xlsx', 'a', encoding='utf-8-sig') as fp:
     
             fp.write(user_name + ',' + user_id + ',' + comment + ',' + comment_id + ',' + praise + ',' + date + '\n')
             fp.close()
         
#print('爬取完毕')       
"""
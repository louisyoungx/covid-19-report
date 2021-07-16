import time
import datetime
import http
import json
import os
import random
import re
import ssl
import urllib
from http import cookiejar
from urllib import parse, request
import requests


# 签到模式 0表示单人签到 1表示多人签到
signs = 0

# 单人签到学号，部分学校可能用一卡通号等代替。可以到 https://fxgl.jx.edu.cn/你的高校代码/  自己尝试一下
# 仅当选择单人签到，即上面signs = 0时才需要配置，否则可以忽略
yourID = 70567
# 多人签到学号组，部分学校可能用一卡通号等代替。可以到  https://fxgl.jx.edu.cn/你的高校代码/   自己尝试一下
# 仅当选择多人签到，即上面signs = 1时才需要配置，否则可以忽略，使用英语逗号 , 将每个学号分开哦，需要是同一个学校，两侧的引号别丢了
IDs = '学号1,学号2,学号3,学号4'

# 高校代码，详见GitHub项目介绍
# 多人签到暂不支持多个学校签到（你想干嘛？）
schoolID = 4136010406

# 身份类型 0表示学生 1表示教职工
identity = 1

# 是否为毕业班的学生 0表示是毕业班的学生 1表示不是毕业班的学生。
sfby = 1

# 暂不支持健康状况为异常和被隔离的健康上报，请手动提交，确保自己提交的信息真实有效。

# 签到模式
# 0表示获取前一日的签到定位（长时间签到可能会偏差较大，适合多人签到且时间跨度不长，每次签到会在上一次签到的基础上随机偏移1.1m以内，理论上连续签到一年会偏移200m左右
# 1表示使用输入的经纬度（单人签到推荐，会在你输入的经纬度定位上随机偏移11.1m以内
signType = 0

class GetInfo(object):
    def __init__(self, signID):
        self.ID = signID
        self.schoolID = schoolID
        self.identity = identity
        self.sfby = sfby
        self.signType = signType
        self.cookie = http.cookiejar.MozillaCookieJar()
        if self.cookie_file_operation() is False:
            print('登陆数据文件丢失或不存在，尝试重新获取登陆数据')
            if self.login() == 'ERROR':
                raise Exception("Some Thing Wrong")
            self.cookie_file_operation()

    def login(self):
        url = 'https://fxgl.jx.edu.cn/' + str(self.schoolID) + '/public/homeQd?loginName=' + str(self.ID) + '&loginType=' + str(
            identity)
        if os.path.isdir('cookie') is False:
            os.mkdir('cookie')
        if os.path.isdir('cookie/' + str(self.ID)) is False:
            os.mkdir('cookie/' + str(self.ID))
        cookie_file = 'cookie/' + str(self.ID) + '/cookie.txt'
        open(cookie_file, 'w+').close()
        cookie = http.cookiejar.MozillaCookieJar(cookie_file)
        cookies = urllib.request.HTTPCookieProcessor(cookie)  # 创建一个处理cookie的handler
        opener = urllib.request.build_opener(cookies)  # 创建一个opener
        request = urllib.request.Request(url=url)
        res = opener.open(request)
        cookie.save(ignore_discard=True, ignore_expires=True)


    def construction_post(self, lng1, lat1, address):
        global lng, lat, zddlwz, signPostInfo
        if self.signType == 0:
            # 随机偏移1m
            print('定位 ' + str(lng1) + '，' + str(lat1) + '，' + str(address) + '\n')
            lng = round(float(lng1) + random.uniform(-0.000010, +0.000010), 6)
            lat = round(float(lat1) + random.uniform(-0.000010, +0.000010), 6)
            zddlwz = address
        else:
            # 随机偏移11m
            print('定位 ' + str(lng) + '，' + str(lat) + '，' + str(zddlwz) + '\n')
            lng = round(float(lng) + random.uniform(-0.000100, +0.000100), 6)
            lat = round(float(lat) + random.uniform(-0.000100, +0.000100), 6)
            address = zddlwz
        # 通过百度地图api获取所在的省市区等
        url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=80smLnoLWKC9ZZWNLL6i7boKiQeVNEbq&output=json&coordtype' \
              '=wgs84ll&location=' + str(lat) + ',' + str(lng)
        res = requests.get(url)
        print(res.text + '\n')
        # 解析api返回的json数据
        res_dic = json.loads(res.text)
        add_dic = res_dic['result']['addressComponent']
        # 取得省市区
        province = add_dic['province']
        city = add_dic['city']
        district = add_dic['district']
        # 一层层剖析尽量获取到最小的街道
        try:
            regular = '(?<=' + district + ').+?(?=$)'
            street = str(re.search(regular, address).group(0))
        except AttributeError:
            try:
                regular = '(?<=' + city + ').+?(?=$)'
                street = str(re.search(regular, address).group(0))
            except AttributeError:
                try:
                    regular = '(?<=' + province + ').+?(?=$)'
                    street = str(re.search(regular, address).group(0))
                except AttributeError:
                    street = address
        province = parse.quote(province)
        city = parse.quote(city)
        district = parse.quote(district)
        street = parse.quote(street)
        address = parse.quote(address)
        post = 'province=' + province + '&city=' + city + '&district=' + district + '&street=' + street + '&xszt=0&jkzk=0' \
                                                                                                          '&jkzkxq=&sfgl=1&gldd=&mqtw=0&mqtwxq=&zddlwz=' + address + '&sddlwz=&bprovince=' + province + '&bcity=' \
               + city + '&bdistrict=' + district + '&bstreet=' + street + '&sprovince=' + province + '&scity=' + city + \
               '&sdistrict=' + district + '&lng=' + str(lng) + '&lat=' + str(lat) + '&sfby=' + str(sfby)
        print(post + '\n')
        signPostInfo = post
        signPostInfo = signPostInfo.encode('utf-8')

    def sign_history(self, check_exit=False):
        if check_exit is False and signType == 1:
            global lng, lat, zddlwz
            self.construction_post(lng, lat, zddlwz)
        url = 'https://fxgl.jx.edu.cn/' + str(schoolID) + '/studentQd/pageStudentQdInfoByXh'
        cookies = urllib.request.HTTPCookieProcessor(self.cookie)
        opener = urllib.request.build_opener(cookies)
        request = urllib.request.Request(url=url, method='POST')
        res = opener.open(request)
        info_json = res.read().decode()
        try:
            res_dic = json.loads(info_json)
            last_dic = res_dic['data']['list'][0]
            global name
            try:
                name = last_dic['xm']
            except NameError:
                name = ''
            print('NAME' + name + '\n')
            if check_exit:
                return True
            else:
                self.construction_post(last_dic['lng'], last_dic['lat'], last_dic['zddlwz'])
                return False
        except json.decoder.JSONDecodeError:
            if check_exit:
                return False
            else:
                print('无历史签到')

    def cookie_file_operation(self, delete=False):
        cookie_file = 'cookie/' + str(self.ID) + '/cookie.txt'
        if delete:
            os.remove(cookie_file)
            print('删除cookie' + '\n')
            return
        if os.path.isfile(cookie_file):
            print('cookie文件存在' + '\n')
            try:
                self.cookie.load(cookie_file, ignore_discard=True, ignore_expires=True)
                print('cookie文件加载成功' + '\n')
            except http.cookiejar.LoadError:
                print('cookie文件加载失败' + '\n')
                return False
            return True
        else:
            return False

    def verify(self):
        url = 'https://fxgl.jx.edu.cn/' + str(schoolID) + '/public/xslby'
        cookies = urllib.request.HTTPCookieProcessor(self.cookie)
        opener = urllib.request.build_opener(cookies)
        request = urllib.request.Request(url=url, method='POST')
        res = opener.open(request)
        info_html = res.read().decode()
        if '学生签到' not in info_html:
            return False
        if self.sign_history(check_exit=True):
            print(str(name) + str(self.ID) + '检测成功！')
            print('COOKIE OK' + '\n')
        else:
            print(str(self.ID) + '没有查询到历史签到记录，请签到一次后再使用本脚本,或者使用另一种签到模式')
            print('没有签到历史' + '\n')
            self.cookie_file_operation(delete=True)
            return 'ERROR'
        return True

    def is_sign(self, cookie):
        url = 'https://fxgl.jx.edu.cn/' + str(schoolID) + '/studentQd/studentIsQd'
        cookies = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(cookies)
        request = urllib.request.Request(url=url, method='POST')
        res = opener.open(request)
        info_json = res.read().decode()
        res_dic = json.loads(info_json)
        if res_dic['data'] == 1:
            print('今天已经签到啦')
            print('已经签到' + '\n')
            return True
        else:
            print('开始签到')
            print('开始签到' + '\n')
            return False



if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    this = GetInfo(yourID)




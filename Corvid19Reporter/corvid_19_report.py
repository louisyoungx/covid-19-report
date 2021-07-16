import http
import json
import os
import urllib
import time
import requests

from ClassData.DataAPI import ClassExistsList, ClassInitData, ClassInfoData
from Config.settings import config
from Logger.logger import logger
from http import cookiejar
from urllib import request
from openpyxl import load_workbook

# 每日报表 https://fxgl.jx.edu.cn/4136010406/dcwjNew/downloaddnew?dates=2021-07-16&loginName=null
# 每日签到数据 https://fxgl.jx.edu.cn/4136010406/adminQd/downloadQdInfo?date=2021-07-16
# 签到统计表 https://fxgl.jx.edu.cn/4136010406/adminQd/downloadQdl?date=2021-07-16

class Corvid19Report(object):
    def __init__(self, signID):
        self.ID = signID
        self.name = ''
        self.schoolID = config.settings("Corvid_19_Report", "schoolID")
        self.identity = config.settings("Corvid_19_Report", "identity")
        self.sfby = config.settings("Corvid_19_Report", "sfby")
        self.signType = config.settings("Corvid_19_Report", "signType")
        self.path = config.path()
        self.cookie = http.cookiejar.MozillaCookieJar()
        if self.login() == 'ERROR':
            raise Exception("Some Thing Wrong")
        self.cookie_file_operation()
        self.get_excel()
        self.load(mode="DONT")
        self.doNotList()


    def login(self):
        url = 'https://fxgl.jx.edu.cn/' + str(self.schoolID) + '/public/homeQd?loginName=' + str(self.ID) + '&loginType=' + str(self.identity)
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
        logger.info("Account: {} Login Successful".format(self.ID))

    def cookie_file_operation(self, delete=False):
        cookie_file = 'cookie/' + str(self.ID) + '/cookie.txt'
        if delete:
            os.remove(cookie_file)
            logger.info('删除cookie')
            return
        if os.path.isfile(cookie_file):
            try:
                self.cookie.load(cookie_file, ignore_discard=True, ignore_expires=True)
                logger.info('cookie文件加载成功')
            except http.cookiejar.LoadError:
                logger.info('cookie文件加载失败')
                return False
            return True
        else:
            return False

    def getClockInfo(self):
        url = 'https://fxgl.jx.edu.cn/' + str(self.schoolID) + '/studentQd/pageStudentQdInfoByXh'
        cookies = urllib.request.HTTPCookieProcessor(self.cookie)
        opener = urllib.request.build_opener(cookies)
        request = urllib.request.Request(url=url, method='POST')
        res = opener.open(request)
        info_json = res.read().decode()
        try:
            res_dic = json.loads(info_json)
            last_dic = res_dic['data']['list'][0]
            try:
                name = last_dic['xm']
            except NameError:
                name = ''
            self.name = name
            logger.info('已签到：{}-{}'.format(self.ID, name))
        except:
            logger.info('未签到：{}'.format(self.ID))

    def getLoginURL(self):
        url = 'https://fxgl.jx.edu.cn/' + str(self.schoolID) + '/public/homeQd?loginName=' + str(
            self.ID) + '&loginType=' + str(self.identity)
        return url

    def _get_excel(self, folder, url, fileName, fileType):
        os.chdir(folder)  # 切换到将要存放文件的目录
        file = open(fileName + fileType, "wb")  # 打开文件
        try:
            req = urllib.request.Request(url=url)
            req.add_header("User-Agent",
                           "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36")
            res = urllib.request.urlopen(req, timeout=40)
            excel = res.read()  # 将文件转换为bytes格式
            file.write(excel)  # 文件写入
            logger.info(type(file), type(req), type(res), type(excel))
        except Exception as f:
            logger.info(str(f))
        file.close()

    def get_excel(self):
        cookieStr = ""
        for item in self.cookie:
            cookieStr = cookieStr + item.name + '=' + item.value

        path = self.path +'/Excel/'
        date = self.date()
        fileName = date + '.xlsx'
        path += fileName
        url = 'https://fxgl.jx.edu.cn/4136010406/adminQd/downloadQdInfo?date=' + date
        herder = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": cookieStr,
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
        }
        res = requests.get(url, headers=herder)
        excel_file = open(path, "wb")
        excel_file.write(res.content)
        excel_file.close()
        logger.info("Get Excel File Scuccess -> {}".format(fileName))



    def date(self):
        localtime = time.localtime(time.time())
        year = localtime.tm_year.__str__()
        month = localtime.tm_mon.__str__()
        day = localtime.tm_mday.__str__()
        if len(month) < 2:
            month = "0" + month
        if len(day) < 2:
            day = "0" + day
        date = "{}-{}-{}".format(year, month, day)
        return date

    def load(self, mode=""):
        path = self.path + '/Excel/'
        date = self.date()
        fileName = date + '.xlsx'
        path += fileName
        wb = load_workbook(path)
        # 也可以使用wb.get_sheet_by_name("Sheet1") 获取工作表
        ws = []
        if mode == "DO":
            ws = wb["学生签到情况"]
        if mode == "DONT":
            ws = wb["学生未签到情况"]
        # 读取数据，把excel中的一个table按行读取出来，存入一个二维的list
        total_list = []
        for row in ws.rows:
            row_list = []
            for cell in row:
                row_list.append(cell.value)
            total_list.append(row_list)
        # 利用字典进行数据统计
        if mode == "DO":
            self.DO = total_list
        if mode == "DONT":
            self.DONT = total_list
        return total_list

    def doNotList(self):
        totalNum = 0
        self.totalDoNotList = ClassInitData()
        for item in self.DONT:
            classID = item[7]
            ID_Name = str(item[1]) + '-' + str(item[2])
            if classID in ClassExistsList():
                totalNum += 1
                for eachClass in self.totalDoNotList:
                    if eachClass["ClassID"] == classID:
                        eachClass["MemberList"].append(ID_Name)
        return self.totalDoNotList

    def classDoNotList(self, classID):
        DoNotList = []
        for eachClass in self.totalDoNotList:
            if eachClass["ClassID"] == classID:
                DoNotList = eachClass["MemberList"]
                break
        DoNotStr = ""
        for mem in DoNotList:
            DoNotStr = DoNotStr + mem + "\n"
        totalNum = len(ClassInfoData(classID))
        DoNotNum = len(DoNotList)
        DoNum = totalNum - DoNotNum
        Time = time.strftime("%Y-%m-%d", time.localtime())
        remindMessage = '新冠病毒疫情防控期间签到情况\n'\
              '{}班共{}人\n' \
              '已完成{}人，未完成{}人\n\n' \
              '未完成\n' \
              '{}\n' \
              '{}'.format(classID, totalNum, DoNum, DoNotNum, Time, DoNotStr)
        return str(remindMessage)





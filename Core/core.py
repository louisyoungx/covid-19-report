import random
import ssl
import time

from ClassData.DataAPI import ClassExistsList, ClassGroupID
from Config.settings import config
from Corvid19Reporter.corvid_19_report import Corvid19Report
from Logger.logger import logger
from Message.message import sendFriendMessage, sendGroupMessage


def main():
    ssl._create_default_https_context = ssl._create_unverified_context
    ID = config.settings("Corvid_19_Report", "ID")
    DEBUG = config.settings("Debug", "DEBUG")
    corvid_19_report = Corvid19Report(ID)
    classList = ClassExistsList()
    for classID in classList:
        remindMessage = corvid_19_report.classDoNotList(classID)
        groupID = ClassGroupID(classID)
        if groupID != "":
            if DEBUG:
                logger.info(remindMessage)
                sendFriendMessage(remindMessage, 1462648167)  # 发送个人消息
                time.sleep(3)
            else:
                sendGroupMessage(remindMessage, groupID)
                time.sleep(random.randint(10,60))

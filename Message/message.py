import json
import requests

from Logger.logger import logger


def sendFriendMessage(message, userid):
    try:
        URL = "192.168.1.72:8888"
        path = "sendFriendMessage"
        URL = "http://{}/{}".format(URL, path)

        body = {
            "sessionKey": "YourSession",
            "target": userid,
            "messageChain": [
                {"type": "Plain", "text": message}
            ]
        }

        # sender = requests.post(URL, params = params, data=json.dumps(body))
        sender = requests.post(URL, data=json.dumps(body))

        mes = message.replace("\n", " ")
        if len(mes) > 10:
            mes = mes[:10] + "···"
        logger.info("Send {}".format(mes))


        # print(sender.request.url)
        # sender.raise_for_status()
        # print(sender.text)
        return True
    except:
        logger.error("Message Send Failed")
        return False


def sendGroupMessage(message, groupid):
    try:
        URL = "192.168.1.72:8888"
        path = "sendGroupMessage"
        URL = "http://{}/{}".format(URL, path)

        body = {
            "sessionKey": "YourSession",
            "target": groupid,
            "messageChain": [
                {"type": "Plain", "text": message}
            ]
        }

        # sender = requests.post(URL, params = params, data=json.dumps(body))
        sender = requests.post(URL, data=json.dumps(body))
        mes = message.replace("\n", " ")
        if len(mes) > 10:
            mes = mes[:10] + "···"
        logger.info("Send {}".format(mes))

        # print(sender.request.url)
        # sender.raise_for_status()
        # print(sender.text)
        return True
    except:
        logger.error("Message Send Failed")
        return False

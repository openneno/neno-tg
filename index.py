import datetime
import time
from sanic import Sanic
from sanic.response import text
import redis
import requests
import json
import bson
import re
import base64
import os
import imghdr

# TgBotToken
token = ""
if len(token) == 0:
    token = os.environ.get('token')
# tgBot webHookUrl
webHookUrl = ""
if len(webHookUrl) == 0:
    webHookUrl = os.environ.get('webHookUrl')
# redis 地址
redisHost = ""
if len(redisHost) == 0:
    redisHost = os.environ.get('redisHost')

# redis端口
redisPort = 0
if redisPort == 0:
    redisPort = int(os.environ.get('redisPort'))

# redis密码
redisPassword = ""
if len(redisPassword) == 0:
    redisPassword = os.environ.get('redisPassword')
r = redis.Redis(host=redisHost, port=redisPort, db=0, password=redisPassword)

proxies = {
    "http": "http://127.0.0.1:1081",
    "https": "http://127.0.0.1:1081",
}


def setWebhook(hookUrl):
    url = "https://api.telegram.org/bot{}/setWebhook".format(token)

    payload = json.dumps({
        "url": hookUrl
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)

    print(response.text)


def sendMessage(chatId, text):
    url = "https://api.telegram.org/bot{}/sendMessage".format(token)

    payload = json.dumps({
        "chat_id": chatId,
        "text": text
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
    print(response.json())


def getFile(FileId):
    url = "https://api.telegram.org/bot{}/getFile".format(token)

    payload = json.dumps({
        "file_id": FileId
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
    filere = response.json()
    print(filere)

    return filere


def getFileDown(filePath):
    url = "https://api.telegram.org/file/bot{}/{}".format(token, filePath)
    response = requests.request("GET", url)
    # response = requests.request("GET", url, proxies=proxies)
    photoContent = response.content
    return photoContent


setWebhook("{}/{}".format(webHookUrl, token))

app = Sanic("neno-wx")


@app.post("/{}".format(token))
def nenoTGPOST(request):
    print(request.json)
    message = request.json
    # get_file()
    chatId = message["message"]["chat"]["id"]
    content = ""
    photo = ""
    if ("text" in message["message"]):
        content = message["message"]["text"]
    if ("photo" in message["message"]):
        if ("caption" in message["message"]):
            content = message["message"]["caption"]
        photoPath = getFile(message["message"]["photo"][-1]["file_id"])["result"]["file_path"]
        photo = getFileDown(photoPath)

    if content.startswith("/token "):
        githubToken = content[7:]
        r.set("githubToken_{}".format(chatId), githubToken)
        sendMessage(chatId, "githubToken 已设置")
        return text("")
    elif content.startswith("/repo "):
        repo = content[6:]
        r.set("githubRepo_{}".format(chatId), repo)
        sendMessage(chatId, "github笔记仓库名 已设置")
        return text("")

    elif content.startswith("/username"):
        username = content[10:]
        r.set("githubUserName_{}".format(chatId), username)
        sendMessage(chatId, "github用户名 已设置")
        return text("")
    githubToken, githubRepo, githubUserName = findGithubConfigByUserT(chatId)

    if githubToken is None:
        sendMessage(chatId, 'githubToken没有配置\n输入 /token 你的token \n如/token nenOhVi3pIJn 进行配置')

        return text("")
    elif githubRepo is None:
        sendMessage(chatId, 'github笔记仓库名没有配置\n输入 /repo你的笔记仓库名 \n如/repo nenonote 进行配置')

        return text("")

    elif githubUserName is None:
        sendMessage(chatId, "github用户名没有配置\n输入 /username 你的github用户名 \n如/username mran 进行配置'")
        return text("")
    else:
        githubToken = githubToken.decode("UTF-8")
        githubRepo = githubRepo.decode("UTF-8")
        githubUserName = githubUserName.decode("UTF-8")
        reply(githubToken, githubRepo, githubUserName, chatId, content, photo)
    return text("")


def reply(githubToken, githubRepo, githubUserName, chatId, content, photo):
    suffixName=""
    photoId=""
    if photo != "":
        status_code, retext, photoId,suffixName = sendNenoPhotoToGithub(githubToken, githubRepo, githubUserName, photo)

    status_code, retext = sendNenoContentToGithub(githubToken, githubRepo, githubUserName, content, photoId,suffixName)
    if (status_code == 201):
        sendMessage(chatId, "保存成功")
    elif status_code == 401:
        sendMessage(chatId, '错误码:{} token错误\n信息:{}'.format(status_code, retext))
    elif status_code == 404:
        sendMessage(chatId, '错误码:{} 仓库名或用户名错误\n信息:{}'.format(status_code, retext))

    else:
        sendMessage(chatId, '发生未知错误')


# 从redis获得保存的用户github设置
def findGithubConfigByUserT(userId):
    githubToken = r.get("githubToken_{}".format(userId))
    githubRepo = r.get("githubRepo_{}".format(userId))
    githubUserName = r.get("githubUserName_{}".format(userId))
    # print(githubToken, githubRepo, githubUserName)
    return githubToken, githubRepo, githubUserName


# 根据用户的github设置将照片发送到github
def sendNenoPhotoToGithub(githubToken, githubRepo, githubUserName, photo):

    photoId = str(bson.ObjectId())

    suffixName = imghdr.what(None, photo)

    url = "https://api.github.com/repos/{}/{}/contents/picData/{}.{}".format(githubUserName, githubRepo,
                                                                    photoId, suffixName)

    payload = json.dumps({
        "content": base64.b64encode(photo).decode("utf-8"),
        "message": "pic upload tg"
    })
    headers = {
        'authorization': 'token {}'.format(githubToken),
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.status_code, response.text, photoId)
    return response.status_code, response.text, photoId,suffixName


# 根据用户的github设置将内容发送到github
def sendNenoContentToGithub(githubToken, githubRepo, githubUserName, content, photoId,suffixName):
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    createTime = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset),
                                                 microsecond=0).isoformat()
    createDate = createTime[:10]
    _id = str(bson.ObjectId())

    url = "https://api.github.com/repos/{}/{}/contents/{}/{}.json".format(githubUserName, githubRepo, createDate,
                                                                          _id)
    tags = re.findall(r"#\S*", content)
    images = []
    if photoId != "":
        images = [{
            "key": photoId,
            "suffixName": suffixName
        }]
    neno = {
        "content": "<p>{}</p>".format(content),
        "pureContent": content,
        "_id": _id,
        "parentId": "",
        "source": "tg",
        "tags": tags,
        "images": images,
        "created_at": createTime,
        "sha": "",
        "update_at": createTime
    }
    base64Content = base64.b64encode(json.dumps(neno, sort_keys=True, indent=4, ensure_ascii=False).encode("UTF-8"))
    payload = json.dumps({
        "content": base64Content.decode("UTF-8"),
        "message": "[ADD] {}".format(content)
    })
    headers = {
        'authorization': 'token {}'.format(githubToken),
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    return response.status_code, response.text

#在服务器部署是取消下一行的注释
# app.run(host="0.0.0.0", port=9001, debug=True)

neno-tg是是使用python编写的用于通过TelegramBot记录笔记到neno的项目。

项目的部署分为两部分

1. Telegrambot的设置参考[官方文档](https://core.telegram.org/bots)
2. 后端服务部署，根据自己的情况选择服务器部署或者是Vercel部署

## 服务器部署

自有域名和服务器可以选择此方式。

**python版本：3.6**

#### 1.拉取项目

```sh
git clone https://github.com/openneno/neno-tg.git
```

#### 2.安装依赖

```sh
cd neno-tg
pip3 install -r requirements.txt -t .
```

#### 3.修改index.py中的配置参数

必需：TelegramBot的`token`、TelegramBot的使用的回调域名`webHookUrl`，如`https://tgbot.nenotg.com`

设置redis相关的参数，用于存储其他用户的github Token、Repo，userName。参数包括：redis 地址`redisHost`，redis端口`redisPort`、redis密码`redisPassword`
你可以使用[redislabs](https://app.redislabs.com/) 的免费redis服务，有30mb足够个人使用了。

#### 4.启动项目
```sh
#取消index.py里的这条注释
app.run(host="0.0.0.0", port=9001, debug=True)
```
端口号为9001，有需要可以在index.py中修改。

```sh
python3 -u index.py
```

#### 5.配置端口映射

由于配置TGBot回掉的要求，需要将端口号映射到443端口上。

## vercel的serverless部署

对于服务器不太了解可以使用此部署方式，此方式也是完全免费的。



### 点击Deploy按钮进行快速部署 [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fopenneno%2Fneno-tg.git&env=webHookUrl,token,redisPassword,redisPort,redisHost)

需要注意的要在vercel项目中填写相应的环境变量

包括：TelegramBot的`token`、TelegramBot的使用的回调域名`webHookUrl`，即vercel给你项目分配的正式环境域名，如`https://tgbot.nenotg.com`
，设置redis相关的环境变量，用于存储用户的github Token、Repo，userName。参数包括：redis 地址`redisHost`，redis端口`redisPort`、redis密码`redisPassword`

你可以使用[redislabs](https://app.redislabs.com/) 的免费redis服务，有30mb足够个人使用了。
## neno使用如何TGBot快速记录笔记

发送 `我的用户id`可以获得你在这个公众号中的id，主要用于配置仅自己可用时获得自己的用户id

输入 /token 你的token 如`/token nenOhVi3pIJn` 配置你的github token

输入 /repo 你的笔记仓库名 如`/repo nenonote` 进行配置仓库名称

输入 /username 你的github用户名 如`/username mran` 进行配置github用户名

当然这些在使用时都会有提示。

你可以使用我的TGbot进行测试。
[NenoTG_Bot](https://t.me/NenoTG_Bot)

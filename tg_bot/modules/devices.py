import json, math
from datetime import datetime
import urllib.error
import urllib.parse
import urllib.request

from tg_bot import dispatcher
from telegram.ext import CommandHandler

baseURL = "https://raw.githubusercontent.com/KrakenProject/official_devices/master"
website = 'krakenproject.github.io/?device='

__help__ = "- /devices - get all supported devices\n- /codename - get latest build"

__mod_name__ = "Devices"


def command_handler(bot, update):
    res = handleMessage(update.message.text);
    if res is None:
        return
    update.message.reply_markdown(res, disable_web_page_preview=True)

def getDevices():
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read())
    devices_list2 = [device['codename'] for device in devices]
    if not devices_list2 == devices_list:
        addHandlers(devices_list2)
    res = ["***Supported Devices: ***\n\n"];
    for device in devices:
        res.append(device['name'] + ' - /' + device['codename'] + "\n")
    return ''.join(res)   

def getDevicesList():
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read())
    return [device['codename'] for device in devices]

def getDeviceInfo(codename):
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read());
    for device in devices:
        if device['codename'] == codename:
            return device
    return ''

def getLastestBuild(codename):
    try:
        request = urllib.request.urlopen(baseURL + '/builds/'+codename+'.json')
    except urllib.error.HTTPError:
        return
    builds = json.loads(request.read());
    return builds['response'][len(builds)];

def getChangelogFile(filename, codename):
    try:
        return str(urllib.request.urlopen(baseURL + '/changelog/' + codename + '/' + 
            filename.replace('zip','txt')).read()).split("'")[1]
    except Exception as e:
        return None

def humanSize(bytes):
    if bytes == 0:
      return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def humanDate(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y/%m/%d %H:%M')

def addHandlers(codenames):
    for codename in codenames:
        dispatcher.add_handler(CommandHandler(codename, command_handler))

def handleMessage(msg):
    # Clean and normalize the input message
    msg = msg.replace("/","")
    msg = msg.replace("@KrakenProject_bot",'')

    if msg == 'devices':
        return getDevices()

    # grab device/build/changelog
    device = getDeviceInfo(msg)
    build = getLastestBuild(msg)
    if build is None:
        return
    changelog = getChangelogFile(build['filename'], msg)
          
    # setup the message and send
    if device['maintainer_name'] is not None and build['filename'] is not None:
        # dirty place XD
        res = ("***Latest Kraken for {} ({})***\n\n".format(device['name'],device['codename'])+
        "***Developer:*** [{}]({})\n".format(device['maintainer_name'], device['maintainer_url'])+
        "***Website:*** [{}]({})\n".format(device['codename'] + ' Page', website + device['codename'])+
        "***XDA:*** [{}]({})\n\n".format(device['codename'] + ' Thread', device['xda_thread'])+
        "***Build:*** [{}]({})\n".format(build['filename'], build['url'])+
        "***Size:*** {}\n".format(humanSize(int(build['size'])))+
        "***Date:*** {}\n\n".format(humanDate(int(build['datetime']))))

        # ignore changelog if needed
        if changelog is not None:
            res += ("***Changelog:***\n```\n{}```".format(changelog.replace('\\n','\n')))

        return res;

devices_list = getDevicesList()


dispatcher.add_handler(CommandHandler('devices', command_handler))
addHandlers(devices_list)

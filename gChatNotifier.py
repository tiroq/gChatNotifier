#!/usr/bin/python

import sys
import json
import urllib2
import datetime
import optparse
from json import dumps


class ChatSender:

    INI_FILE = '/usr/local/share/zabbix/alertscripts/google_chat.ini'

    PROBLEM_IMG = 'https://png.pngtree.com/svg/20161208/status_warning_336325.png'
    ACK_IMG = 'https://static1.squarespace.com/static/549db876e4b05ce481ee4649/t/54a47a31e4b0375c08400709/1472574912591/form-3.png'
    RESOLVED_IMG = 'https://image.flaticon.com/icons/png/128/291/291201.png'

    def __init__(self, webhook_name):
        cp = configparser.RawConfigParser()
        try:
            cp.read(self.INI_FILE)
            if cp.has_section('zabbix'):
                self.zabbix_url = cp['zabbix']['host']
                self.datafile = cp['zabbix']['datafile']
            if cp.has_section('chat'):
                self.webhook = cp['chat'][webhook_name]
        except:
            print('Falha na leitura do arquivo de configuracao')

        self.evt_thread = self.readEventThread()
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        date = {}
        date['date'] = today

        try:
            if self.evt_thread['date'] and self.evt_thread['date'] != today:
                with open(self.datafile, 'w') as f:
                    json.dump(date, f)
        except:
            self.evt_thread['date'] = today
            with open(self.datafile, 'w') as f:
                json.dump(self.evt_thread, f)


    def sendMessage(self, event):
        url = "https://chat.googleapis.com/v1/spaces/AAAAYxsnrwE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=biSVy1f8GxHS08W5W4zes5UmG4p3fHvYGZAO37P-ySY%3D"

        body = {
            "cards": [ 
              { "header": 
                { "title": "Severidade: " + 1,
                  "subtitle": 1,
                  "imageUrl": PROBLEM_IMG,
                  "imageStyle": "IMAGE"
                },
                "sections": [
                  { "widgets": [
                    { "keyValue": {
                        "topLabel": "Alarme",
                        "content": "asd",
                        "contentMultiline": "true"
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Host",
                        "content": "dsfghfj ",
                        "contentMultiline": "true"
                      }
                    },
                    { "keyValue": {
                        "topLabel": "Data/Hora",
                        "content": "date +  + time"
                      }
                    },
                    { "keyValue": {
                        "topLabel": "ID do Evento",
                        "content": "-1"
                      }
                    }
                  ]},
                  { "widgets": [
                    { "buttons": [
                      { "textButton": 
                        { "text": "Ver o evento no ZABBIX",
                          "onClick": {
                            "openLink": {
                              "url": ""
                            }
                          }
                        }
                      }
                    ]}
                  ]}
              ]}
            ]}

        message_headers = { 'Content-Type': 'application/json; charset=UTF-8'}

        # answer = requests.post(url, data=json.dumps(body), headers=message_headers)
        # print(answer)
        # response = answer.json()
        # print(response)

        data = json.dumps(body)
        req = urllib2.Request(url, data, message_headers)
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()

    def readEventThread(self):
        try:
            with open(self.datafile) as f:
                result = json.load(f)
        except:
            result = {}
        return result

    def writeEventThread(self, event_thread):
        content = self.readEventThread()
        if self.trigger_id not in content:
            content[self.trigger_id] = event_thread[self.trigger_id]
            with open(self.datafile, 'w') as f:
                json.dump(content, f)


if __name__ == '__main__':

    options = optparse.OptionParser(usage='%prog [options]', description='pandoc handler')
    options.add_option('-w', '--webhook', type='str', default=None, help='webhook')

    opts, args = options.parse_args()
    webhook_name = opts.webhook

    cs = ChatSender(webhook_name)
    cs.sendMessage("event")

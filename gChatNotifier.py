#!/usr/bin/python2

import sys
import json
import urllib2
import datetime
import optparse
from json import dumps


class Sender:
    statuses = {
        'fail': 'https://png.pngtree.com/svg/20161208/status_warning_336325.png',
        'note': 'https://static1.squarespace.com/static/549db876e4b05ce481ee4649/t/54a47a31e4b0375c08400709/1472574912591/form-3.png',
        'pass': 'https://image.flaticon.com/icons/png/128/291/291201.png'
    }
    message_headers = { 'Content-Type': 'application/json; charset=UTF-8'}

    def __init__(self, webhook, delimeter="::", debug=False):
        self.delimeter = delimeter
        self.debug = debug
        self.url = webhook
        

    def _send(self, body):
        data = json.dumps(body)
        if self.debug: print data
        req = urllib2.Request(self.url, data, self.message_headers)
        f = urllib2.urlopen(req)
        response = f.read()
        if self.debug: print response
        f.close()


    def sendMessage(self, text):
        body = { 'text': text }
        self._send(body)

    def sendForm(self, title='', subtitle='', status='note', entries=[], details_url='localhost'):
        img = self.statuses.get(status, 'note')

        _entries = []
        for n, entry in enumerate(entries):
            if self.delimeter not in entry:
                entry = 'field{0}{1}{2}'.format(n, self.delimeter, entry)
            topLabel, content = entry.split(self.delimeter)
            if content == '': content = 'empty'
            _entries.append({ 'keyValue': {'topLabel': topLabel, 'content': content, 'contentMultiline': 'true'}})

        body = { 
               'cards':[{ 
                    'header':{ 
                        'title': title,
                        'subtitle': subtitle,
                        'imageUrl': img,
                        'imageStyle': 'IMAGE'
                    },
                    'sections': []
                }]
            }
        if len(_entries) > 0:
            body['cards'][0]['sections'].append({ 'widgets': _entries })
        if details_url != '':
            body['cards'][0]['sections'].append(
                { 'widgets': [{
                    'buttons': [{ 'textButton': { 'text': 'DETAILS', 'onClick': { 'openLink': { 'url': details_url }}}}]
                    }]
                }
            )

        self._send(body)

if __name__ == '__main__':

    options = optparse.OptionParser(usage='%prog [options]', description='gSender')
    options.add_option('-w', '--webhook', type='str', default=None, help='webhook url as is')
    options.add_option('-d', '--delimeter', type='str', default='::', help='delimeter for entry. default "::". e.g.: -e field1::value1')
    options.add_option('-e', '--entry', action='append', dest='entries')
    options.add_option('--details_url', type='str', default='', help='external link to detailed report')
    options.add_option('--status', type='str', default='note', help='status of the report(note/pass/fail)')
    options.add_option('--title', type='str', default='Report', help='title of the message')
    options.add_option('--subtitle', type='str', default='Short report', help='subtitle of the message')

    opts, args = options.parse_args()
    if not opts.webhook:
        options.error('Please set webhook url via -w key!')
        sys.exit(1)

    service = Sender(opts.webhook, delimeter=opts.delimeter)
    service.sendForm(entries=opts.entries, status=opts.status, title=opts.title, subtitle=opts.subtitle, details_url=opts.details_url)

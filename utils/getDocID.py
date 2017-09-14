# -*- coding: utf-8 -*-
# author__ = "lyao"
# version__ = "1.0.1"
# Date: 2017/09/09 11:57
import requests
import pymysql
from scrapy.selector import Selector
from wenshu.utils.wenshu_session import getSess
import re
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
}
(sess,vl5x) = getSess()
conn = pymysql.Connection(host='127.0.0.1',user='root', password="123",
                 database='crawl',use_unicode=True,charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('SELECT docID_list FROM anyou')
docID_tup = cursor.fetchall()
for tup in list(docID_tup):
    for id in list(tup):
        for doc_id in list(id):
            print id
            # doc_url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}'.format(id)
            # while True:
            #     try:
            #         response = requests.get(doc_url,headers=headers,timeout=10)
            #         # 有特殊符号前面加R 先提出整体 再处理特殊符号
            #         title = re.search(u'''.*?"Title(.*?)PubDate''',response.content).group(1)
            #         pubDate = re.search(u'''.*?PubDate(.*?)Html''',response.content).group(1)
            #         title = re.match(r'\\":\\"(.*?)\\",\\"', title).group(1).decode('utf-8')
            #         pubDate = re.match(r'\\":\\"(.*?)\\",\\"', pubDate).group(1)
            #         with open('doc.html','w') as f:
            #             f.write(response.content)
            #         select = Selector(response)
            #         doc_list = select.xpath("//div//text()").extract()
            #         content = '  '.join(doc_list)
            #         doc = u'标题:'+title+u',发布日期:'+pubDate+u',正文:'+content
            #         print doc
            #         break
            #     except Exception as e:
            #         continue
        break
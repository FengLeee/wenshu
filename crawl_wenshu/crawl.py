# -*- coding: utf-8 -*-
__author__ = "yaoo"
__version__ = "1.0.1"
__email__ = "1711602280@qq.com"
'''只能爬取100页 没有添加查询条件'''
import execjs
import json
import re
import pymysql
import math
from wenshu.utils.wenshu_log import getLogger
from wenshu.utils.wenshu_session import getSess
from wenshu.utils.yundama import result_captcha
import time
from wenshu.utils.captcha_local import retrive_img,process_img,recognize
import random
from scrapy.selector import Selector
import requests
sess,vl5x = getSess()

logger = getLogger(__name__)

conn = pymysql.Connection(host='127.0.0.1',user='root',password='123',
                          database='crawl',charset='utf8mb4',use_unicode=True)
cursor = conn.cursor()

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'X-Forwarded-For': '{}.{}.{}.{},113.88.176.160'.format(random.randint(1,254),random.randint(1,254),random.randint(1,254),random.randint(1,254))
}

with open('ua_list.json', 'r') as f:
    ua_list = json.load(f)

def crwal_condition(condition,total):
    '''
    :param condition: 查询的条件
    :param total: 所有的案由
    :return:
    '''
    anyou = '  '.join(total)
    count,id_list = getFirstPage(condition,total)

    if count=='':
        return
    # count为0时 id_list = []
    if count==0:
        cursor.execute('''insert into wenshu(anyou, count) VALUES (%s,%s)''', (anyou, count))
        conn.commit()
        print 'crawl %s over' % (condition)
        return
    elif count<=20:
        for docID in id_list:
            # url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}'.format(docID)
            # 根据docID请求文档 存入数据库
            insertMysql(docID,anyou,count)

        # 插入MySQL return
        # docID = ','.join(docID_list)
        # cursor.execute('''insert into anyou(anyou, count, docID_list) VALUES (%s,%s,%s)''', (anyou, count, docID))
        # conn.commit()
        print 'crawl %s over' % (condition)
        return

    elif count>2000:
        cursor.execute('''insert into wenshu(anyou, count) VALUES (%s,%s)''',
                       (anyou, count))
        conn.commit()
        print (anyou + ', count is: %s' % (count))
        print 'crawl %s over' % (condition)
        return

    else:
        index = int(math.ceil(count/20.0))
        for docID in id_list:
            insertMysql(docID, anyou, count)
        page=2
        while page <=index:
            count, id_list = getFirstPage(condition,total,index=page)
            if id_list=='':
                return
            for docID in id_list:
                # 这所有的docID放入一个list 最后添加到MySQL
                # url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}'.format(docID)
                # ef6a2973-81a8-4834-9533-aa340ebb02a0
                insertMysql(docID, anyou, count)
            page+=1
    # 最后爬取完毕
    print 'crawl %s over' %(condition)
    return

def getCaptcha():
    global sess,vl5x
    ua = random.choice(ua_list)
    while True:
        try:
        # 获取验证码 发送验证码 验证guid
            yzm = execjs.compile('''
            function createGuid() {
                return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
            }
            function ref() {
                var guid = createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" + createGuid() + createGuid() + createGuid(); //CreateGuid();
                return guid;
            }
            ''')
            guid = yzm.call('ref')
            yzm_url = 'http://wenshu.court.gov.cn/ValiCode/CreateCode/?guid={}'.format(guid)
            headers = {
                'User-Agent': ua,
                'X-Forwarded-For': '{}.{}.{}.{},113.88.176.160'.format(random.randint(1, 254), random.randint(1, 254),
                                                                       random.randint(1, 254), random.randint(1, 254))
            }
            # yzm_url = 'http://wenshu.court.gov.cn/User/ValidateCode?guid={}'.format(guid)
            yzm = sess.get(yzm_url, headers=headers,allow_redirects=False)
            if yzm.status_code == 302:
                sess, vl5x = getSess()
                continue
            if yzm.status_code >= 500:
                print 'the service is bad and response_status_code is %s, wait one minute retry' % (
                    yzm.status_code)
                time.sleep(60)
                continue
            with open('captcha.jpg', 'wb') as f:
                f.write(yzm.content)
            captcha = result_captcha('captcha.jpg')
            return captcha,guid
        except Exception as e:
            print 'get captcah bad retry again'
            pass


def getFirstPage(condition,total,index=1):
    '''
    获取案由的具体页面
    :param condition:
    :param total:
    :param index:
    :return:
    '''
    global sess, vl5x
    anyou = ','.join(total)
    num_level = 0
    level = condition[0:4]
    if u'一级案由' == level:
        num_level = 1
    elif u'二级案由' == level:
        num_level = 2
    elif u'三级案由' == level:
        num_level = 3
    elif u'四级案由' == level:
        num_level = 4

    i = 0
    while i < 5:
        captcha, guid = getCaptcha()  # 每次请求都要用到
        form_data = {
            'Param': condition,
            'Index': index,
            'Page': 20,
            'Order': '法院层级',
            'Direction': 'asc',
            'vl5x': vl5x,
            'number': captcha,
            'guid': guid,

        }
        try:
            ua = random.choice(ua_list)
            headers = {
                'User-Agent': ua,
                'X-Forwarded-For': '{}.{}.{}.{},113.88.176.160'.format(random.randint(1, 254), random.randint(1, 254),
                                                                       random.randint(1, 254), random.randint(1, 254))
            }
            print num_level*'    '+'%s is crawling index is %s' %(condition, index)
            response = sess.post('http://wenshu.court.gov.cn/List/ListContent', headers=headers, data=form_data)
            if response.status_code == 302:
                sess, vl5x = getSess()
                continue
            if response.status_code >= 500:
                print 'the service is bad and response_status_code is %s, wait one minute retry' % (
                    response.status_code)
                time.sleep(60)
                continue
            # 返回的数据进行序列化
            data_unicode = json.loads(response.text)

            if data_unicode == u'remind key':
                # cookie 到期
                sess, vl5x = getSess()
                print 'getFirstPage response content is remind key retry again'
                continue
            if data_unicode == u'remind':
                # cookie访问次数过多
                sess, vl5x = getSess()
                ua = random.choice(ua_list)
                remind_captcha = sess.get('http://wenshu.court.gov.cn/User/ValidateCode',headers=headers)
                img = retrive_img(remind_captcha)
                img = process_img(img)
                captcha = recognize(img)
                captcha_data = {
                    'ValidateCode': captcha
                }
                sess.post('http://wenshu.court.gov.cn/Content/CheckVisitCode',headers=headers,data=captcha_data)
                print 'getFirstPage response content is remind  retry again'
                continue
            # 每一页的docID
            id_list = re.findall(u'''.*?"文书ID\\":\\"(.*?)\\",''', data_unicode)
            # count是根据条件condition 筛选出来的总文档数 根据count决定要爬多少页
            data_list = json.loads(data_unicode)
            if len(data_list) == 0:
                time.sleep(2)
                print 'getFirstPage response content is [] retry again'
                continue
            count = data_list[0]['Count']
            count = int(count)
            return count,id_list
        except Exception as e:
            i += 1
            if i == 5:
                message = anyou+': '+str(index)+str(e).decode('utf-8')+'   '+'is bad'
                logger.error(message)
                print (message)
                return '',''


def insertMysql(docID,anyou,count):
    '''
    根据文档ID爬取文书
    :param docID: 文书ID
    :param anyou: 案由条件
    :param count: 案由条件对应的文档个数
    :return:
    '''
    global sess, vl5x
    doc_url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}'.format(docID)
    i = 0
    while True:
        try:
            ua = random.choice(ua_list)
            headers = {
                'User-Agent': ua,
                'X-Forwarded-For': '{}.{}.{}.{},113.88.176.160'.format(random.randint(1, 254), random.randint(1, 254),
                                                                       random.randint(1, 254), random.randint(1, 254))
            }
            doc_response = sess.get(doc_url, headers=headers)

            if doc_response.status_code == 302: #重定向 重新获取cookie
                sess, vl5x = getSess()
                continue
            if doc_response.status_code >= 500: #服务器出错
                print 'the service is bad and response_status_code is %s, wait one minute retry' % (
                    doc_response.status_code)
                time.sleep(60)
                continue
            try:
                data_unicode = json.loads(doc_response.text) # 如果返回数据异常,对返回的数据进行序列化
                if data_unicode == u'remind key':
                    # cookie 到期
                    sess, vl5x = getSess()
                    print 'getFirstPage response content is remind key retry again'
                    continue
                if data_unicode == u'remind':
                    # cookie访问次数过多
                    sess, vl5x = getSess()
                    ua = random.choice(ua_list)
                    remind_captcha = sess.get('http://wenshu.court.gov.cn/User/ValidateCode', headers=headers)
                    img = retrive_img(remind_captcha)
                    img = process_img(img)
                    captcha = recognize(img)
                    captcha_data = {
                        'ValidateCode': captcha
                    }
                    sess.post('http://wenshu.court.gov.cn/Content/CheckVisitCode', headers=headers, data=captcha_data)
                    print 'getFirstPage response content is remind  retry again'
                    continue
            except Exception as e:
                pass
            # 有特殊符号前面加R 先提出整体 再处理特殊符号
            title = re.search(u'''.*?"Title(.*?)PubDate''', doc_response.content).group(1)
            pubDate = re.search(u'''.*?PubDate(.*?)Html''', doc_response.content).group(1)
            title = re.match(r'\\":\\"(.*?)\\",\\"', title).group(1).decode('utf-8')
            pubDate = re.match(r'\\":\\"(.*?)\\",\\"', pubDate).group(1)
            select = Selector(doc_response)
            doc_list = select.xpath("//div//text()").extract()
            content = '  '.join(doc_list)
            doc = u'标题:' + title + u',发布日期:' + pubDate + u',正文:' + content
            cursor.execute('''insert into wenshu(anyou, count, doc_id,content) VALUES (%s,%s,%s,%s)''',
                           (anyou, count, docID, doc))
            conn.commit()
            time.sleep(1)
            break
        except Exception as e:
            time.sleep(2)
            i+=1
            if i==5:
                message = anyou + ': ' + str(docID) + str(e).decode('utf-8') + '   ' + 'is bad'
                logger.error(message)
                print (message)
                break
            continue
if __name__ == '__main__':
    crwal_condition(u'三级案由:爆炸',[])
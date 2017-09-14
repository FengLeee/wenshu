# -*- coding: utf-8 -*-
# author__ = "lyao"
# version__ = "1.0.1"
# Date: 2017/09/04 18:36
import random
import re
import json
import time
from crawl import crwal_condition
from wenshu.utils.wenshu_log import getLogger
from wenshu.utils.wenshu_session import getSess
'''递归 深度爬取 以案由为选择条件 爬取总数小于等于2000的案由'''
logger = getLogger(__name__)
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'X-Forwarded-For': '{}.{}.{}.{},113.88.176.160'.format(random.randint(1, 254), random.randint(1, 254),
                                                           random.randint(1, 254), random.randint(1, 254))
}
# 获取sess和加密后的cookie字段
(sess,vl5x) = getSess()
FLAG = False
def getLastLevel(level,name,f,total):
    '''
    定位到最底层的子案由
    :param level: 案由层级 一级案由 二级案由 三级案由 四级案由
    :param name: 案由名称
    :param f:
    :param total: 当前案由的 所有父类案由
    :return:
    '''
    global sess, vl5x, FLAG
    if isinstance(level,str):
        level=level.decode('utf-8')
    if isinstance(name,str):
        name=name.decode('utf-8')

    condition = level + ':' + name

    # 判断level是几级案由
    if u'一级案由' == level:
        num_level = 1
        total[0] = condition
    elif u'二级案由' == level:
        num_level = 2
        total[1] = condition
    elif u'三级案由' == level:
        num_level = 3
        total[2] = condition
    elif u'四级案由' == level:
        num_level = 4
        total[3] = condition
    # 构造请求案由请求表单
    form_data = {
        'Param': level+':'+name,
        'parval':name
    }
    i= 0
    while i<3:
        try:
            response = sess.post('http://wenshu.court.gov.cn/List/ReasonTreeContent',
                                     headers=headers,data=form_data)
            if response.status_code == 302:#网站重定向 重新获取cookie
                (sess, vl5x) = getSess()
                # getLastLevel(level, name, f, total)
                continue
            if response.status_code >= 500:
                print 'the service is bad and response_status_code is %s, wait one minute retry' % (
                response.status_code)
                time.sleep(60)
                continue
            key_data = json.loads(response.text)  # Unicode
            reasonTree = json.loads(key_data)  # dict
            next_level = reasonTree[0]['Key'] # 下一级案由
            count = reasonTree[0]['Value'] # 获取当前案由的子类案由个数 如果子类案由数为0 则可以进行爬取
            count = int(count)
            if count == 0: # 说明到了最底层 可以构造参数 访问文档
                print num_level * '    ', level, name,'is crawling'
                f.write((num_level * '    ' + level + ': ' + name + '\n').encode('utf-8'))
                f.flush()
#                 if name == u'过失以危险方法危害公共安全':
#                     FLAG = True
                if True:
                    crwal_condition(condition,total)
                return
            else:
                print num_level * '    ', level, name
                f.write((num_level * '    ' + level + ': ' + name + '\n').encode('utf-8'))
                f.flush()
            key_list = re.findall(u'.*?\{\\"Key\\":\\"(.*?)\\",\\"Value\\"', key_data)
            key_list = [i for i in key_list if i != ''] #获取当前案由下的子案由
            break
        except Exception as e:
            time.sleep(2)
            if i==2:
                print e
                print num_level * '    ', level, name
                logger.error(condition+'    '+','.join(total)+str(e).decode('utf-8'))
                return
            i+=1

    if next_level == level: #如果子案由==当前案由会造成死循环
        return

    for next_name in key_list[1:]:
        # Value = child_dice['Value']
        # print next_level,next_name, Value
        time.sleep(2)
        getLastLevel(next_level, next_name, f,total)

if __name__ == '__main__':
    total=['','','','','']
    xs = open('condition.txt', 'a')
    getLastLevel('一级案由', '刑事案由',xs,total)
    xs.close()



    # ms = open(u'民事案由.txt', 'a')
    # xz = open(u'行政案由.txt', 'a')
    # pc = open(u'赔偿案由.txt', 'a')

    # getKey('一级案由', '民事案由',ms)
    # ms.close()
    # getKey('一级案由', '行政案由',xz)
    # xz.close()
    # getKey('一级案由', '赔偿案由',pc)
    # pc.close()

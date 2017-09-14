# -*- coding: utf-8 -*-
# author__ = "lyao"
# version__ = "1.0.1"
# Date: 2017/09/02 20:51
import requests
import re
import json
import time
import logging
# xs = open(u'刑事案由.txt', 'a')
# ms = open(u'民事案由.txt', 'a')
# xz = open(u'行政案由.txt', 'a')
# pc = open(u'赔偿案由.txt', 'a')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')

fh = logging.FileHandler('err.log',encoding='utf-8')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh)

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'
}



def getKey(level,name,li):
    if isinstance(level,str):
        level=level.decode('utf-8')
    if isinstance(name,str):
        name=name.decode('utf-8')

    form_data = {
        'Param': level+':'+name,
        'parval':name
    }

    i= 0
    key_list = []
    while i<3:
        try:
            response = requests.post('http://wenshu.court.gov.cn/List/ReasonTreeContent',
                                     headers=headers,data=form_data,timeout=10)
            key_data = json.loads(response.text)
            count = re.search(u'''\\"Value\\":\\"(\d+)\\",''',key_data).group(1)
            count = int(count)
            # 网站改版不能根据这个条件来判断
            # if key_data == "":
            key = level + ":" + name
            if count == 0:
                # 说明到了最底层 可以构造参数 访问文档
                # 得到文档后 通过count可以判断文档数量  小于2000可以爬取(如果进行爬取 提取文档ID 文档ID+案由一起存入到MySQL) 大于两千记录下来 等待重新判断
                li.append(key)
                return
            else:
                # {NAME: []}
                li.append({key:[]})
            key_list = re.findall(u'.*?\{\\"Key\\":\\"(.*?)\\",\\"Value\\"', key_data)
            key_list = [i for i in key_list if i != '']
            break
        except Exception as e:
            print e
            time.sleep(2)
            if i==2:
                logger.error(level+name)
                return
            i+=1

    next_level = key_list[0]
    # 防止死循环
    if next_level == level:
        return
    name_list = key_list[1:]
    name_list = list(enumerate(name_list))

    num_level = level[0:1]
    if u'一' == num_level:
        num_level = 1
    elif u'二' == num_level:
        num_level = 2
    elif u'三' == num_level:
        num_level = 3
    elif u'四' == num_level:
        num_level = 4


    for index,next_name in name_list:
        print num_level * '    ', next_level, next_name
        time.sleep(2)
        # 添加子元素
        str_xs = json.dumps(xs,ensure_ascii=False)
        with  open('ms.txt','w') as f:
            f.write(str_xs.encode('utf-8'))
        # 把当前最后一个节点传递到下一次请求 当前节点永远是数组的最后一位
        temp = li[len(li)-1][key]
        getKey(next_level, next_name, temp)



if __name__ == '__main__':
    xs = []

    # getKey('一级案由', '刑事案由',xs)
    getKey('一级案由', '民事案由',xs)
    # getKey('一级案由', '行政案由',xz)
    # getKey('一级案由', '赔偿案由',pc)
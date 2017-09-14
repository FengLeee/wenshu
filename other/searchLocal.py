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
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Referer': 'http://wenshu.court.gov.cn/list/list/',
    'Host': 'wenshu.court.gov.cn',
    'Accept': '*/*',
    'Accept-Language': 'zh,zh-TW;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
}
cookies = {
    'vjkl5': 'E2330319A1FFE3454001C6180D52FF9DAEF8B785',
'	vjkl5': 'DED1AFEA1FF0246AA012F181489723ABBCD9EF73',
'	_gscu_2116842793': '04413044q62dqq12',
'	_gscs_2116842793': '04413044mk0k8012|pv:1',
'	_gscbrs_2116842793': '1',
'	Hm_lvt_3f1a54c5a86d62407544d433f6418ef5': '1504413044',
'	Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5': '1504413044'
}
def getKey(level,name,f):
    if isinstance(level,str):
        level = level.decode('utf-8')
    if isinstance(name,str):
        name = name.decode('utf-8')

    num_level = 0
    # 根据请求的层级 控制打印的格式
    if u'法院地域' == level:
        num_level = 1
    elif u'中级法院' == level:
        num_level = 2
    # 基层法院下层没有更多 所以这里可以return
    elif u'基层法院' == level:
        return

    print num_level * '    ', level, name
    # 写入当前请求的层级 不管下面的请求成功与否 都写入当前的层级
    f.write((num_level * '    ' + level + ': ' + name + '\n').encode('utf-8'))
    f.flush()

    form_data = {
        'Param': level+':'+name,
        'parval':name
    }
    key_list = []
    i = 0
    while i < 3:
        try:
            response = requests.post('http://wenshu.court.gov.cn/List/CourtTreeContent',
                                     headers=headers,data=form_data,timeout=10,
                                     cookies=cookies)
            key_data = json.loads(response.text)
            if key_data == "":
                return
            key_list = re.findall(u'.*?\{\\"Key\\":\\"(.*?)\\",\\"Value\\"', key_data)
            # 去除空格后的list
            key_list = [i for i in key_list if i != '']
            break
        except Exception as e:
            print e
            time.sleep(2)
            if i == 2:
                logger.error(level+name)
                return
            i += 1
    # if len(key_list)==0:
    #     return
    # 下一个请求的层级
    next_level = key_list[0]
    # 如果返回的层级  和请求的层级相等 会造成死循环
    if next_level == level:
        return
    for next_name in key_list[1:]:
        time.sleep(2)
        getKey(next_level, next_name, f)


if __name__ == '__main__':
    #  辽宁省
    # 辽宁省沈阳市中级人民法院  这两个先忽略
    dy = open(u'法院地域.txt', 'a')
    # 法院地域
    init_list = [
        '法院地域',
        # '最高人民法院',
        # '北京市',
        # '天津市',
        # '河北省',
        # '山西省',
        # '内蒙古自治区',
        # '吉林省',
        # '黑龙江省',
        # '上海市',
        # '江苏省',
        # '浙江省',
        # '安徽省',
        # '福建省',
        # '辽宁省',
        # '辽宁省沈阳市中级人民法院',
        '江西省',
        '山东省',
        '河南省',
        '湖北省',
        '湖南省',
        '广东省',
        '广西壮族自治区',
        '海南省',
        '重庆市',
        '四川省',
        '贵州省',
        '云南省',
        '西藏自治区',
        '陕西省',
        '甘肃省',
        '青海省',
        '宁夏回族自治区',
        '新疆维吾尔自治区',
        '新疆维吾尔自治区高级人民法院生产建设兵团分院',
    ]
    level = init_list[0]
    # for name in init_list[1:]:
        # getKey(level,name,dy)
    getKey('法院地域','辽宁省',dy)

    dy.close()
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     cgb
   Description :
   Author :       Vincent
   date：          2020/4/20
-------------------------------------------------
   Change Activity:
                   2020/4/20:
-------------------------------------------------
"""
import os
import json
import time
import logging

from requests_html import HTMLSession
from pyppeteer.errors import TimeoutError

products = list()
with open("config.json", 'r', encoding='UTF-8') as f:
    config = json.load(f)
    products = list(filter(lambda x: x['type'] == 'cgb', config['products']))

bark_key = os.environ.get("BARK_KEY")


class CgbMonitor:

    def __init__(self):
        start_url = "http://shop.cgbchina.com.cn/mall/integrate/zengzhi"
        self.sess = HTMLSession()
        self.sess.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.88 Safari/537.36 '
        }
        self.sess.get(start_url)

    def parser(self, target_url: str):
        res_dict = {"name": "",
                    "stock_quantity": 0,
                    "product_points": 99999,
                    "card_type": ""}
        try:
            r = self.sess.get(target_url)
            r.html.render(sleep=2, timeout=60)
            res_dict["name"] = r.html.find('div.product-detail-content-title', first=True).text
            btn = r.html.find('div.product-detail-content-btn > a.js-buy', first=True)
            res_dict["stock_quantity"] = btn
            res_dict["product_points"] = int(r.html.find('li.product-points > span', first=True).text)
            # 兑换卡种
            res_dict["card_type"] = r.html.find('li.card-type', first=True).text[6:]
        except (AttributeError, TimeoutError):
            pass
        return res_dict

    def messager(self, title: str, msg: str):
        self.sess.get("https://api.day.app/%s/%s/%s?url=wx2654d9155d70a468://" % (bark_key, title, msg,))


if __name__ == "__main__":
    # print(os.environ.get('PYPPETEER_DOWNLOAD_HOST'))
    logging.info('开始工作')
    bot = CgbMonitor()
    str1 = ''
    for product in products:
        info = {'stock_quantity': 0}
        if product['enable']:
            time_start = time.time()
            info = bot.parser(product['url'])
            print("{0}的运行时间为{1}s".format(product['name'], int(time.time() - time_start)))
        else:
            info['stock_quantity'] = -1
        if info['stock_quantity'] > product['threshold']:
            str1 += "、{0}".format(product['name'])
        # print("%s，剩余%s件" % (info['name'], info['stock_quantity']))
    if str1 is not '':
        bot.messager('建行库存更新', '{0}有货了'.format(str1[1:]))
    print('结束工作')

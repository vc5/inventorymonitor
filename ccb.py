import os
import json
import time

from requests_html import HTMLSession

products = list()
with open("config.json", 'r', encoding='UTF-8') as f:
    config = json.load(f)
    products = config['products']

bark_key = os.environ.get("BARK_KEY")


class CcbMonitor:

    def __init__(self):
        start_url = "http://jf.ccb.com/index.html"
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
        r = self.sess.get(target_url)
        r.html.render(sleep=2, timeout=100)
        try:
            res_dict["name"] = r.html.find('div.prd_top_info > p.prd_top_title', first=True).text
            res_dict["stock_quantity"] = int(r.html.find('#pint', first=True).text)
            res_dict["product_points"] = int(r.html.find('li.product-points > span', first=True).text)
            # 兑换卡种
            res_dict["card_type"] = r.html.find('li.card-type', first=True).text[6:]
        except AttributeError:
            pass
        return res_dict

    def messager(self, title: str, msg: str):
        self.sess.get("https://api.day.app/%s/%s/%s?url=wx2654d9155d70a468://" % (bark_key, title, msg,))


if __name__ == "__main__":
    # print(os.environ.get('PYPPETEER_DOWNLOAD_HOST'))
    print('开始工作')
    bot = CcbMonitor()
    str1 = ''
    for product in products:
        info = {'stock_quantity': 0}
        if product['enable']:
            print("{0}的开始时间为{1}".format(product['name'], time.time()))
            info = bot.parser(product['url'])
            print("{0}的结束时间为{1}".format(product['name'], time.time()))
        else:
            info['stock_quantity'] = -1
        if info['stock_quantity'] > product['threshold']:
            str1 += "、{0}".format(product['name'])
        # print("%s，剩余%s件" % (info['name'], info['stock_quantity']))
    if str1 is not '':
        bot.messager('建行库存更新', '{0}有货了'.format(str1[1:]))
    print('结束工作')

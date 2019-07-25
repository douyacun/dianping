import requests
from config import *
from log import getLogger
from util.http import send_http
from settings import API_SHOP_INFO, SHOP_INFO_HEADERS
from pkg.token_m import TokenM

logger = getLogger(__name__)


class ShopInfo:
    def __init__(self, shopId):
        self.shopId = shopId
        self.session = requests.session()
        self.url = API_SHOP_INFO.format(shopId)
        self.token = TokenM(shopId)
        self.homepage = ""
        self._fetched = False

    def start_request(self):
        headers = SHOP_INFO_HEADERS
        headers['Referer'] = "http://www.dianping.com/shop/{}".format(self.shopId)
        result = send_http(self.session,
                           'get',
                           self.url,
                           retries=MAX_RETRY,
                           headers=headers,
                           timeout=TIMEOUT,
                           _token=self.token.new(),
                           kind='SHOP',
                           )
        if result:
            response, _, _ = result
            self.homepage = response.json()
            self._fetched = True
            logger.info(f'成功获取店铺:{self.shopId} 详情.')


if __name__ == '__main__':
    s = ShopInfo(93600792)
    s.start_request()
    print(s.homepage)

# coding:utf-8
import json
import requests
import dianping
from settings import *
from config import *
from shop import Shop
from decorator import timer
from log import getLogger
from util.tools import from_pattern
from exception import NoTextFiled
from util.tools import get_sub_tag
from util.http import send_http
from bs4.element import Tag
import re

logger = getLogger(__name__)


def init_db(db):
    if db and not db.connected:
        db.connect()
    return db


def init_search_db(db):
    if db and not db.connected:
        db.connect()
        db.use_db(MongoDB['searchDB'])
    return db


def get_city_list(url, headers=HEADERS, proxy=None):
    result = send_http(requests.session(),
                       'get',
                       url,
                       retries=-1,
                       proxy=proxy,
                       headers=headers,
                       timeout=TIMEOUT,
                       kind='CITY_LIST',
                       )
    if result:
        text = result[0].text
        ul = get_sub_tag(text, 'city_list')
        if ul:
            with open(CITY_LIST_FILE_PATH, 'w') as f:
                res = {}
                lis = ul('li')
                for li in lis:
                    _as = li('a')
                    for a in _as:
                        res[a.text] = CITY_URL_PREFIX + a['href']
                f.write(json.dumps(res))
            return res


def get_city_areacode(cityId=None, cityName=None):
    active_cities = dianping.DianPing().active_cities
    for city in active_cities:
        if cityId and str(cityId) == str(city['cityId']):
            return city['cityAreaCode']
        if cityName and city['cityName'].startswith(cityName):
            return city['cityAreaCode']
    logger.debug(f'未找到 Name:{cityName} ID:{cityId} 城市区号.')
    return ''


@timer
def get_city_shop_info(shopId, cityId, proxy, headers):
    shop = Shop(shopId)
    shop.get(proxy=proxy, headers=headers)
    if not shop._fetched:
        return
    data = {
        # '地址': shop.address,
        'reviews': shop.reviews,  # 点评数
        'review_tags': shop.review_tags,  # 点评标签
        'phoneNumber': get_full_phone(shop.phone, cityId),  # 电话
        'comment_kinds': shop.comment_kinds,  # 点评类别
        'scores': shop.scores  # 评分
    }
    return data, shop.proxy, shop.headers


def get_full_phone(phone, cityId):
    if not phone:
        return
    # res = []
    # _phone = [i.strip() for i in phone_str.split('\xa0') if i]
    # for i in _phone:
    #     if from_pattern(PATTERN_PHONE, i):
    #         res.append(i)
    #     else:
    #         code = get_city_areacode(cityId)
    #         res.append('-'.join([code, i]))
    # return res
    tags = {
        "gk50z": '0',
        "gk9nf": '2',
        "gkq2w": '3',
        "gkv3i": '4',
        "gksqi": '5',
        "gkssm": '6',
        "gk44o": '7',
        "gk3i3": '8',
        "gkgpj": '9',
    }
    phone_str = ''
    phone: list
    for k in phone:
        if isinstance(k, Tag):
            if k.name == 'cc':
                phone_str += tags[k['class'][0]]
        elif isinstance(k, str):
            phone_str += k
    m = re.search(r"(\d+)", phone_str)
    if m is not None:
        return m.group(1)
    else:
        return ''


def post_data(cityId, cityName, keyword, page, shopType, categoryId, regionId, mode, sortId, filterId):
    data = {
        "cityId": cityId,
        "cityEnName": cityName,
        "promoId": "0",
        "shopType": shopType,
        "categoryId": categoryId,
        "regionId": regionId,
        "sortMode": mode,
        "shopSortItem": sortId,
        "keyword": keyword,
        "searchType": "2",
        "branchGroupId": "0",
        "aroundShopId": "0",
        "shippingTypeFilterValue": filterId,
        "page": str(page)
    }
    return data


def transfer_data(item, locations):
    regions = [find_region_by_id(i, locations) for i in item.get('regionList', [])]
    data = {
        'shopName': item.get('shopName'),  # 店名
        'shopPowerTitle': item.get('shopPowerTitle'),  # 星级
        'addDate': item.get('addDate'),  # 注册时间
        'address': item.get('address'),  # 地址
        'avgPrice': item.get('avgPrice'),  # 人均
        'bookingSetting': item.get('bookingSetting'),  # 预定
        'branchUrl': HOST + item.get('branchUrl'),  # 分店url
        'defaultPic': item.get('defaultPic'),  # 商铺图片
        'dishTag': item.get('dishTag'),  # 商铺标签
        'geoLat': item.get('geoLat'),  # 经度
        'geoLng': item.get('geoLng'),  # 纬度
        'phoneNo': item.get('phoneNo'),  # 电话号
        'shopId': item.get('shopId'),  # 店铺id
        'memberCardId': item.get('memberCardId'),  # 会员卡ID
        'regions': regions,  # 地区
        'regionList': item.get('regionList'),
        'expand': item.get('expand'),
        'poi': item.get('poi'),
        'promoId': item.get('promoId'),
        'shopDealId': item.get('shopDealId'),
        'shopPower': item.get('shopPower'),
        'hasSceneryOrder': item.get('hasSceneryOrder'),
    }
    return data


def find_id(key, key_dict_list):
    def get_id(key, key_dict_list, parent=None):
        p = c = None
        if key is None:
            return '0', '0'
        for item in key_dict_list:
            if item['text'] == key:
                _res = item['value']
                if not parent:
                    return _res, _res
            if item.get('children'):
                pid = item['value']
                _, c = get_id(key, item['children'])
                if c:
                    return pid, c
        return p, c

    _id = get_id(key, key_dict_list)
    if _id == (None, None):
        raise NoTextFiled(f'未找到 "{key}" 相关字段.')
    return _id


def find_sort_value(key, category_id, sort_dict):
    if category_id in sort_dict:
        if not key:
            return '2', '0'
        item = sort_dict[category_id]
        for i in item:
            if i['text'] == key:
                return i['mode'], i['sort']
    raise NoTextFiled(f'未找到 "{key}" 排序项.')


def find_filter_value(key):
    value = SEARCH_MAP_FILTERS.get(key)
    return value if value else '0'


def find_region_by_id(id, key_dict_list):
    for item in key_dict_list:
        if item['value'] == str(id):
            return item['text']
        elif item.get('children') != None:
            res = find_region_by_id(id, item.get('children'))
            if res:
                return res


def find_children_regions(id, key_dict_list, first=True):
    found = False
    for item in key_dict_list:
        if item['value'] == str(id):
            found = True
            if item.get('children'):
                return [i['value'] for i in item['children']]
            else:
                return False
        elif item.get('children'):
            res = find_children_regions(id, item.get('children'), False)
            if not res is None:
                return res
    if not found and first:
        return [i['value'] for i in key_dict_list if i['value'] != 0]

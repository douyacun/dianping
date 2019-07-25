import base64, zlib, time, random


class TokenM:
    def __init__(self, shopId):
        self.shopId = shopId

    def new(self):
        ts = int(time.time() * 1000)
        # 时间戳 *1000-600
        cts = int(time.time() * 1000) + random.randint(100, 300)
        ip = "http://www.dianping.com/shop/{}".format(self.shopId)
        tokens = str({
            "rId": 100041,
            "ver": "1.0.6",
            "ts": ts,
            "cts": cts,
            "brVD": [1920, 186],
            "brR": [[1920, 1080], [1920, 1040], 24, 24],
            "bI": [ip, ""],
            "mT": ["{},{}".format(random.randint(100, 1600), random.randint(100, 900))],
            "kT": [],
            "aT": [],
            "tT": [],
            "aM": "",
            "sign": self.gen_sign()
        }).encode()
        return self.encode(tokens)

    def encode(self, _s):
        return base64.b64encode(zlib.compress(_s)).decode()

    def decode(self, _token):
        bb = base64.b64decode(_token)
        return zlib.decompress(bb).decode()

    def gen_sign(self):
        return self.encode(_s="shopId={}".format(self.shopId).encode())


if __name__ == '__main__':
    T = TokenM(93600792)
    # a = {"rId": 100041, "ver": "1.0.6", "ts": 1563985654214, "cts": 1563985654476, "brVD": [1920, 330],
    #  "brR": [[1920, 1080], [1920, 1057], 24, 24], "bI": ["http://www.dianping.com/shop/93600792", ""], "mT": [],
    #  "kT": [], "aT": [], "tT": [], "aM": "", "sign": "eJxTKs7IL/BMsbU0NjMwMLc0UgIALqcEjQ=="}
    # _token = T.gen_sign()
    # _token = 'eJxVj09rwkAQxb/LnJfsbLJ/sgEPih6iSaFFe5EcYpQYxSRmQyNIv3tnaT0UBt6b38yDmScM6RESgYhSMPg6DZCACDDQwGB0NFE6skZapaRWDKr/zMQUOgyfS0j2wobIlDSFJx8EfonAGAv28hH5UFL5rZSW4DyOfcL5NE3BsSnbvmnroOpu3J27nttIIxob0jFAidvWJ4QUETPaeHL1hLT80/HV5/QHpVxTt+RO68d240ya8UXuDjt8u+RTnlW4q9N5dq9Wl/fZDL5/AGScRmg='
    # print(_token)
    print(T.new())
    # print(T.new())

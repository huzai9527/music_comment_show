from Crypto.Cipher import AES
import base64
import requests


def AES_encrypt(text, key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, "0102030405060708")
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


def getRawJson(id, offset, limit):
    f_key = "0CoJUm6Qyw8W8jud"
    text = "{\"rid\":\""+id+"\",\"offset\":\""+offset+"\",\"total\":\"true\",\"limit\":\""+limit+"\",\"csrf_token\":\"\"}"
    rs = AES_encrypt(text, f_key)
    params = AES_encrypt(str(rs)[2:-1], "FwtEYduOXlNEHbLP")
    encSecKey = "81e7a41af9830200d5606be1a632e57eb0006b3cdae579127115c6323d4c4802f3af9efcee21d9f4126dde266773cbd795f19ae44028f9f8d038cd62d2816952fa99bb61ecb5fba87d5b178ff4b982ee34c7491808f7cb774554a0235a210caf2e5e867a0e2ebdf6f994be1b198ab43b14ce1f7cfa6f80b9070dea5fc5d6c712"
    data = {
        'params': params,
        'encSecKey': encSecKey
    }
    headers = {
         'Accept-Language':"zh-CN,zh;q=0.9,en;q=0.8",
         'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',

         'Cookie': 'appver=1.5.0.75771',
         'Referer': 'http://music.163.com/'
    }
    url = "https://music.163.com/weapi/v1/resource/comments/"+id+"?csrf_token="
    return requests.post(url,headers=headers, data=data).json()

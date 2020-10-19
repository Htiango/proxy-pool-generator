import os
from random import choice
import requests
from bs4 import BeautifulSoup
import time
import json


POOL_SIZE = 10
UPDATE_INTERVAL_SEC = 900
JSON_OUTPUT_PATH = "proxy_pools.json"


def timeit(method):
    """
    decorator function to calculate the time
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        time_ms = "{:.2f}ms".format((te - ts) * 1000)
        print("Time finishing {}: {}".format(method, time_ms))
        return result
    return timed


def test():
    start = time.time()
    response = requests.get('https://www.google.com')
    print("Finished in {}".format(time.time()-start))
    return response


def proxy_generator(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    proxy_ls = [{"https": value} for value in list(map(lambda x:x[0]+':'+x[1], 
        list(zip(map(lambda x:x.text, soup.findAll('td')[::8]),
            map(lambda x:x.text, soup.findAll('td')[1::8])))))]
    return proxy_ls

@timeit
def get_proxys(url_ip, url_test):
    proxy_ls = proxy_generator(url_ip)
    proxy_valid_set = set()
    for proxy in  proxy_ls:
        print("Trying proxy: {}".format(proxy))
        try:
            response = requests.request("get", url_test, proxies=proxy, timeout=7)
            response_code = response.status_code
            if response_code == 200:
                print("Succeed!!!!!!!!")
                proxy_str = "http://" + proxy["https"]
                proxy_valid_set.add(proxy_str)
            else:
                print("Response in error code: {}".format(response_code))
        except Exception as e:
            print(e)
    return list(proxy_valid_set)


def update_json(data, path=JSON_OUTPUT_PATH):
    with open(path, 'w') as f:
        json.dump(data, f)


with open('urls.json', 'r') as f:
    config = json.load(f)
url_ip = config["url_ip"]

url_test = config["url_test"]

while True:
    pools = get_proxys(url_ip, url_test)
    print(pools)
    update_json(pools)
    print("finish!")
    print("Sleep for {} seconds".format(UPDATE_INTERVAL_SEC))
    time.sleep(UPDATE_INTERVAL_SEC)



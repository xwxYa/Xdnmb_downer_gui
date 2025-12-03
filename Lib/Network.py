import requests
from .log import Log
import ssl
ssl.HAS_SNI = False
requests.packages.urllib3.disable_warnings()

dfheader = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39",
    "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"''',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "dnt": "1",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "utf-8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
}


def get_qs(qs, key):
    try:
        id = qs[key]
    except KeyError:
        return False
    else:
        return id


class Network():
    def __init__(self, hostTips: dict, log_path=".log", log_level=20, proxies={"http": None, "https": None},
                 timeout=30, max_retries=3) -> None:
        '''
        hostTips = {
            "office.com": {
                "ip": "0.0.0.0"
            },
            "office.com": {
                "ip": False
            }
        }
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
        '''

        self.LOG = Log("Network", log_level=log_level, log_path=log_path)

        self.s = requests.session()
        self.s.trust_env = False
        self.s.keep_alive = False
        self.table = hostTips
        self.timeout = timeout
        self.max_retries = max_retries

    def get(self, url, headers=False, noDefaultHeader=False, changeDefaultHeader=False, verify=False, **kwargs):
        h = Header.headerchange(headers, noDefaultHeader, changeDefaultHeader)
        domain = url.split("/")[2]
        conf = get_qs(self.table, domain)
        if conf != False:
            ip = get_qs(conf, "ip")
            if ip:
                url = url.replace(domain, ip)
                h["host"] = domain

        # 设置默认超时，如果用户没有指定
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        # 重试机制
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                r = self.s.get(url, headers=h, verify=False, **kwargs)
                self.LOG.info(f"[GET][INFO]\t\t{r.status_code}\t{r.url}\t{domain}")
                try:
                    self.LOG.debug(
                        f"[GET][DEBUG]\t\t{h}\n"+"\t"*11 + f"{r.headers}\n" + "\t"*11 + f"{r.text}")
                except Exception:
                    pass
                return r
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    import time
                    wait_time = (attempt + 1) * 1  # 递增等待时间: 1s, 2s, 3s...
                    self.LOG.warning(f"[GET][RETRY {attempt + 1}/{self.max_retries}]\t\t{url}\t{domain}\t{e.args}\t等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.LOG.error(f"[GET][ERROR]\t\t{url}\t{domain}\t{e.args}\t已重试{self.max_retries}次")

        # 所有重试都失败
        raise Exception(last_exception.args)

    def post(self, url, data=False, json={}, headers=False, noDefaultHeader=False, changeDefaultHeader=False, verify=False, **kwargs):
        h = Header.headerchange(headers, noDefaultHeader, changeDefaultHeader)
        domain = url.split("/")[2]
        conf = get_qs(self.table, domain)
        if conf != False:
            ip = get_qs(conf, "ip")
            if ip:
                url = url.replace(domain, ip)
                h["host"] = domain

        # 设置默认超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        # 重试机制
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                if data == False:
                    r = self.s.post(url, json=json, headers=h, verify=False, **kwargs)
                    request_data = json
                else:
                    r = self.s.post(url, data=data, headers=h, verify=False, **kwargs)
                    request_data = data

                self.LOG.info(f"[POST][INFO]\t\t{r.status_code}\t{r.url}\t{domain}")
                try:
                    self.LOG.debug(
                        f"[POST][DEBUG]\t\t{h}\n"+"\t"*11 + f"{r.headers}\n" + "\t"*11 + f"{request_data}\n" + "\t"*11 + f"{r.text}")
                except Exception:
                    pass
                return r
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    import time
                    wait_time = (attempt + 1) * 1
                    self.LOG.warning(f"[POST][RETRY {attempt + 1}/{self.max_retries}]\t\t{url}\t{domain}\t{e.args}\t等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.LOG.error(f"[POST][ERROR]\t\t{url}\t{domain}\t{e.args}\t已重试{self.max_retries}次")

        # 所有重试都失败
        raise Exception(last_exception.args)

    def put(self, url, data=False, json={}, headers=False, noDefaultHeader=False, changeDefaultHeader=False, verify=False, **kwargs):
        h = Header.headerchange(headers, noDefaultHeader, changeDefaultHeader)
        domain = url.split("/")[2]
        conf = get_qs(self.table, domain)
        if conf != False:
            ip = get_qs(conf, "ip")
            if ip:
                url = url.replace(domain, ip)
                h["host"] = domain
        try:
            if data == False:
                r = self.s.put(url, json=json, headers=h,
                                verify=False, **kwargs)
                data = json
            else:
                r = self.s.put(url, data=data, headers=h,
                                verify=False, **kwargs)
        except Exception as e:
            self.LOG.error(f"[POST][ERROR]\t\t{url}\t{domain}\t{e.args}")
            raise Exception(e.args)
        self.LOG.info(f"[POST][INFO]\t\t{r.status_code}\t{r.url}\t{domain}")
        try:
            self.LOG.debug(
                f"[POST][DEBUG]\t\t{h}\n"+"\t"*11 + f"{r.headers}\n" + "\t"*11 + f"{data}\n" + "\t"*11 + f"{r.text}")
        except Exception:
            pass
        return r

    def changeHeader(self, header, noDefaultHeader=False):
        return Header.headerchange(header, noDefaultHeader, changeDefaultHeader=True)


class Header():
    @staticmethod
    def headerchange(header, noDefaultHeader=False, changeDefaultHeader=False):
        global dfheader
        if header:
            if noDefaultHeader:
                h = header
            else:
                h = Header.addheader(dfheader, header)
        else:
            h = dfheader.copy()
        if changeDefaultHeader:
            dfheader = h.copy()
        return h

    @staticmethod
    def addheader(d1: dict, d2: dict):
        d = d2.copy()
        for i in d1:
            d[i] = d1[i]
        return d

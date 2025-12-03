from Lib.Network import Network
import os
import json


class XdnmbException(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Xdnmb():
    def __init__(self, cookie, s: Network = Network({})) -> None:
        self.s = s
        self.s.changeHeader({"cookie": cookie})

    def po(self, id, page):
        url = f"https://api.nmb.best/Api/po/id/{id}/page/{page}"
        r = self.s.get(url).json()
        self.success(r)
        return self.remove_tips(r)

    def all(self, id, page):
        url = f"https://api.nmb.best/Api/thread/id/{id}/page/{page}"
        r = self.s.get(url).json()
        self.success(r)
        return self.remove_tips(r)

    def subscribe(self, uuid):
        def single(page):
            url = f"https://api.nmb.best/Api/feed/uuid/{uuid}/page/{page}"
            r = self.s.get(url).json()
            self.success(r)
            return r
        fin = []
        i = 1
        t = single(i)
        c = self.cache("subscribe")
        if c:
            if c[0]["id"] == t[0]["id"]:
                return c
        while t != []:
            fin += t
            i += 1
            t = single(i)
        self.cache("subscribe", fin)
        return fin

    def get_by_id(self, id):
        url = f"https://api.nmb.best/Api/ref/id/{id}"
        r = self.s.get(url).json()
        self.success(r)
        return r

    def get_all(self, id, handle, p=1, fin=None):
        if fin is None:
            fin = []
        try:
            r = handle(id, p)
            fin.append(r)
            p += 1
            while len(r["Replies"]) != 0:
                r = handle(id, p)
                fin.append(r)
                p += 1
        except Exception as e:
            self.err = self.transform(fin)
            raise Exception(e.args)
        return fin

    def get_with_cache(self, id, handle):
        cache_key = f"{id}_{handle.__name__}"
        c = self.cache(cache_key)
        if c:
            fin = self.get_all(id, handle, p=len(c)+1, fin=c)
            return self.transform(fin)
        else:
            fin = self.get_all(id, handle)
            self.cache(cache_key, fin[:-2])
            return self.transform(fin)

    @staticmethod
    def success(r):
        # 检查响应中是否包含错误信息
        if "success" in r and r["success"] == False:
            error_msg = r.get("error", "未知错误")
            if error_msg == "该串不存在":
                raise XdnmbException("虚空下载不可取,该串不存在,再给你一次机会")
            elif error_msg == "必须登入领取饼干后才可以访问":
                raise XdnmbException("饼干呢?你这饼干假的吧,必须登入领取饼干后才可以访问,再给你一次机会")
            else:
                raise XdnmbException(f"很神秘,是不知道的错误呢:{error_msg}")
        return r

    @staticmethod
    def transform(fin):
        f = fin[0]
        i = 1
        while i < len(fin):
            f["Replies"] += fin[i]["Replies"]
            i += 1
        return f

    @staticmethod
    def remove_tips(fin):
        # 过滤掉广告回复（ID为9999999）
        # 使用列表推导式，避免在遍历时删除元素的问题
        AD_REPLY_ID = 9999999
        fin["Replies"] = [reply for reply in fin["Replies"] if reply["id"] != AD_REPLY_ID]
        return fin

    @staticmethod
    def cache(id, fin=None):
        # Ensure .log folder exists
        if not os.path.exists(".log"):
            os.makedirs(".log")

        path = os.path.join(".log", f"{id}.json")

        # 读取缓存
        if fin is None:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    c = json.load(f)
                return c
            except FileNotFoundError:
                print("[INFO]:未检测到缓存")
                return False
            except json.JSONDecodeError:
                print("[WARNING]:缓存文件损坏，将被忽略")
                return False
            except Exception as e:
                print(f"[ERROR]:读取缓存失败: {e}")
                return False
        # 写入缓存
        else:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(fin, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[ERROR]:写入缓存失败: {e}")

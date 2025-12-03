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
        """获取订阅列表（原始方法，保持向后兼容）"""
        def single(page):
            url = f"https://api.nmb.best/Api/feed/uuid/{uuid}/page/{page}"
            r = self.s.get(url).json()
            self.success(r)
            return r
        fin = []
        i = 1
        t = single(i)
        c = self.cache("subscribe")

        # 如果第一页就是空的，直接返回空列表
        if not t:
            return []

        # 检查缓存
        if c and len(c) > 0:
            if c[0]["id"] == t[0]["id"]:
                return c

        while t != []:
            fin += t
            i += 1
            t = single(i)
        self.cache("subscribe", fin)
        return fin

    def get_subscribe_list(self, uuid):
        """
        获取订阅列表的详细信息（用于GUI显示）
        返回格式化的订阅串列表

        Returns:
            list: [
                {
                    'id': 串ID,
                    'title': 标题,
                    'content': 内容,
                    'content_preview': 内容预览（前100字），
                    'img': 图片,
                    'ext': 图片扩展名,
                    'time': 时间
                },
                ...
            ]
        """
        import re
        raw_list = self.subscribe(uuid)
        formatted_list = []

        for item in raw_list:
            # 提取并格式化关键信息
            formatted = {
                'id': item.get('id', 0),
                'title': item.get('title', '无标题'),
                'content': item.get('content', ''),
                'img': item.get('img', ''),
                'ext': item.get('ext', ''),
            }

            # 生成内容预览（移除HTML标签，取前100字）
            content_clean = re.sub(r'<br\s*/?>', ' ', formatted['content'], flags=re.IGNORECASE)
            content_clean = re.sub(r'<[^>]+>', '', content_clean)
            content_clean = content_clean.strip()
            formatted['content_preview'] = content_clean[:100] + ('...' if len(content_clean) > 100 else '')

            # 时间
            formatted['time'] = item.get('now', item.get('time', item.get('Time', '')))

            formatted_list.append(formatted)

        return formatted_list

    def add_feed(self, uuid, tid):
        """
        添加订阅

        Args:
            uuid: 用户订阅UUID
            tid: 串ID（整数）

        Raises:
            XdnmbException: 添加失败时抛出
        """
        import json
        url = f"https://api.nmb.best/api/addFeed?uuid={uuid}&tid={tid}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        r = self.s.post(url, headers=headers)
        if r.status_code == 200:
            response_text = r.text.strip()
            try:
                result = json.loads(response_text)
                if result == '订阅大成功→_→':
                    return True
                else:
                    raise XdnmbException(f"添加订阅失败: {response_text}")
            except json.JSONDecodeError:
                if response_text == '订阅大成功→_→':
                    return True
                else:
                    raise XdnmbException(f"添加订阅失败: {response_text}")
        else:
            raise XdnmbException(f"添加订阅失败，HTTP状态码: {r.status_code}")

    def del_feed(self, uuid, tid):
        """
        删除订阅

        Args:
            uuid: 用户订阅UUID
            tid: 串ID（整数）

        Raises:
            XdnmbException: 删除失败时抛出
        """
        import json
        url = f"https://api.nmb.best/api/delFeed?uuid={uuid}&tid={tid}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        r = self.s.post(url, headers=headers)
        if r.status_code == 200:
            response_text = r.text.strip()
            try:
                result = json.loads(response_text)
                if result == '取消订阅成功!':
                    return True
                else:
                    raise XdnmbException(f"删除订阅失败: {response_text}")
            except json.JSONDecodeError:
                if response_text == '取消订阅成功!':
                    return True
                else:
                    raise XdnmbException(f"删除订阅失败: {response_text}")
        else:
            raise XdnmbException(f"删除订阅失败，HTTP状态码: {r.status_code}")

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

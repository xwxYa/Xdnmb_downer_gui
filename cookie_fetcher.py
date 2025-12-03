"""
Cookie获取帮助模块
提供手动获取Cookie的指导信息
"""

class CookieFetcher:
    def __init__(self):
        pass

    def fetch_cookie_manual_guide(self):
        """
        返回手动获取Cookie的指南
        """
        guide = """
手动获取Cookie方法：

方法一：使用开发者工具Console（推荐，最简单）
1. 打开浏览器，访问 https://www.nmbxd1.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 "Console"（控制台）标签
4. 在底部输入以下命令并回车：
   document.cookie
5. 复制输出的完整内容
6. 粘贴到本程序的Cookie输入框，点击"保存"

方法二：使用开发者工具Application
1. 打开浏览器，访问 https://www.nmbxd1.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 "Application"（应用）或 "Storage"（存储）标签
4. 左侧选择 "Cookies" -> "https://www.nmbxd1.com"
5. 找到 PHPSESSID 和 userhash 的值
6. 按格式填入：PHPSESSID=xxxxx userhash=xxxxx

方法三：使用书签工具
1. 创建一个新书签，URL填入：
   javascript:(function(){let domain=document.domain;let cookie=document.cookie;prompt('Cookies: '+domain, cookie)})();
2. 访问 https://www.nmbxd1.com 并登录
3. 点击这个书签
4. 复制弹出的Cookie内容，粘贴到程序中

注意：
- 推荐使用方法一，最简单快捷
- Cookie可以直接复制整个字符串，程序会自动提取需要的字段
- Cookie有效期有限，过期后需要重新获取
"""
        return guide

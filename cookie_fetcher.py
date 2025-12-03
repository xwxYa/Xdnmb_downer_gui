"""
Cookie自动获取模块
使用Selenium自动打开浏览器，让用户登录后自动获取Cookie
"""
import time
import os

class CookieFetcher:
    def __init__(self):
        self.driver = None
        self.use_selenium = self._check_selenium()

    def _check_selenium(self):
        """检查是否安装了selenium"""
        try:
            import selenium
            return True
        except ImportError:
            return False

    def fetch_cookie_auto(self, callback=None):
        """
        自动打开浏览器获取Cookie
        callback: 回调函数，用于更新GUI状态
        """
        if not self.use_selenium:
            raise Exception("未安装selenium库，请运行: pip install selenium")

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Chrome选项
            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            if callback:
                callback("正在启动浏览器...")

            # 尝试使用不同的方式启动Chrome
            try:
                # 方式1：直接启动
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e1:
                try:
                    # 方式2：使用Edge（Windows系统通常都有）
                    if callback:
                        callback("Chrome启动失败，尝试使用Edge浏览器...")
                    from selenium.webdriver.edge.options import Options as EdgeOptions
                    edge_options = EdgeOptions()
                    edge_options.add_argument('--disable-blink-features=AutomationControlled')
                    self.driver = webdriver.Edge(options=edge_options)
                except Exception as e2:
                    # 方式3：使用Firefox
                    try:
                        if callback:
                            callback("Edge启动失败，尝试使用Firefox浏览器...")
                        self.driver = webdriver.Firefox()
                    except Exception as e3:
                        raise Exception(
                            f"无法启动浏览器。请确保已安装Chrome、Edge或Firefox浏览器。\n"
                            f"Chrome错误: {str(e1)}\n"
                            f"Edge错误: {str(e2)}\n"
                            f"Firefox错误: {str(e3)}"
                        )

            if callback:
                callback("浏览器已启动，正在打开X岛匿名版...")

            # 打开X岛匿名版
            self.driver.get("https://www.nmbxd1.com")

            if callback:
                callback("请在浏览器中完成登录操作...")
                callback("登录成功后，浏览器会自动关闭并获取Cookie")

            # 等待用户登录（检测Cookie是否包含必要字段）
            max_wait = 300  # 最多等待5分钟
            start_time = time.time()

            while time.time() - start_time < max_wait:
                cookies = self.driver.get_cookies()
                cookie_dict = {c['name']: c['value'] for c in cookies}

                # 检查是否已获取到必要的Cookie
                if 'userhash' in cookie_dict and 'PHPSESSID' in cookie_dict:
                    # 格式化Cookie
                    cookie_str = f"PHPSESSID={cookie_dict['PHPSESSID']} userhash={cookie_dict['userhash']}"

                    if callback:
                        callback("Cookie获取成功！")

                    self.driver.quit()
                    return cookie_str

                time.sleep(1)

            # 超时
            self.driver.quit()
            raise Exception("获取Cookie超时，请重试")

        except Exception as e:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            raise e

    def fetch_cookie_manual_guide(self):
        """
        返回手动获取Cookie的指南
        """
        guide = """
手动获取Cookie方法：

方法一：使用浏览器开发者工具
1. 打开Chrome浏览器，访问 https://www.nmbxd1.com
2. 按F12打开开发者工具
3. 切换到"Application"（应用）或"Storage"（存储）标签
4. 左侧选择"Cookies" -> "https://www.nmbxd1.com"
5. 找到 PHPSESSID 和 userhash 的值
6. 按格式填入：PHPSESSID=xxxxx userhash=xxxxx

方法二：使用书签工具
1. 创建一个新书签，URL填入：
   javascript:(function(){let domain=document.domain;let cookie=document.cookie;prompt('Cookies: '+domain, cookie)})();
2. 访问 https://www.nmbxd1.com 并登录
3. 点击这个书签
4. 复制弹出的Cookie内容，粘贴到程序中
"""
        return guide

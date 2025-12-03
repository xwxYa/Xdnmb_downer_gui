import os
import zipfile
from Lib.Network import Network


def mkdir(path):
    """创建目录，带异常处理"""
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except PermissionError:
            raise Exception(f"权限不足：无法创建目录 {path}")
        except OSError as e:
            raise Exception(f"创建目录失败 {path}: {e}")


def sanitize_folder_name(text, max_length=100):
    """
    清理文件夹名称，移除不合法字符

    :param text: 原始文本
    :param max_length: 最大长度
    :return: 清理后的文件夹名
    """
    import re

    # 1. 移除HTML标签
    clean_text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)

    # 2. 替换Windows/Linux不允许的文件名字符为下划线
    # 不允许的字符: / \ : * ? " < > |
    illegal_chars = r'[/\\:*?"<>|]'
    clean_text = re.sub(illegal_chars, '_', clean_text)

    # 3. 去除首尾空格和特殊字符
    clean_text = clean_text.strip('. ')  # 移除首尾的点和空格

    # 4. 压缩连续的空格为单个空格
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # 5. 限制长度
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length].strip()

    # 6. 如果清理后为空，使用默认名称
    if not clean_text:
        clean_text = "未命名文件夹"

    return clean_text


def ZIP_single(root_path, dir_path):
    '''
    root_path:文件夹根目录
    dir_path:文件夹内文件夹路径
    '''
    # 获取子目录的名称
    dir_name = os.path.basename(dir_path)
    zip_file_path = os.path.join(root_path, dir_name + ".epub")
    with zipfile.ZipFile(zip_file_path, "w", compression=zipfile.ZIP_STORED) as zipf:
        # 递归地添加子目录中的文件和文件夹到归档文件
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, dir_path)
                zipf.write(file_path, arcname=arc_name)


class Epub():
    def __init__(self, name, url) -> None:
        self.name = name
        self.url = url
        self.forder_init()
        self.list = []
        self.id = 1
        self.pics = []

    def forder_init(self):
        mkdir(".tmp")
        mkdir(f".tmp/{self.name}")
        mkdir(f".tmp/{self.name}/META-INF")
        with open(f".tmp/{self.name}/META-INF/container.xml", "w", encoding="utf-8") as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>''')
        with open(f".tmp/{self.name}/mimetype", "w", encoding="utf-8") as f:
            f.write('''application/epub+zip''')
        mkdir(f".tmp/{self.name}/OEBPS")
        mkdir(f".tmp/{self.name}/OEBPS/Images")
        mkdir(f".tmp/{self.name}/OEBPS/Styles")
        mkdir(f".tmp/{self.name}/OEBPS/Text")
        with open("cover.jpg","rb") as f:
            b = f.read()
        with open(f'.tmp/{self.name}/OEBPS/Images/cover.jpg',"wb") as f:
            f.write(b)

    def plugin(self, Net: Network):
        self.s = Net
    
    def download(self,url:list):
        fin = []
        for i in url:
            try:
                r = self.s.get(i)
                if r.status_code == 200:
                    with open(f'''.tmp/{self.name}/OEBPS/Images/{i.split("/")[-1]}''',"wb") as f:
                        f.write(r.content)
                    self.pics.append(i)
                    fin.append(i)
            except:
                print(f"[ERR]:\t{i}\t下载失败,是否将文件正常加入EPUB图片清单和插入章节Y/N")
                inputs = input('>')
                if inputs == "Y":
                    print(f'''[TIPS]:您需要手动下载该文件置于.tmp/{self.name}/OEBPS/Images/{i.split("/")[-1]}''')
                    self.pics.append(i)
                    fin.append(i)
        return fin

    def cover(self, text):
        with open(f".tmp/{self.name}/OEBPS/Text/cover.xhtml", "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>书籍封面</title>
</head>
<body>
<div style="text-align: center; padding: 0pt; margin: 0pt;">
<svg xmlns="http://www.w3.org/2000/svg" height="100%" preserveAspectRatio="xMidYMid meet" version="1.1" viewBox="0 0 179 248" width="100%" xmlns:xlink="http://www.w3.org/1999/xlink">
<image height="248" width="179" xlink:href="../Images/cover.jpg"></image>
</svg>
</div>
<h1>{self.name}</h1>
<h2>{self.url}</h2>
<h3>更新時間: 我不知道</h3>
<h3>簡介:</h3>
''')
            o = text.replace("\n", "").split("<br />")
            for i in o:
                if i != "":
                    f.write(f"<p>　　{i}</p>\n")
            f.write("</body>\n</html>\n")
        self.list.append({
            "id": "cover",
            "url": "Text/cover.xhtml",
            "title": "书籍封面"
        })

    def add_text(self, text, title, pics=[]):
        pics = self.download(pics)
        o = text.replace("\n", "").split("<br />")
        with open(f".tmp/{self.name}/OEBPS/Text/{self.id:06d}.xhtml", "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>{title}</title>
</head>
<body>
<h3>{title}</h3>\n''')
            for i in o:
                if i != "":
                    f.write(f"<p>　　{i}</p>\n")
            for i in pics:
                f.write(
                    f'''<p>　　<img src="../Images/{i.split("/")[-1]}" alt=""/></p>\n''')
            f.write("</body></html>")
        self.list.append({
            "id": f"{self.id:06d}",
            "url": f"Text/{self.id:06d}.xhtml",
            "title": title
        })
        self.id += 1

    def finish(self):
        with open(f".tmp/{self.name}/OEBPS/toc.ncx", "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
 "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
<meta content="hbooker:100012892" name="dtb:uid"/>
<meta content="2" name="dtb:depth"/>
<meta content="0" name="dtb:totalPageCount"/>
<meta content="0" name="dtb:maxPageNumber"/>
</head>
<docTitle>
<text>{self.name}</text>
</docTitle>
<docAuthor>
<text>{self.url}</text>
</docAuthor>
<navMap>\n''')
            i = 1
            while i <= len(self.list):
                f.write(
                    f'''<navPoint id="{self.list[i-1]["id"]}" playOrder="{i}"><navLabel><text>{self.list[i-1]["title"]}</text></navLabel><content src="{self.list[i-1]["url"]}" /></navPoint>\n''')
                i += 1
            f.write("</navMap>\n</ncx>\n")
        with open(f".tmp/{self.name}/OEBPS/content.opf", "w", encoding="utf-8") as f:
            f.write(f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
<dc:identifier id="BookId">{self.url}</dc:identifier>
<dc:title>{self.name}</dc:title>
<dc:creator opf:role="aut">{self.url}</dc:creator>
<dc:language>zh-CN</dc:language>
<dc:publisher></dc:publisher>
</metadata>
<manifest>
<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml" />
<item href="Images/cover.jpg" id="cover.jpg" media-type="image/jpeg" />
''')
#可以在此处</metadata>之前加入<meta name="cover" content="cover.jpg"/>,加入后QQ的epub插件会出现异常，移除后正常，但封面章节内的文字依旧不显示
            for i in self.list:
                f.write(
                    f'''<item href="{i["url"]}" id="{i["url"].replace("Text/", "")}" media-type="application/xhtml+xml" />\n''')
            for i in self.pics:
                f.write(
                    f'''<item href="Images/{i.split("/")[-1]}" id="{i.split("/")[-1]}" media-type="image/jpeg" />\n''')
            f.write('''</manifest>\n<spine toc="ncx">\n''')
            for i in self.list:
                f.write(
                    '''<itemref idref="{}" />\n'''.format(i["url"].replace("Text/", "")))
            f.write(
                '''</spine>\n<guide>\n<reference href="Text/cover.xhtml" title="书籍封面" type="cover" />\n</guide>\n</package>''')
        ZIP_single(".tmp", os.path.join(".tmp", self.name))

class TXT():
    def __init__(self,name) -> None:
        mkdir(".tmp")
        self.f = open(f".tmp/{name}.txt","w",encoding="utf-8")
    
    def add(self,text):
        self.f.write(text.replace("<br />",""))
        self.f.write("\n")

    def __del__(self):
        if hasattr(self, 'f'):
            self.f.close()

class Markdown():
    def __init__(self, name, url, mode='online', path_type='relative') -> None:
        """
        初始化Markdown导出器
        :param name: 文件名
        :param url: 来源URL
        :param mode: 'online' 使用在线图片URL，'local' 下载图片到本地
        :param path_type: 'relative' 使用相对路径，'absolute' 使用绝对路径（仅在mode='local'时有效）
        """
        try:
            mkdir(".tmp")
        except Exception as e:
            raise Exception(f"无法创建输出目录：{e}")

        self.name = name
        self.url = url
        self.mode = mode
        self.path_type = path_type
        self.s = None

        # 创建文件和文件夹
        if mode == 'local':
            # 本地模式：创建图片文件夹
            self.img_dir = f".tmp/{self.name}_files"
            try:
                mkdir(self.img_dir)
                mkdir(f"{self.img_dir}/images")
            except Exception as e:
                raise Exception(f"无法创建图片目录：{e}")

        # 创建markdown文件
        try:
            self.f = open(f".tmp/{self.name}.md", "w", encoding="utf-8")
        except PermissionError:
            raise Exception(f"权限不足：无法创建文件 .tmp/{self.name}.md")
        except Exception as e:
            raise Exception(f"创建Markdown文件失败：{e}")

    def plugin(self, Net: Network):
        """注入Network对象用于下载图片"""
        self.s = Net

    def download_images_batch(self, urls, max_workers=5):
        """
        并发下载多张图片
        :param urls: 图片URL列表
        :param max_workers: 最大并发数
        :return: {url: local_path} 字典
        """
        if not urls:
            return {}

        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = {}

        print(f"[INFO] 开始并发下载 {len(urls)} 张图片（最大并发数：{max_workers}）")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有下载任务
            future_to_url = {executor.submit(self.download_image, url): url for url in urls}

            # 等待完成并收集结果
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    local_path = future.result()
                    results[url] = local_path
                except Exception as e:
                    print(f"[错误] 下载图片时发生异常: {url}, {e}")
                    results[url] = None

        success_count = sum(1 for path in results.values() if path is not None)
        print(f"[INFO] 图片下载完成：成功 {success_count}/{len(urls)} 张")

        return results

    def download_image(self, url, retry=3):
        """
        下载图片到本地，支持重试
        :param url: 图片URL
        :param retry: 重试次数
        :return: 本地路径（相对或绝对）或None
        """
        if not self.s:
            print(f"[警告] 未设置Network对象，无法下载图片: {url}")
            return None

        for attempt in range(retry):
            try:
                r = self.s.get(url, timeout=10)
                if r.status_code == 200:
                    filename = url.split("/")[-1]
                    local_path = f"{self.img_dir}/images/{filename}"

                    # 写入文件，带异常处理
                    try:
                        with open(local_path, "wb") as f:
                            f.write(r.content)
                    except PermissionError:
                        print(f"[错误] 权限不足，无法写入图片: {local_path}")
                        return None
                    except OSError as e:
                        print(f"[错误] 写入图片失败: {local_path}, 错误: {e}")
                        return None

                    # 验证文件是否真的写入
                    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                        print(f"[成功] 图片已下载: {filename} ({len(r.content)} bytes)")

                        # 根据 path_type 返回相对路径或绝对路径
                        if self.path_type == 'absolute':
                            return os.path.abspath(local_path)
                        else:
                            return f"./{self.name}_files/images/{filename}"
                    else:
                        print(f"[警告] 图片文件写入失败: {filename}")
                else:
                    print(f"[错误] 下载图片失败 (状态码 {r.status_code}): {url}")
            except Exception as e:
                if attempt < retry - 1:
                    print(f"[重试 {attempt + 1}/{retry}] 下载图片失败: {url}, 错误: {e}")
                    import time
                    time.sleep(1)  # 等待1秒后重试
                else:
                    print(f"[错误] 下载图片失败（已重试{retry}次）: {url}, 错误: {e}")

        return None

    def format_text(self, text):
        """
        格式化文本，将HTML的<br />转换为Markdown换行
        :param text: 原始文本
        :return: 格式化后的文本
        """
        # 替换<br />为两个换行（Markdown段落分隔）
        formatted = text.replace("<br />", "\n\n")
        # 移除可能的空行
        lines = [line.strip() for line in formatted.split("\n") if line.strip()]
        return "\n\n".join(lines)

    def add_cover(self, text):
        """
        添加封面信息（标题、来源、简介）
        :param text: 简介内容
        """
        # 写入标题
        self.f.write(f"# {self.name}\n\n")

        # 写入来源信息
        self.f.write(f"**来源**: [{self.url}]({self.url})\n\n")

        # 写入简介
        self.f.write(f"## 简介\n\n")
        formatted_text = self.format_text(text)
        self.f.write(f"{formatted_text}\n\n")

        # 添加分隔线
        self.f.write("---\n\n")

    def add_text(self, text, title, pics=[]):
        """
        添加章节内容
        :param text: 章节文本
        :param title: 章节标题
        :param pics: 图片URL列表
        """
        # 写入章节标题
        self.f.write(f"## {title}\n\n")

        # 写入文本内容
        formatted_text = self.format_text(text)
        self.f.write(f"{formatted_text}\n\n")

        # 处理图片
        if pics:
            for pic_url in pics:
                if self.mode == 'local':
                    # 本地模式：下载图片并使用相对路径
                    local_path = self.download_image(pic_url)
                    if local_path:
                        self.f.write(f"![图片]({local_path})\n\n")
                    else:
                        # 下载失败，回退到在线URL
                        self.f.write(f"![图片]({pic_url})\n\n")
                else:
                    # 在线模式：直接使用URL
                    self.f.write(f"![图片]({pic_url})\n\n")

        # 添加分隔线
        self.f.write("---\n\n")

    def finish(self):
        """完成并关闭文件"""
        # 添加版权信息
        self.f.write("\n\n---\n\n")
        self.f.write(f"*本文档由 Xdnmb_downer 生成*\n\n")
        self.f.write(f"*来源: {self.url}*\n\n")
        self.f.write(f"*版权归属原作者及X岛匿名版所有，请在24小时内删除*\n")
        self.f.close()
        print(f"[完成] Markdown文件已生成: .tmp/{self.name}.md")
        if self.mode == 'local':
            print(f"[完成] 图片文件夹: {self.img_dir}/images/")

    def __del__(self):
        if hasattr(self, 'f') and not self.f.closed:
            self.f.close()

if __name__ == '__main__':
    e = Epub("test", "adw")
    e.cover("ABABA")
    n = Network({})
    e.plugin(n)
    e.add_text("aaa", "wuti", [
               "https://image.nmb.best/image/2022-09-13/6320726e73bd9.jpg"])

    e.finish()

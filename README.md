# Xdnmb_downer_gui
X岛匿名版的下载工具（GUI版）

### 请勿用于违法用途，工具仅供学习交流使用，所下载及生成的文件版权属于X岛匿名版与原作者所有，请在24小时内删除

本意用于打包缓存小说版的文章，顺便提供更好的阅读体验

生成后的TXT与Epub均位于.tmp文件夹内

## 安装依赖

```bash
pip install -r requirements.txt
```

**注意**：只需要安装 `requests` 库，无其他依赖

## 快速开始

### GUI版本（推荐）

**启动程序**：
- Windows：双击 `run_gui.bat` 或运行 `python gui.py`
- Linux/Mac：执行 `bash run_gui.sh` 或 `python3 gui.py`

**使用步骤**：
1. 点击"打开X岛"按钮，在浏览器中登录（如已登录可跳过）
2. 按F12打开开发者工具，在Console（控制台）输入 `document.cookie` 并回车
3. 复制输出的Cookie，粘贴到程序的Cookie输入框，点击"保存"
4. 输入串ID（如：51340998）
5. 选择下载模式（所有回复/只下载PO的回复）
6. 选择输出格式（EPUB/TXT）
7. 可选：设置自定义标题和内容过滤
8. 点击"开始下载"，文件保存在`.tmp`文件夹

**功能特点**：
- 简单易用：点击"打开X岛"按钮快速访问网站，点击"帮助"查看详细获取教程
- 智能内容过滤：三种过滤模式提升阅读体验
  - 自动过滤短回复（≤25字符且无图片）
  - 智能过滤无意义回复（fy、mark、jmjp等）
  - 手动审核模式（逐条确认）
  - 可视化词汇表管理
- 双下载模式：支持下载所有回复或只下载PO（楼主）的回复
- 增量更新：缓存机制支持串更新后只下载新回复
- 实时日志显示和过滤统计
- 支持EPUB和TXT格式，TXT格式自动添加回复分割线
- 多线程下载，界面流畅

### 命令行版本

`python run.py`

如果喜欢自定义可以自己修改main.py

`python main.py`

## Cookie获取说明

初次使用请先获取cookies，有以下几种方式：

### 方式一：使用开发者工具（推荐）
1. 打开浏览器访问 https://www.nmbxd1.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 "Console"（控制台）标签
4. 在底部输入 `document.cookie` 并回车
5. 复制输出的内容（以 PHPSESSID= 开头）
6. 粘贴到程序的Cookie输入框

### 方式二：使用书签工具
1. 创建书签，URL填入：
   ```javascript
   javascript:(function(){let domain=document.domain;let cookie=document.cookie;prompt('Cookies: '+domain, cookie)})();
   ```
2. 访问 https://www.nmbxd1.com 并登录
3. 点击书签，复制弹出的Cookie内容
4. 粘贴到程序的Cookie输入框

## 题外话

> 版权的代码我直接摆在你脸上了，反正公开的东西想搞事的谁也拦不住
>
> 不搞编译了，没用的东西.jpg

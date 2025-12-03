# Xdnmb_downer_gui
X岛匿名版的下载工具（GUI版）

### 请勿用于违法用途，工具仅供学习交流使用，所下载及生成的文件版权属于X岛匿名版与原作者所有，请在24小时内删除

本意用于打包缓存小说版的文章，顺便提供更好的阅读体验

生成后的TXT与Epub均位于.tmp文件夹内

## 安装依赖

```bash
pip install -r requirements.txt
```

**注意**：
- `selenium`库仅在使用GUI的"自动获取Cookie"功能时需要
- 如果只使用手动输入Cookie或命令行版本，可以不安装selenium
- GUI界面会在需要时提示安装selenium

## 快速开始

### GUI版本（推荐）

**启动程序**：
- Windows：双击 `run_gui.bat` 或运行 `python gui.py`
- Linux/Mac：执行 `bash run_gui.sh` 或 `python3 gui.py`

**使用步骤**：
1. 点击"自动获取"按钮，在打开的浏览器中登录（首次使用会自动安装selenium）
2. 登录成功后Cookie自动填入，点击"保存"
3. 输入串ID（如：51340998）
4. 选择输出格式和过滤选项
5. 点击"开始下载"，文件保存在`.tmp`文件夹

**功能特点**：
- 一键自动获取Cookie：自动打开浏览器登录，无需手动复制
- 智能内容过滤：三种过滤模式提升阅读体验
  - 自动过滤短回复（≤25字符且无图片）
  - 智能过滤无意义回复（fy、mark、jmjp等）
  - 手动审核模式（逐条确认）
  - 可视化词汇表管理
- 实时日志显示和过滤统计
- 支持EPUB和TXT格式
- 多线程下载，界面流畅

### 命令行版本：

`python run.py`

如果喜欢自定义可以自己修改main.py

`python main.py`

初次使用请先准备好cookies，如果你不知晓cookies是何物，可以按下方说明进行操作

俩种方式
1. 全选如下内容，直接拖到书签栏

`javascript:(function(){let domain=document.domain;let cookie=document.cookie;prompt('Cookies: '+domain, cookie)})();`

2. 打开匿名版，点击书签，直接复制框内内容填入程序`c + [你刚刚复制的内容]`

或者
1. PC浏览器，随便添加一个页面到书签
2. 右键该书签，进行编辑，将内容替换成`javascript:(function(){let domain=document.domain;let cookie=document.cookie;prompt('Cookies: '+domain, cookie)})();`即可
3. 打开匿名版，点击书签，直接复制框内内容填入程序`c + [你刚刚复制的内容]`

题外话：

> 版权的代码我直接摆在你脸上了，反正公开的东西想搞事的谁也拦不住
> 
>  不搞编译了，没用的东西.jpg


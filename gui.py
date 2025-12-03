import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
from io import StringIO
from Xdnmb import Xdnmb, XdnmbException
from Epub import Epub, TXT
from Lib.ini import CONF
from cookie_fetcher import CookieFetcher
from content_filter import ContentFilter

class XdnmbDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Xdnmb下载器 GUI版")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        self.conf = CONF("Xdnmb")
        self.is_downloading = False
        self.is_fetching_cookie = False
        self.cookie_fetcher = CookieFetcher()
        self.content_filter = ContentFilter()

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Cookie设置区域
        ttk.Label(main_frame, text="Cookie设置:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cookie_entry = ttk.Entry(main_frame, width=50)
        self.cookie_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Cookie按钮框架
        cookie_btn_frame = ttk.Frame(main_frame)
        cookie_btn_frame.grid(row=0, column=2, padx=5, pady=5)

        self.auto_fetch_btn = ttk.Button(cookie_btn_frame, text="自动获取", command=self.auto_fetch_cookie)
        self.auto_fetch_btn.grid(row=0, column=0, padx=2)

        ttk.Button(cookie_btn_frame, text="保存", command=self.save_cookie).grid(row=0, column=1, padx=2)

        ttk.Button(cookie_btn_frame, text="帮助", command=self.show_cookie_help).grid(row=0, column=2, padx=2)

        # Cookie说明
        cookie_hint = ttk.Label(main_frame, text='格式: PHPSESSID=***** userhash=*****  (点击"自动获取"按钮可自动打开浏览器获取)', foreground="gray")
        cookie_hint.grid(row=1, column=1, sticky=tk.W, padx=5)

        # 串ID输入
        ttk.Label(main_frame, text="串ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.id_entry = ttk.Entry(main_frame, width=50)
        self.id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 标题设置
        ttk.Label(main_frame, text="自定义标题:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 标题说明
        title_hint = ttk.Label(main_frame, text="留空则使用原标题，填写则使用自定义标题", foreground="gray")
        title_hint.grid(row=3, column=2, sticky=tk.W, padx=5)

        # 输出格式选择
        format_frame = ttk.LabelFrame(main_frame, text="输出格式", padding="10")
        format_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.epub_var = tk.BooleanVar(value=False)
        self.txt_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(format_frame, text="EPUB", variable=self.epub_var).grid(row=0, column=0, padx=10)
        ttk.Checkbutton(format_frame, text="TXT", variable=self.txt_var).grid(row=0, column=1, padx=10)

        # 下载模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="下载模式", padding="10")
        mode_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.download_mode_var = tk.StringVar(value="all")
        ttk.Radiobutton(mode_frame, text="下载所有回复", variable=self.download_mode_var,
                       value="all").grid(row=0, column=0, padx=10, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="只下载PO的回复", variable=self.download_mode_var,
                       value="po").grid(row=0, column=1, padx=10, sticky=tk.W)

        # 内容过滤选择
        filter_frame = ttk.LabelFrame(main_frame, text="内容过滤（智能优化）", padding="10")
        filter_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.filter_auto_var = tk.BooleanVar(value=False)
        self.filter_smart_var = tk.BooleanVar(value=False)
        self.filter_manual_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(filter_frame, text="自动过滤短回复（≤25字符且无图片）",
                       variable=self.filter_auto_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        ttk.Checkbutton(filter_frame, text="智能过滤无意义回复（fy、mark、jmjp等）",
                       variable=self.filter_smart_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)

        ttk.Checkbutton(filter_frame, text="手动审核模式（逐条确认删除）",
                       variable=self.filter_manual_var).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)

        # 查看/编辑无意义词汇按钮
        ttk.Button(filter_frame, text="管理词汇表",
                  command=self.show_word_manager).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)

        self.download_btn = ttk.Button(button_frame, text="开始下载", command=self.start_download)
        self.download_btn.grid(row=0, column=0, padx=5)

        ttk.Button(button_frame, text="清空日志", command=self.clear_log).grid(row=0, column=1, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="下载日志", padding="5")
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(9, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 版权信息
        copyright_text = "请勿用于违法用途，工具仅供学习交流使用\n所下载及生成的文件版权属于X岛匿名版与原作者所有，请在24小时内删除"
        ttk.Label(main_frame, text=copyright_text, foreground="red", justify=tk.CENTER).grid(
            row=10, column=0, columnspan=3, pady=5
        )

    def load_settings(self):
        """加载保存的设置"""
        try:
            cookie = self.conf.load("cookie", "cookie")
            if cookie and len(cookie) > 0:
                cookie_str = cookie[0].replace("_", "%")
                self.cookie_entry.insert(0, cookie_str)
                self.log("已加载保存的Cookie")
        except:
            self.log("未检测到保存的Cookie")

    def save_cookie(self):
        """保存Cookie设置"""
        cookie = self.cookie_entry.get().strip()
        if not cookie:
            messagebox.showwarning("警告", "Cookie不能为空")
            return

        # 验证Cookie格式
        parts = cookie.split(" ")
        if len(parts) < 2:
            messagebox.showerror("错误", "Cookie格式不正确\n格式应为: PHPSESSID=***** userhash=*****")
            return

        # 保存Cookie
        cookie_encoded = cookie.replace("%", "_")
        self.conf.add("cookie", "cookie", cookie_encoded)
        self.conf.save()
        self.log("Cookie已保存")
        messagebox.showinfo("成功", "Cookie已保存")

    def auto_fetch_cookie(self):
        """自动获取Cookie"""
        if self.is_fetching_cookie:
            messagebox.showwarning("警告", "正在获取Cookie中，请等待")
            return

        if self.is_downloading:
            messagebox.showwarning("警告", "正在下载中，请等待下载完成")
            return

        # 检查selenium是否安装
        if not self.cookie_fetcher.use_selenium:
            result = messagebox.askyesno(
                "缺少依赖",
                "自动获取Cookie需要安装selenium库。\n\n是否现在安装？\n\n（将执行: pip install selenium）"
            )
            if result:
                self.log("正在安装selenium...")
                import subprocess
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
                    self.log('selenium安装成功，请重新点击"自动获取"按钮')
                    messagebox.showinfo("成功", 'selenium已安装，请重新点击"自动获取"按钮')
                    # 重新初始化fetcher
                    self.cookie_fetcher = CookieFetcher()
                except Exception as e:
                    self.log(f"安装失败: {str(e)}")
                    messagebox.showerror("错误", f"安装失败: {str(e)}")
            return

        # 在新线程中获取Cookie
        fetch_thread = threading.Thread(target=self._fetch_cookie_thread)
        fetch_thread.daemon = True
        fetch_thread.start()

    def _fetch_cookie_thread(self):
        """Cookie获取线程"""
        self.is_fetching_cookie = True
        self.auto_fetch_btn.config(state='disabled')

        def callback(msg):
            """更新日志的回调函数"""
            self.log(msg)

        try:
            self.log("="*50)
            self.log("开始自动获取Cookie...")
            self.log("即将打开浏览器，请在浏览器中登录X岛匿名版")
            self.log("登录成功后，Cookie会自动获取并填入")

            # 调用cookie_fetcher获取Cookie
            cookie_str = self.cookie_fetcher.fetch_cookie_auto(callback=callback)

            # 将Cookie填入输入框
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, cookie_str)

            self.log('Cookie已自动填入，请点击"保存"按钮保存')
            self.log("="*50)

            messagebox.showinfo("成功", 'Cookie获取成功！\n请点击"保存"按钮保存Cookie')

        except Exception as e:
            error_msg = str(e)
            self.log(f"获取Cookie失败: {error_msg}")
            self.log("="*50)
            messagebox.showerror("错误", f'获取Cookie失败:\n{error_msg}\n\n您可以点击"帮助"按钮查看手动获取方法')

        finally:
            self.is_fetching_cookie = False
            self.auto_fetch_btn.config(state='normal')

    def show_cookie_help(self):
        """显示Cookie获取帮助"""
        help_text = self.cookie_fetcher.fetch_cookie_manual_guide()

        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("Cookie获取帮助")
        help_window.geometry("600x500")

        # 添加文本框
        text_frame = ttk.Frame(help_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, help_text)
        text_widget.config(state='disabled')

        # 关闭按钮
        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)

    def show_word_manager(self):
        """显示无意义词汇管理窗口"""
        manager_window = tk.Toplevel(self.root)
        manager_window.title("管理无意义词汇表")
        manager_window.geometry("500x600")

        # 说明文本
        info_frame = ttk.Frame(manager_window, padding="10")
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, text="词汇表用于智能过滤功能，只有完全匹配的回复才会被过滤",
                 foreground="blue").pack()

        # 词汇列表
        list_frame = ttk.LabelFrame(manager_window, text="当前词汇表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建滚动文本框显示词汇
        words_text = scrolledtext.ScrolledText(list_frame, wrap=tk.WORD, height=20)
        words_text.pack(fill=tk.BOTH, expand=True)

        # 加载现有词汇
        words = self.content_filter.get_meaningless_words()
        words_text.insert(1.0, '\n'.join(words))

        # 添加词汇框架
        add_frame = ttk.LabelFrame(manager_window, text="添加新词汇", padding="10")
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        new_word_entry = ttk.Entry(add_frame, width=30)
        new_word_entry.pack(side=tk.LEFT, padx=5)

        def add_word():
            word = new_word_entry.get().strip()
            if word:
                self.content_filter.add_custom_word(word)
                words = self.content_filter.get_meaningless_words()
                words_text.delete(1.0, tk.END)
                words_text.insert(1.0, '\n'.join(words))
                new_word_entry.delete(0, tk.END)
                self.log(f'已添加词汇: {word}')
                messagebox.showinfo("成功", f'已添加词汇: {word}')

        ttk.Button(add_frame, text="添加", command=add_word).pack(side=tk.LEFT, padx=5)

        # 删除词汇说明
        del_frame = ttk.Frame(manager_window, padding="10")
        del_frame.pack(fill=tk.X, padx=10)
        ttk.Label(del_frame, text='提示：直接在上方文本框中编辑词汇表，点击"保存"生效',
                 foreground="gray").pack()

        # 按钮框架
        btn_frame = ttk.Frame(manager_window, padding="10")
        btn_frame.pack(fill=tk.X)

        def save_words():
            content = words_text.get(1.0, tk.END).strip()
            new_words = [w.strip() for w in content.split('\n') if w.strip()]
            # 重新设置词汇表
            ContentFilter.MEANINGLESS_WORDS = new_words
            self.log(f'词汇表已更新，共{len(new_words)}个词汇')
            messagebox.showinfo("成功", f'词汇表已更新，共{len(new_words)}个词汇')

        def reset_words():
            # 恢复默认词汇表
            default_words = [
                'jmjp', '集美交配', '姐妹交配', 'fy', '插眼', '好串我住',
                'mark', '码一下', '码了', '彩虹女人手', '沙发', 'dd', '已阅', '好耶'
            ]
            ContentFilter.MEANINGLESS_WORDS = default_words
            words_text.delete(1.0, tk.END)
            words_text.insert(1.0, '\n'.join(default_words))
            self.log('词汇表已恢复默认')
            messagebox.showinfo("成功", "词汇表已恢复默认")

        ttk.Button(btn_frame, text="保存", command=save_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="恢复默认", command=reset_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=manager_window.destroy).pack(side=tk.LEFT, padx=5)

    def show_manual_review(self, candidates, callback):
        """显示手动审核窗口"""
        if not candidates:
            messagebox.showinfo("提示", "没有需要审核的内容")
            callback([])
            return

        review_window = tk.Toplevel(self.root)
        review_window.title(f'手动审核 - 共{len(candidates)}条待审核')
        review_window.geometry("700x500")

        # 当前索引
        current_index = [0]
        to_delete = []

        # 显示区域
        content_frame = ttk.Frame(review_window, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 进度标签
        progress_label = ttk.Label(content_frame, text="", font=("Arial", 10, "bold"))
        progress_label.pack()

        # 原因标签
        reason_label = ttk.Label(content_frame, text="", foreground="blue")
        reason_label.pack(pady=5)

        # 内容显示
        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, height=15)
        content_text.pack(fill=tk.BOTH, expand=True, pady=10)

        # 按钮框架
        btn_frame = ttk.Frame(review_window, padding="10")
        btn_frame.pack()

        def show_current():
            if current_index[0] >= len(candidates):
                # 审核完成
                review_window.destroy()
                callback(to_delete)
                return

            cand = candidates[current_index[0]]
            progress_label.config(text=f'第 {current_index[0] + 1} / {len(candidates)} 条')

            reason_text = "短回复（≤25字符且无图片）" if cand['reason'] == 'short' else "无意义回复"
            reason_label.config(text=f'标记原因: {reason_text}')

            content_text.delete(1.0, tk.END)
            reply = cand['reply']
            content_text.insert(1.0, f"标题: {reply.get('title', '无标题')}\n\n")
            content_text.insert(tk.END, f"内容:\n{reply.get('content', '')}\n\n")
            if reply.get('img', ''):
                content_text.insert(tk.END, f"图片: {reply['img']}{reply.get('ext', '')}\n")

        def delete_current():
            to_delete.append(candidates[current_index[0]]['index'])
            self.log(f"标记删除: 第{current_index[0] + 1}条")
            current_index[0] += 1
            show_current()

        def keep_current():
            self.log(f"保留: 第{current_index[0] + 1}条")
            current_index[0] += 1
            show_current()

        def skip_all():
            self.log("跳过剩余所有审核")
            review_window.destroy()
            callback(to_delete)

        ttk.Button(btn_frame, text="删除 (D)", command=delete_current).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保留 (K)", command=keep_current).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="跳过剩余", command=skip_all).pack(side=tk.LEFT, padx=5)

        # 键盘快捷键
        review_window.bind('d', lambda e: delete_current())
        review_window.bind('k', lambda e: keep_current())

        # 显示第一条
        show_current()

    def apply_filters(self, replies, filter_options):
        """
        应用过滤器到回复列表

        Args:
            replies: 原始回复列表
            filter_options: 过滤选项字典 {'auto': bool, 'smart': bool, 'manual': bool}

        Returns:
            filtered_replies: 过滤后的回复列表
        """
        filtered_replies = replies.copy()

        # 1. 应用自动过滤（短回复）
        if filter_options.get('auto', False):
            self.log("应用自动过滤：短回复（≤25字符且无图片）")
            filtered_replies, info = self.content_filter.filter_auto(filtered_replies, max_length=25)
            self.log(f"  - 自动过滤了 {info['filtered']} 条短回复")

        # 2. 应用智能过滤（无意义回复）
        if filter_options.get('smart', False):
            self.log("应用智能过滤：无意义回复")
            filtered_replies, info = self.content_filter.filter_smart(filtered_replies)
            self.log(f"  - 智能过滤了 {info['filtered']} 条无意义回复")
            if info['filtered'] > 0:
                # 显示被过滤的内容样例
                samples = [self.content_filter.normalize_text(r['content']) for r in info['removed'][:5]]
                self.log(f"  - 样例: {', '.join(samples)}")

        # 3. 应用手动审核
        if filter_options.get('manual', False):
            self.log("应用手动审核模式...")
            candidates = self.content_filter.get_filter_candidates(filtered_replies, max_length=25)

            if candidates:
                self.log(f"  - 发现 {len(candidates)} 条待审核回复")
                self.log("  - 打开审核窗口，请在窗口中操作...")

                # 使用事件来等待手动审核完成
                import queue
                result_queue = queue.Queue()

                def manual_callback(to_delete_indices):
                    result_queue.put(to_delete_indices)

                # 在主线程中显示审核窗口
                self.root.after(0, lambda: self.show_manual_review(candidates, manual_callback))

                # 等待审核完成
                to_delete_indices = result_queue.get()

                # 删除标记的回复（从后往前删除以避免索引问题）
                for idx in sorted(to_delete_indices, reverse=True):
                    if 0 <= idx < len(filtered_replies):
                        del filtered_replies[idx]

                self.log(f"  - 手动审核完成，删除了 {len(to_delete_indices)} 条回复")
            else:
                self.log("  - 没有需要审核的内容")

        return filtered_replies

    def log(self, message):
        """在日志区域显示消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def start_download(self):
        """开始下载"""
        if self.is_downloading:
            messagebox.showwarning("警告", "正在下载中，请等待完成")
            return

        # 获取Cookie
        cookie = self.cookie_entry.get().strip()
        if not cookie:
            messagebox.showerror("错误", "请先设置Cookie")
            return

        # 获取串ID
        try:
            thread_id = int(self.id_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的串ID（数字）")
            return

        # 获取输出格式
        output_formats = []
        if self.epub_var.get():
            output_formats.append("epub")
        if self.txt_var.get():
            output_formats.append("txt")

        if not output_formats:
            messagebox.showerror("错误", "请至少选择一种输出格式")
            return

        # 获取标题设置
        custom_title = self.title_entry.get().strip()

        # 获取过滤选项
        filter_options = {
            'auto': self.filter_auto_var.get(),
            'smart': self.filter_smart_var.get(),
            'manual': self.filter_manual_var.get()
        }

        # 获取下载模式
        download_mode = self.download_mode_var.get()

        # 在新线程中执行下载
        download_thread = threading.Thread(
            target=self.download_thread,
            args=(cookie, thread_id, output_formats, custom_title, filter_options, download_mode)
        )
        download_thread.daemon = True
        download_thread.start()

    def download_thread(self, cookie, thread_id, output_formats, custom_title, filter_options, download_mode):
        """下载线程"""
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        self.progress.start()

        try:
            self.log("="*50)
            self.log(f"开始下载串 ID: {thread_id}")
            self.log(f"输出格式: {', '.join(output_formats)}")

            # 创建Xdnmb实例
            x = Xdnmb(cookie)

            # 根据下载模式选择处理函数
            if download_mode == "po":
                handler = x.po
                mode_text = "只下载PO的回复"
            else:
                handler = x.all
                mode_text = "下载所有回复"

            # 获取数据
            self.log(f"下载模式: {mode_text}")
            self.log("正在获取串内容...")
            fin = x.get_with_cache(thread_id, handler)

            # 处理标题
            original_title = fin["title"]
            self.log(f"从API获取的原始标题: {original_title}")
            self.log(f"自定义标题: {custom_title if custom_title else '(未设置)'}")

            if custom_title:
                fin["title"] = custom_title
                self.log(f"✓ 使用自定义标题: {custom_title}")
            else:
                self.log(f"✓ 使用原始标题: {fin['title']}")

            fin["id"] = thread_id
            original_count = len(fin['Replies'])
            self.log(f"共获取到 {original_count} 条回复")

            # 应用内容过滤
            if any(filter_options.values()):
                self.log("-" * 30)
                self.log("开始应用内容过滤...")
                fin['Replies'] = self.apply_filters(fin['Replies'], filter_options)
                filtered_count = original_count - len(fin['Replies'])
                self.log(f"过滤完成：保留 {len(fin['Replies'])} 条，过滤 {filtered_count} 条")
                self.log("-" * 30)

            # 导出文件
            self.log("正在导出文件...")
            self.log(f"最终使用的标题: {fin['title']}")

            if "epub" in output_formats:
                self.log("正在生成EPUB...")
                e = Epub(fin["title"], f"https://www.nmbxd1.com/t/{thread_id}")
                e.plugin(x.s)
                e.cover(fin["content"])

                e.add_text(
                    f'''来自https://www.nmbxd1.com/t/{thread_id}<br />版权归属原作者及X岛匿名版<br />请勿用于违法用途，仅供学习交流使用，请在24小时内删除<br />本文档由https://github.com/Rcrwrate/Xdnmb_downer生成''',
                    "来源声明"
                )

                msg = fin["Replies"]
                for i, reply in enumerate(msg):
                    if i % 10 == 0:
                        self.log(f"处理进度: {i+1}/{len(msg)}")

                    if reply["img"] != "":
                        e.add_text(
                            reply["content"],
                            reply["title"],
                            ["https://image.nmb.best/image/" + reply["img"] + reply["ext"]]
                        )
                    else:
                        e.add_text(reply["content"], reply["title"])

                e.finish()
                self.log(f"EPUB文件已生成: .tmp/{fin['title']}.epub")

            if "txt" in output_formats:
                self.log("正在生成TXT...")
                t = TXT(fin["title"])
                t.add(f'''来自https://www.nmbxd1.com/t/{thread_id}\n版权归属原作者及X岛匿名版\n请勿用于违法用途，仅供学习交流使用，请在24小时内删除\n本文档由https://github.com/Rcrwrate/Xdnmb_downer生成''')
                t.add(fin["content"])

                for reply in fin["Replies"]:
                    t.add("\n——————————")
                    t.add(reply["content"])

                del t
                self.log(f"TXT文件已生成: .tmp/{fin['title']}.txt")

            self.log("="*50)
            self.log("下载完成！文件保存在 .tmp 文件夹中")
            messagebox.showinfo("成功", f"下载完成！\n文件保存在 .tmp 文件夹中")

        except XdnmbException as e:
            error_msg = str(e)
            self.log(f"错误: {error_msg}")
            messagebox.showerror("错误", error_msg)

        except Exception as e:
            error_msg = str(e)
            self.log(f"未知错误: {error_msg}")
            messagebox.showerror("错误", f"下载失败: {error_msg}")

        finally:
            self.is_downloading = False
            self.download_btn.config(state='normal')
            self.progress.stop()

def main():
    root = tk.Tk()
    app = XdnmbDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

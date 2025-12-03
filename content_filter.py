"""
内容过滤模块
提供三种过滤模式：自动过滤、手动审核、智能识别
"""
import re

class ContentFilter:
    """内容过滤器"""

    # 无意义词汇列表
    MEANINGLESS_WORDS = [
        'jmjp',
        '集美交配',
        '姐妹交配',
        'fy',
        '插眼',
        '好串我住',
        'mark',
        '码一下',
        '码了',
        '彩虹女人手',
        # 可以继续添加更多
        '沙发',
        'dd',
        '已阅',
        '好耶',
    ]

    def __init__(self):
        self.filtered_count = 0
        self.total_count = 0

    def normalize_text(self, text):
        """
        标准化文本：去除空格、换行、标签等
        用于精确匹配
        """
        # 移除HTML标签
        text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        # 移除空格和换行
        text = text.strip().replace(' ', '').replace('\n', '').replace('\r', '')
        return text

    def is_short_reply(self, reply, max_length=25):
        """
        检测是否为短回复
        条件：内容≤max_length字符 且 无图片
        """
        content = self.normalize_text(reply.get('content', ''))
        has_image = reply.get('img', '') != ''

        return len(content) <= max_length and not has_image

    def is_meaningless(self, reply):
        """
        检测是否为无意义回复
        条件：标准化后的内容完全等于无意义词汇列表中的某一项
        """
        content = self.normalize_text(reply.get('content', ''))

        # 精确匹配，内容必须完全等于列表中的词汇
        return content in self.MEANINGLESS_WORDS

    def filter_auto(self, replies, max_length=25):
        """
        自动过滤模式：自动删除短回复

        Args:
            replies: 回复列表
            max_length: 最大字符长度

        Returns:
            filtered_replies: 过滤后的回复列表
            filter_info: 过滤信息
        """
        self.filtered_count = 0
        self.total_count = len(replies)

        filtered_replies = []
        removed_replies = []

        for reply in replies:
            if self.is_short_reply(reply, max_length):
                self.filtered_count += 1
                removed_replies.append(reply)
            else:
                filtered_replies.append(reply)

        filter_info = {
            'mode': 'auto',
            'total': self.total_count,
            'filtered': self.filtered_count,
            'remaining': len(filtered_replies),
            'removed': removed_replies
        }

        return filtered_replies, filter_info

    def filter_smart(self, replies):
        """
        智能识别模式：自动删除无意义回复

        Args:
            replies: 回复列表

        Returns:
            filtered_replies: 过滤后的回复列表
            filter_info: 过滤信息
        """
        self.filtered_count = 0
        self.total_count = len(replies)

        filtered_replies = []
        removed_replies = []

        for reply in replies:
            if self.is_meaningless(reply):
                self.filtered_count += 1
                removed_replies.append(reply)
            else:
                filtered_replies.append(reply)

        filter_info = {
            'mode': 'smart',
            'total': self.total_count,
            'filtered': self.filtered_count,
            'remaining': len(filtered_replies),
            'removed': removed_replies
        }

        return filtered_replies, filter_info

    def filter_combined(self, replies, max_length=25):
        """
        组合模式：同时应用自动过滤和智能识别

        Args:
            replies: 回复列表
            max_length: 最大字符长度

        Returns:
            filtered_replies: 过滤后的回复列表
            filter_info: 过滤信息
        """
        self.filtered_count = 0
        self.total_count = len(replies)

        filtered_replies = []
        removed_replies = []

        for reply in replies:
            # 满足任意一个条件就过滤
            if self.is_short_reply(reply, max_length) or self.is_meaningless(reply):
                self.filtered_count += 1
                removed_replies.append(reply)
            else:
                filtered_replies.append(reply)

        filter_info = {
            'mode': 'combined',
            'total': self.total_count,
            'filtered': self.filtered_count,
            'remaining': len(filtered_replies),
            'removed': removed_replies
        }

        return filtered_replies, filter_info

    def get_filter_candidates(self, replies, max_length=25):
        """
        获取待审核的回复列表（用于手动审核模式）

        Args:
            replies: 回复列表
            max_length: 最大字符长度

        Returns:
            candidates: 待审核回复列表，每项包含索引和回复内容
        """
        candidates = []

        for idx, reply in enumerate(replies):
            is_short = self.is_short_reply(reply, max_length)
            is_meaningless = self.is_meaningless(reply)

            if is_short or is_meaningless:
                candidates.append({
                    'index': idx,
                    'reply': reply,
                    'reason': 'short' if is_short else 'meaningless'
                })

        return candidates

    @staticmethod
    def add_custom_word(word):
        """添加自定义无意义词汇"""
        if word and word not in ContentFilter.MEANINGLESS_WORDS:
            ContentFilter.MEANINGLESS_WORDS.append(word)

    @staticmethod
    def remove_custom_word(word):
        """移除自定义无意义词汇"""
        if word in ContentFilter.MEANINGLESS_WORDS:
            ContentFilter.MEANINGLESS_WORDS.remove(word)

    @staticmethod
    def get_meaningless_words():
        """获取当前的无意义词汇列表"""
        return ContentFilter.MEANINGLESS_WORDS.copy()


if __name__ == "__main__":
    # 测试代码
    filter = ContentFilter()

    test_replies = [
        {'content': 'fy', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': 'fyyy', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': 'mark', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': '这是一个正常的回复内容', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': 'jmjp', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': '集美交配', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': '短回复', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': '这是一个比较长的正常回复，应该不会被过滤掉', 'img': '', 'title': '无标题', 'ext': ''},
        {'content': 'mark', 'img': 'image123', 'title': '无标题', 'ext': '.jpg'},  # 有图片不应被自动过滤
    ]

    print("=== 测试智能识别模式 ===")
    filtered, info = filter.filter_smart(test_replies)
    print(f"总数: {info['total']}, 过滤: {info['filtered']}, 剩余: {info['remaining']}")
    print(f"被过滤的内容:")
    for r in info['removed']:
        print(f"  - '{r['content']}'")

    print("\n=== 测试自动过滤模式 ===")
    filtered, info = filter.filter_auto(test_replies, max_length=10)
    print(f"总数: {info['total']}, 过滤: {info['filtered']}, 剩余: {info['remaining']}")
    print(f"被过滤的内容:")
    for r in info['removed']:
        print(f"  - '{r['content']}'")

    print("\n=== 测试组合模式 ===")
    filtered, info = filter.filter_combined(test_replies, max_length=10)
    print(f"总数: {info['total']}, 过滤: {info['filtered']}, 剩余: {info['remaining']}")
    print(f"被过滤的内容:")
    for r in info['removed']:
        print(f"  - '{r['content']}'")

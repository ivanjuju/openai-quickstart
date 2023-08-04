import re

from book import ContentType
from prompt.constants import system_prompt


class PromptTemplate:
    @staticmethod
    def make_text_prompt(text: str, target_language: str) -> str:
        return f"翻译为{target_language}：{text}"

    @staticmethod
    def make_table_prompt(table: str, target_language: str) -> str:
        return f"翻译为{target_language}，保持间距（空格，分隔符），以表格形式返回：\n{table}"

    @staticmethod
    def make_text_messages(content: str, target_language: str) -> list:
        content = re.sub(r' +\n', "\n", content)
        return [
            {"role": "system", "content": system_prompt(target_language)},
            {"role": "user", "content": content},
        ]

    @staticmethod
    def translate_prompt(content, target_language: str) -> str:
        if content.content_type == ContentType.TEXT:
            return PromptTemplate.make_text_prompt(content.original, target_language)
        elif content.content_type == ContentType.TABLE:
            return PromptTemplate.make_table_prompt(content.get_original_as_str(), target_language)

    @staticmethod
    def translate_messages(content, target_language: str) -> list:
        if content.content_type == ContentType.MIXED:
            return PromptTemplate.make_text_messages(content.original, target_language)

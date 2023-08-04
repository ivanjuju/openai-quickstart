from enum import Enum, auto

import pdfplumber
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent
from book.content import MixedContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG


class ParserType(Enum):
    AHEAD = 'AHEAD'
    BEHIND = 'BEHIND'


class PDFParser:
    @staticmethod
    def parse_pdf(pdf_file_path: str, pages: Optional[int] = None,
                  parse_type: Optional[ParserType] = ParserType.AHEAD) -> Book:
        # 构建book变量，初始化page数组
        book = Book(pdf_file_path)

        with pdfplumber.open(pdf_file_path) as pdf:
            # 校验pages参数的合法性
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            # 确定要解析、翻译的page数
            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()
                match parse_type:
                    case ParserType.AHEAD:
                        PDFParser.parse_ahead(page, pdf_page)
                    case ParserType.BEHIND:
                        PDFParser.parse_behind(page, pdf_page)

                book.add_page(page)

        return book

    @staticmethod
    def parse_ahead(page, pdf_page):
        # Store the original text content
        raw_text = pdf_page.extract_text()
        tables = pdf_page.extract_tables()
        # Remove each cell's content from the original text
        for table_data in tables:
            for row in table_data:
                for cell in row:
                    raw_text = raw_text.replace(cell, "", 1)
        # Handling text
        if raw_text:
            # Remove empty lines and leading/trailing whitespaces
            raw_text_lines = raw_text.splitlines()
            cleaned_raw_text_lines = [line.strip() for line in raw_text_lines if line.strip()]
            cleaned_raw_text = "\n".join(cleaned_raw_text_lines)

            text_content = Content(content_type=ContentType.TEXT, original=cleaned_raw_text)
            page.add_content(text_content)
            LOG.debug(f"[raw_text]\n {cleaned_raw_text}")
        # Handling tables
        if tables:
            table = TableContent(tables)
            page.add_content(table)
            LOG.debug(f"[table]\n{table}")

    @staticmethod
    def parse_behind(page, pdf_page):
        text = pdf_page.extract_text(layout=True)
        content = MixedContent(ContentType.MIXED, text)
        page.add_content(content)
        pass

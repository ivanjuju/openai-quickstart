from typing import Optional
from model import Model
from prompt.prompt_template import PromptTemplate
from translator.pdf_parser import PDFParser, ParserType
from translator.writer import Writer
from utils import LOG


class PDFTranslator:
    def __init__(self, model: Model):
        self.model = model

    def translate_pdf(self, pdf_file_path: str, file_format: str = 'PDF', target_language: str = '中文',
                      output_file_path: str = None, pages: Optional[int] = None,
                      parse_type: Optional[ParserType] = ParserType.AHEAD):
        # 解析pdf并封装单book变量中
        book = PDFParser.parse_pdf(pdf_file_path, pages, parse_type)

        for page_idx, page in enumerate(book.pages):
            for content_idx, content in enumerate(page.contents):
                if content.original is None or content.original == '':
                    continue
                match parse_type:
                    case ParserType.AHEAD:
                        prompt = PromptTemplate.translate_prompt(content, target_language)
                        translation, status = self.model.make_request(prompt)
                    case ParserType.BEHIND:
                        prompt = PromptTemplate.translate_messages(content, target_language)
                        translation, status = self.model.make_request_by_message(prompt)
                    case _:
                        raise Exception("parse type error!")
                LOG.debug(prompt)
                LOG.info(translation)

                # Update the content in self.book.pages directly
                book.pages[page_idx].contents[content_idx].set_translation(translation, status)

        Writer.save_translated_book(book, output_file_path, file_format)

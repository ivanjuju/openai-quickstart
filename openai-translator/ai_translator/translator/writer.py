import ast
import pandas as pd
from reportlab.lib import colors, pagesizes, units
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

from book import Book, ContentType
from utils import LOG

table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),  # 更改表头字体为 "SimSun"
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),  # 更改表格中的字体为 "SimSun"
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
])


class Writer:
    @staticmethod
    def save_translated_book(book: Book, output_file_path: str = None, file_format: str = "PDF"):
        if file_format.lower() == "pdf":
            Writer._save_translated_book_pdf(book, output_file_path)
        elif file_format.lower() == "markdown":
            Writer._save_translated_book_markdown(book, output_file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @staticmethod
    def _save_translated_book_pdf(book: Book, output_file_path: str = None):
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', f'_translated.pdf')

        LOG.info(f"pdf_file_path: {book.pdf_file_path}")
        LOG.info(f"开始翻译: {output_file_path}")

        # Register Chinese font
        font_path = "../fonts/simsun.ttc"  # 请将此路径替换为您的字体文件路径
        pdfmetrics.registerFont(TTFont("SimSun", font_path))

        # Create a new ParagraphStyle with the SimSun font
        simsun_style = ParagraphStyle('SimSun', fontName='SimSun', fontSize=12, leading=14)

        # Create a PDF document
        doc = SimpleDocTemplate(output_file_path, pagesize=pagesizes.letter)
        styles = getSampleStyleSheet()
        story = []

        # Iterate over the pages and contents
        for page in book.pages:
            for content in page.contents:
                if content.status:
                    if content.content_type == ContentType.TEXT:
                        # Add translated text to the PDF
                        text = content.translation
                        para = Paragraph(text, simsun_style)
                        story.append(para)

                    elif content.content_type == ContentType.TABLE:
                        # Add table to the PDF
                        table = content.translation
                        pdf_table = Table(table.values.tolist())
                        pdf_table.setStyle(table_style)
                        story.append(pdf_table)
                    elif content.content_type == ContentType.MIXED:
                        content_text_list = ast.literal_eval(content.translation)
                        for content_text in content_text_list:
                            content_text_value = content_text.get("content")
                            if not content_text_value:
                                continue
                            content_text_type = content_text.get("type")
                            if content_text_type == "text":
                                para = Paragraph(content_text_value, simsun_style)
                                story.append(para)
                            elif content_text_type == "table":
                                table_df = pd.DataFrame(content_text_value)
                                pdf_table = Table(table_df.values.tolist())
                                pdf_table.setStyle(table_style)
                                story.append(pdf_table)

            # Add a page break after each page except the last one
            if page != book.pages[-1]:
                story.append(PageBreak())

        # Save the translated book as a new PDF file
        doc.build(story)
        LOG.info(f"翻译完成: {output_file_path}")

    @staticmethod
    def _save_translated_book_markdown(book: Book, output_file_path: str = None):
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', f'_translated.md')

        LOG.info(f"pdf_file_path: {book.pdf_file_path}")
        LOG.info(f"开始翻译: {output_file_path}")
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            # Iterate over the pages and contents
            for page in book.pages:
                for content in page.contents:
                    if content.status:
                        if content.content_type == ContentType.TEXT:
                            # Add translated text to the Markdown file
                            text = content.translation
                            output_file.write(text + '\n\n')

                        elif content.content_type == ContentType.TABLE:
                            # Add table to the Markdown file
                            table = content.translation
                            body, header, separator = Writer.df_to_table_str(table)
                            output_file.write(header + separator + body)
                        elif content.content_type == ContentType.MIXED:
                            content_text_list = ast.literal_eval(content.translation)
                            for content_text in content_text_list:
                                content_text_value = content_text.get("content")
                                if not content_text_value:
                                    continue
                                content_text_type = content_text.get("type")
                                if content_text_type == "text":
                                    output_file.write(content_text_value + '\n\n')
                                elif content_text_type == "table":
                                    table_df = pd.DataFrame(content_text_value)
                                    body, header, separator = Writer.df_to_table_str(table_df)
                                    output_file.write(header + separator + body)

                # Add a page break (horizontal rule) after each page except the last one
                if page != book.pages[-1]:
                    output_file.write('---\n\n')

        LOG.info(f"翻译完成: {output_file_path}")

    @staticmethod
    def df_to_table_str(table):
        header = '| ' + ' | '.join(str(column) for column in table.columns) + ' |' + '\n'
        separator = '| ' + ' | '.join(['---'] * len(table.columns)) + ' |' + '\n'
        # body = '\n'.join(['| ' + ' | '.join(row) + ' |' for row in table.values.tolist()]) + '\n\n'
        body = '\n'.join(['| ' + ' | '.join(str(cell) for cell in row) + ' |' for row in
                          table.values.tolist()]) + '\n\n'
        return body, header, separator

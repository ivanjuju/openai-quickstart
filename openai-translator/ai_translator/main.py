import sys
import os

from translator.pdf_parser import ParserType

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader
from model import GLMModel, OpenAIModel
from translator import PDFTranslator

if __name__ == "__main__":
    # 参数解析
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    # yml中的配置信息解析
    config_loader = ConfigLoader(args.config)
    config = config_loader.load_config()

    # 参数or配置文件中获取本次翻译采用的LLM信息
    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']

    # 构建LLM基类
    model = OpenAIModel(model=model_name, api_key=api_key)

    # 获取要解析文件的地址
    pdf_file_path = args.book if args.book else config['common']['book']
    # 翻译后文件的格式，如：pdf、md
    file_format = args.file_format if args.file_format else config['common']['file_format']

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    # 解析并翻译pdf
    translator.translate_pdf(pdf_file_path, file_format, parse_type=ParserType(args.parser_type))

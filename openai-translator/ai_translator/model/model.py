from book import ContentType


class Model:

    def make_request_by_message(self, messages: list):
        raise NotImplementedError("子类必须实现 make_request_by_message 方法")

    def make_request(self, prompt):
        raise NotImplementedError("子类必须实现 make_request 方法")

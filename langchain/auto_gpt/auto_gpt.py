import os

import faiss
import gradio as gr
from langchain import SerpAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.docstore import InMemoryDocstore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.tools import Tool
from langchain.vectorstores import FAISS
from langchain_experimental.autonomous_agents import AutoGPT


def initialize_chat_bot(vector_store_dir: str = "chat_bot"):
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name="search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions",
        )
    ]
    # OpenAI Embedding 向量维数
    embedding_size = 1536
    # 使用 Faiss 的 IndexFlatL2 索引
    index = faiss.IndexFlatL2(embedding_size)
    # 实例化 Faiss 向量数据库
    embeddings_model = OpenAIEmbeddings()
    vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
    global AGENT
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    AGENT = AutoGPT.from_llm_and_tools(
        ai_name="Jarvis",
        ai_role="Assistant",
        tools=tools,
        llm=llm,
        memory=vectorstore.as_retriever(),  # 实例化 Faiss 的 VectorStoreRetriever
    )
    # 打印 Auto-GPT 内部的 chain 日志
    AGENT.chain.verbose = True
    return AGENT


def chat(message, history):
    print(f"[message]{message}")
    print(f"[history]{history}")
    ans = AGENT.run([message])
    print(ans)
    return ans


def launch_gradio():
    demo = gr.ChatInterface(
        fn=chat,
        title="贾维斯",
        # retry_btn=None,
        # undo_btn=None,
        chatbot=gr.Chatbot(height=600),
    )

    demo.launch(share=True, server_name="0.0.0.0")


if __name__ == "__main__":
    # 初始化房产销售机器人
    initialize_chat_bot()
    # 启动 Gradio 服务
    launch_gradio()

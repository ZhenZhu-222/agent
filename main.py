import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from jiankong import ragtool
from smart_pasture import render_smart_pasture
from utils import deteframe_agent


st.set_page_config(page_title="智能体工具箱", page_icon="🤖", layout="wide")


MODULES = {
    "航空装配车间智能体": "assembly_agent",
    "智慧牛场驾驶舱": "smart_pasture",
}


def render_assembly_agent() -> None:
    """Render the existing aviation assembly agent experience."""
    st.title("航空装配车间智能体")

    with st.sidebar:
        openai_api_key = st.text_input("请输入 api 秘钥：", type="password", key="assembly_api_key")
        st.markdown("[请联系赵博 18851137913]")

        if openai_api_key:
            ragtool.openai_api_key = openai_api_key

        uploaded_file = st.file_uploader("请上传知识库文件，类型 pdf", type=["pdf"], key="assembly_pdf")
        ragtool.uploaded_file = uploaded_file

        if ragtool.uploaded_file is None:
            st.info("未检测到上传文件，请确保文件已上传后重试。")

    api_key = getattr(ragtool, "openai_api_key", None)

    if ragtool.uploaded_file:
        content = ragtool.uploaded_file.read()
        temp_pdf_path = "temp.pdf"
        with open(temp_pdf_path, "wb") as temp_file:
            temp_file.write(content)

        loader = PyPDFLoader(temp_pdf_path)
        doc = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=40,
            separators=["\n", "\n\n", "。"],
        )
        texts = splitter.split_documents(doc)
        ragtool.texts = texts

    if "rag_memory" not in st.session_state:
        st.session_state["rag_memory"] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="answer",
        )
    ragtool.memory = st.session_state["rag_memory"]

    if "agent_memory" not in st.session_state:
        st.session_state["agent_memory"] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

    if "memorys" not in st.session_state:
        st.session_state["memorys"] = [
            {"role": "human", "content": "你好"},
            {"role": "ai", "content": "我是基于智能体的智能装配助手，有什么可以帮您"},
        ]

    for content in st.session_state["memorys"]:
        st.chat_message(content["role"]).write(content["content"])

    if "assembly_input" not in st.session_state:
        st.session_state["assembly_input"] = ""

    st.session_state["assembly_input"] = st.chat_input(
        "请输入您的问题", disabled=not api_key
    )

    if st.session_state["assembly_input"]:
        question = st.session_state["assembly_input"]

        if not api_key:
            st.info("请输入你的 api 秘钥")
            st.stop()

        st.session_state["memorys"].append({"role": "human", "content": question})
        st.chat_message("human").write(question)

        if not ragtool.uploaded_file:
            st.info("请上传知识库文档后重试")
            st.stop()
        else:
            with st.spinner("AI 正在思考中，请稍等..."):
                response = deteframe_agent(
                    open_ai_key=api_key,
                    memorys=st.session_state["agent_memory"],
                    question=question,
                )
                st.session_state["memorys"].append({"role": "ai", "content": response["output"]})
                st.chat_message("ai").write(response["output"])

                if ragtool.documents:
                    with st.expander("点击查看数据库原文"):
                        for doc in ragtool.documents["source_documents"]:
                            st.write(doc.page_content)
                    ragtool.documents = None

        st.session_state["assembly_input"] = ""


st.sidebar.title("智能体插件中心")
selected_module = st.sidebar.radio("选择功能", list(MODULES.keys()), key="selected_module")

if MODULES[selected_module] == "assembly_agent":
    render_assembly_agent()
else:
    render_smart_pasture()

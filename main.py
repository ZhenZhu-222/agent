from langchain_openai import OpenAI
import streamlit as st
from langchain.memory import ConversationBufferMemory
from ceshi2 import deteframe_agent
from jiankong import ragtool
from langchain import hub
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from prompt import PROMPT_TEMPLATE
from jiankong import ragtool
import streamlit as st



# if "ragtool" not in st.session_state:
#
#     st.session_state["ragtool"] = ragtool


st.title("航空装配车间智能体")

with st.sidebar:
    openai_api_key = st.text_input("请输入api秘钥：", type="password",key="api_key_input")
    st.markdown("[请联系赵博18851137913]")
    if openai_api_key is not None:
        ragtool.openai_api_key = openai_api_key# 将文件赋值给 ragtool.uploaded_file


   # ragtool.uploaded_file = st.file_uploader("上传你的PDF文件：", type="pdf")

    uploaded_file = st.file_uploader("请上传知识库文件，类型pdf", type=["pdf"])
    ragtool.uploaded_file = uploaded_file

    # if uploaded_file is not None:
    #     ragtool.uploaded_file = uploaded_file  # 将文件赋值给 ragtool.uploaded_file
    # else:
    #     st.warning("未检测到上传文件，请上传一个 PDF 文件后再试。")

    if ragtool.uploaded_file is None:
        # raise ValueError("未检测到上传文件，请确保文件已上传。")
        st.info("未检测到上传文件，请确保文件已上传后重试。")
        #st.stop()
        # return
if ragtool.uploaded_file:
    content = ragtool.uploaded_file.read()
    # 将文件内容写入临时 PDF 文件
    temp_pdf_path = "temp.pdf"
    with open(temp_pdf_path, "wb") as temp_file:
        temp_file.write(content)

    # 加载 PDF 文件
    loader = PyPDFLoader(temp_pdf_path)
    doc = loader.load()  # 得到 documents 列表

    # 分割文本
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=40,
        separators=["\n", "\n\n", "。"]
    )
    texts = splitter.split_documents(doc)
    ragtool.texts = texts

# 初始化对话记忆
if "rag_memory" not in st.session_state:
    st.session_state["rag_memory"] = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="answer"
    )
ragtool.memory = st.session_state["rag_memory"]

if "agent_memory" not in st.session_state:
    st.session_state["agent_memory"] = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )


if "memorys" not in st.session_state:
    st.session_state["memorys"] = [
        {"role": "human", "content": "你好"},
        {"role": "ai", "content": "我是基于智能体的智能装配助手，有什么可以帮您"}
    ]

# 显示对话历史
for content in st.session_state["memorys"]:
    st.chat_message(content["role"]).write(content["content"])

# 用户输入问题
if "input" not in st.session_state:
    st.session_state["input"] = ""  # 初始化输入框状态

st.session_state["input"] = st.chat_input("请输入您的问题",disabled=not openai_api_key)


if st.session_state["input"]:
    question = st.session_state["input"]

    if not openai_api_key:
        st.info("请输入你的api秘钥")
        st.stop()

    # 将用户输入加入对话历史
    st.session_state["memorys"].append({"role": "human", "content": question})
    st.chat_message("human").write(question)

    # 处理文件上传和问题
    if not ragtool.uploaded_file:
        st.info("请上传知识库文档后重试")
        st.stop()
    else:
        with st.spinner("AI正在思考中，请稍等..."):

            try:
                # 调用 `qa_agent` 获取答案
                response = deteframe_agent(open_ai_key= openai_api_key, memorys=st.session_state["agent_memory"],
                                    question= question)
                # 将 AI 回复加入对话历史
                st.session_state["memorys"].append({"role": "ai", "content": response["output"]})
                st.chat_message("ai").write(response["output"])
                if ragtool.documents:
                    with st.expander("点击查看数据库原文"):
                        for doc in ragtool.documents["source_documents"]:
                            st.write(doc.page_content)
                    ragtool.documents = None
            finally:
                pass
            # except Exception as e:
            #     st.error(f"AI处理错误：{str(e)}")

    # 清空输入框
    st.session_state["input"] = ""

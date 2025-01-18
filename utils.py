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




def deteframe_agent(open_ai_key, memorys, question):

    class rag(BaseTool):
        name = "装配知识库工具"
        description = "当你被要求回应大模型或者装配内容时，请使用此工具"

        def _run(self, text):
            model = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=open_ai_key)
            # 读取 PDF 文件内容
            # with open(ragtool.uploaded_file, "rb") as file:
            #     content = file.read()  # 读取文件内容
            # 检查上传文件是否存在

            # 生成向量数据库
            embedding_model = OpenAIEmbeddings(openai_api_key=open_ai_key)
            db = FAISS.from_documents(ragtool.texts, embedding_model)
            retriever = db.as_retriever()

            # 构建 ConversationalRetrievalChain
            chain = ConversationalRetrievalChain.from_llm(
                llm=model,
                memory=ragtool.memory,
                retriever=retriever,
                chain_type="refine",
                return_source_documents=True
            )

            # 假设 text 一定是包含 'title' 键的字典
            text = text['title']

            # 检查是否成功转换为字符串（以防万一）
            if not isinstance(text, str):
                raise ValueError(f"Invalid text input after extraction: {text}")

            print(f"Processed text: {text}")
            result = chain.invoke({"chat_history": ragtool.memory, "question": text})
            ragtool.documents = result
            return result["answer"]






    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=open_ai_key,
        temperature=0
    )

    # Create rag instance with parameters passed in
    tools = [rag()]

    # Pull the structured chat agent prompt from hub
    prompt = hub.pull("hwchase17/structured-chat-agent")

    # New instructions for the model to follow
    additional_instruction = "你对用户的一切回答都要检查是否回应的是中文，必须严格使用中文输出，不管对方使用的什么语言。\n\n"

    # Modify the system message prompt
    original_system_message = prompt.messages[0].prompt
    new_template = original_system_message.template + additional_instruction
    prompt.messages[0].prompt.template = new_template

    # Create agent
    agent = create_structured_chat_agent(
        llm=model,
        tools=tools,
        prompt=prompt
    )

    # Create the agent executor with tools and memory
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memorys,
        verbose=True,
        handle_parsing_errors=Ture,
        max_iterations=8
    )

    # Execute the agent
    response = agent_executor.invoke({
        "input": question
    })

    return response

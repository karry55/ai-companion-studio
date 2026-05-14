import streamlit as st
import os
from openai import OpenAI

st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="😶‍🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={

    }
)
# 大标题
st.title("AI智能伴侣")

# 创建AI大模型交互的客户端对象
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# logo
st.logo("资源/logo.png")

# 系统提示词
system_prompt = "你是一个可爱的ai助理,你的名字叫做karry"

# 初始化聊天
if "messages" not in st.session_state:
    st.session_state.messages = []

# 展示聊天信息
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# 消息输入框
prompt = st.chat_input("请输入您要咨询的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print("-------------->调用AI大模型,提示词:", prompt)

    # 保存用户的提输词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用AI大模型
    print([
        {"role": "system", "content": system_prompt},
        *st.session_state.messages
    ])
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages
        ],
        stream=True
    )

    # 输出大模型返回的结果(流式输出)
    response_message = st.empty()  # 用于展示大模型返回的结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 保存大模型返回的结果（使用full_response而不是ai_reply）
    st.session_state.messages.append({"role": "assistant", "content": full_response})
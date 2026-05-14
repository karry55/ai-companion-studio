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
st.logo("资源/logo.png")  # 改用 st.image

#系统提示词
system_prompt="你是一个可爱的ai助理,你的名字叫做karry"

#初始化聊天
if "massages" not in st.session_state:
    st.session_state.massages = [
        #{"role": "system", "content": system_prompt}
    ]
#展示聊天信息
for message in st.session_state.massages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else :
        st.chat_message("assistant").write(message["content"])



# 消息输入框
prompt = st.chat_input("请输入您要咨询的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print("-------------->调用AI大模型,提示词:", prompt)
    #保存用户的提输词
    st.session_state.massages.append({"role": "user", "content": prompt})

    # 调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-v4-pro",  # 修正模型名称
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}  # 使用用户的输入
        ],
        stream=False
    )

    # 显示AI回复
    ai_reply = response.choices[0].message.content
    print("<--------------AI大模型回复:", ai_reply)
    st.chat_message("assistant").write(ai_reply)
    #保存大模型返回的结果
    st.session_state.massages.append({"role": "assistant", "content": ai_reply})


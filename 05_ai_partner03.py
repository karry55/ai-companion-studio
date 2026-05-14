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
system_prompt = """
             你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。:
             规则:
               1.每次只回1条消息
               2.禁止任何场景或状态描述性文字
               3.匹配用户的语言
               4.回复简短，像微信聊天一样
               5.有需要的话可以用公等emoji表情
               6.用符合伴侣性格的方式对话
               7.回复的内容，要充分体现伴侣的性格特征
             伴侣性格:
               %s
               你必须严格遵守上述规则来回复用户。
             """

# 初始化聊天
if "messages" not in st.session_state:
    st.session_state.messages = []

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"

#性格
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的东北姑娘"

# 展示聊天信息
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

#左侧侧边栏 with是上下文管理器
with st.sidebar:
    st.sidebar.title("伴侣信息")
    #伴侣名称
    nick_name=st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框
    nature=st.text_area("性格",placeholder="请输入性格",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature


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
            {"role": "system", "content": system_prompt %(st.session_state.nick_name,st.session_state.nature)},
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
import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="😶‍🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={

    }
)


# 辅助函数：将时间字符串转换为安全的文件名
def safe_filename(time_str):
    """将 '2026-05-14 15:30:25' 转换为 '2026-05-14_15-30-25'"""
    return time_str.replace(":", "-").replace(" ", "_")


# 保存会话信息的函数
def save_session():
    if st.session_state.messages:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,  # 保持原始格式
            "messages": st.session_state.messages
        }
        # 如果sessions目录不存在,则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        # 使用安全文件名保存
        filename = f"sessions/{safe_filename(st.session_state.current_session)}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                # 返回去掉.json的文件名
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)   #排序,降序排序
    return session_list



# 加载指定的会话信息
def load_session(session_filename):
    """session_filename 是不带.json的安全文件名，如 '2026-05-14_15-30-25'"""
    try:
        filepath = f"sessions/{session_filename}.json"
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_data["current_session"]  # 恢复原始格式
                return True
    except Exception as e:
        st.error(f"加载会话失败: {e}")
        return False


# 删除会话信息函数
def delete_session(session_filename):
    """session_filename 是不带.json的安全文件名"""
    try:
        filepath = f"sessions/{session_filename}.json"
        if os.path.exists(filepath):
            os.remove(filepath)
            # 如果删除的是当前会话，清空消息并重置会话标识
            if session_filename == safe_filename(st.session_state.current_session):
                st.session_state.messages = []
                st.session_state.current_session = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("删除成功!")
            return True
    except Exception as e:
        st.error(f"删除失败: {e}")
        return False


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

# 昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"

# 性格
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的小姑娘"

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 展示聊天信息
st.text("当前会话: %s" % st.session_state.current_session)

# 显示聊天消息
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

# 左侧侧边栏
with st.sidebar:
    # 新建对话
    if st.button("新建对话", width="stretch", icon="👆"):
        # 保存当前对话信息（只有当有消息时才保存）
        if st.session_state.messages:
            save_session()

        # 清空消息并创建新会话
        st.session_state.messages = []
        st.session_state.current_session = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()

    # 会话历史
    st.subheader("会话历史")
    session_list = load_sessions()

    # 按时间倒序排列（最新的在前）
    session_list.sort(reverse=True)

    for session_filename in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            # 读取会话文件获取显示信息
            try:
                with open(f"sessions/{session_filename}.json", "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    # 显示格式：昵称 - 时间
                    display_text = f"{session_data['nick_name']} - {session_data['current_session']}"
            except:
                display_text = session_filename

            # 判断是否为当前会话（比较安全文件名）
            is_current = (session_filename == safe_filename(st.session_state.current_session))

            if st.button(display_text, width="stretch", icon="📜", key=f"load_{session_filename}",
                         type="primary" if is_current else "secondary"):
                if load_session(session_filename):
                    st.rerun()

        with col2:
            # 删除会话信息
            if st.button("❌", key=f"delete_{session_filename}"):
                if delete_session(session_filename):
                    st.rerun()

    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")

    # 伴侣名称
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name, key="nick_name_input")
    if nick_name != st.session_state.nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框
    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature, key="nature_input")
    if nature != st.session_state.nature:
        st.session_state.nature = nature

# 消息输入框
prompt = st.chat_input("请输入您要咨询的问题")

if prompt:
    # 显示用户消息
    with st.chat_message("user"):
        st.write(prompt)

    # 保存用户的输入
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True
    )

    # 输出大模型返回的结果(流式输出)
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                response_placeholder.write(full_response)

    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话信息
    save_session()
"""数据分析智能体"""
import matplotlib.pyplot as plt
import openpyxl
import pandas as pd
import streamlit as st
from utils import dataframe_agent

# 语言配置 - 中英文文本映射
LANG_CONFIG = {
    "zh": {
        "page_title": "数据分析智能体",
        "sidebar_title": "数据文件上传",
        "main_title": "AI分析结果",
        "history_title": "历史记录",
        "file_type_radio": "请选择数据文件类型:",
        "file_uploader": "上传你的{}数据文件",
        "sheet_radio": "请选择要加载的工作表：",
        "raw_data": "原始数据",
        "query_placeholder": "请输入你关于以上数据集的问题或数据可视化需求：",
        "button_text": "生成回答",
        "info_text": "请先上传数据文件",
        "spinner_text": "AI正在思考中，请稍等...",
        "history_upload": "用户上传了{}文件",
        "history_query": "用户查询: {}",
        "toggle_expand": "展开更多",
        "toggle_collapse": "收起"
    },
    "en": {
        "page_title": "AI Data Analysis",
        "sidebar_title": "Data File Upload",
        "main_title": "AI Analysis Results",
        "history_title": "History",
        "file_type_radio": "Select data file type:",
        "file_uploader": "Upload your {} data file",
        "sheet_radio": "Select the worksheet to load:",
        "raw_data": "Raw Data",
        "query_placeholder": "Enter your questions or data visualization requirements about the above dataset:",
        "button_text": "Generate Answer",
        "info_text": "Please upload a data file first",
        "spinner_text": "AI is thinking, please wait...",
        "history_upload": "User uploaded {} file",
        "history_query": "User query: {}",
        "toggle_expand": "Expand more",
        "toggle_collapse": "Collapse"
    }
}

# 初始化语言状态
if "language" not in st.session_state:
    st.session_state.language = "zh"

# 初始化历史记录
if "history" not in st.session_state:
    st.session_state.history = []

# 初始化折叠状态
if "is_expanded" not in st.session_state:
    st.session_state.is_expanded = False

# 添加历史记录函数
def add_to_history(event):
    st.session_state.history.append(event)

# 设置页面配置
st.set_page_config(
    page_title=LANG_CONFIG[st.session_state.language]["page_title"],
    page_icon="📊",
    layout="wide"
)

# 自定义 CSS 样式
st.markdown(
    """
    <style>
    /* 设置整体背景颜色和字体 */
    body {
        background-color: #f0f2f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2c3e50;
    }

    /* 设置卡片式容器基础样式 */
    .card-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 123, 255, 0.1);
    }
    .card-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 123, 255, 0.15);
    }

    /* 设置标题样式 */
    h2 {
        color: #1a73e8;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(26, 115, 232, 0.1);
    }

    /* 设置按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(26, 115, 232, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(26, 115, 232, 0.3);
    }

    /* 设置输入框样式 */
    .stTextArea>div>div>textarea {
        border: 2px solid rgba(26, 115, 232, 0.1);
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        transition: all 0.3s ease;
        background-color: white;
    }
    .stTextArea>div>div>textarea:focus {
        border-color: #1a73e8;
        box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.15);
    }

    /* 设置单选框样式 */
    .stRadio>label {
        font-size: 16px;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    .stRadio>div {
        background-color: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(26, 115, 232, 0.1);
    }

    /* 设置表格样式 */
    table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin: 16px 0;
    }
    th, td {
        border: 1px solid rgba(26, 115, 232, 0.1);
        padding: 12px;
        background-color: white;
    }
    th {
        background-color: rgba(26, 115, 232, 0.05);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 14px;
        color: #1a73e8;
    }
    tr:hover td {
        background-color: rgba(26, 115, 232, 0.02);
    }

    /* 设置历史记录区域样式 */
    .history-container {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
        border: 1px solid rgba(26, 115, 232, 0.1);
        transition: all 0.3s ease;
    }
    .history-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 123, 255, 0.15);
    }
    .history-container p {
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 8px;
        background-color: rgba(26, 115, 232, 0.05);
        border-left: 4px solid #1a73e8;
        font-size: 15px;
        line-height: 1.5;
        transition: all 0.3s ease;
    }
    .history-container p:hover {
        background-color: rgba(26, 115, 232, 0.08);
        transform: translateX(4px);
    }

    /* 设置文件上传区域样式 */
    .uploadedFile {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
        margin: 16px 0;
        border: 1px solid rgba(26, 115, 232, 0.1);
        transition: all 0.3s ease;
    }
    .uploadedFile:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 123, 255, 0.15);
    }

    /* 设置展开/折叠按钮样式 */
    .stExpander>div>div>div>div>div>button {
        background-color: transparent;
        border: none;
        color: #1a73e8;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stExpander>div>div>div>div>div>button:hover {
        color: #0d47a1;
        text-decoration: underline;
    }

    /* 设置侧边栏样式 */
    .css-1d391kg {
        background-color: white;
        border-right: 1px solid rgba(26, 115, 232, 0.1);
        padding: 2rem;
    }

    /* 设置主要内容区域样式 */
    .main .block-container {
        padding: 2rem;
        max-width: 100%;
    }

    /* 设置数据预览区域样式 */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
        border: 1px solid rgba(26, 115, 232, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

def create_chart(input_data, chart_type):
    """生成统计图表"""
    df_data = pd.DataFrame(
        data={
            "x": input_data["columns"],
            "y": input_data["data"]
        }
    ).set_index("x")
    if chart_type == "bar":
        plt.figure(figsize=(8, 5), dpi=120)
        plt.bar(input_data["columns"], input_data["data"], width=0.4, hatch='///')
        st.pyplot(plt.gcf())
    elif chart_type == "line":
        st.line_chart(df_data)

# 主区域右上角语言切换
col1, col2 = st.columns([3, 1])
with col2:
    lang_option = st.radio(
        "",
        ("中文", "English"),
        key="lang_radio",
        horizontal=True
    )
    if lang_option == "中文" and st.session_state.language != "zh":
        st.session_state.language = "zh"
        st.rerun()
    elif lang_option == "English" and st.session_state.language != "en":
        st.session_state.language = "en"
        st.rerun()

# 侧边栏
with st.sidebar:
    st.title(LANG_CONFIG[st.session_state.language]["sidebar_title"])
    
    # 文件类型选择和上传
    option = st.radio(
        LANG_CONFIG[st.session_state.language]["file_type_radio"],
        ("单文件分析", "多文件数据合并", "数据表连接(JOIN操作)")
    )
    file_type = "xlsx" if option == "单文件分析" else "csv"
    data = st.file_uploader(
        LANG_CONFIG[st.session_state.language]["file_uploader"].format(option),
        type=file_type
    )

    if data:
        if file_type == "xlsx":
            wb = openpyxl.load_workbook(data)
            option = st.radio(
                LANG_CONFIG[st.session_state.language]["sheet_radio"],
                options=wb.sheetnames
            )
            st.session_state["df"] = pd.read_excel(data, sheet_name=option)
        else:
            st.session_state["df"] = pd.read_csv(data)

        # 添加上传历史记录
        add_to_history(LANG_CONFIG[st.session_state.language]["history_upload"].format(option))

        with st.expander(LANG_CONFIG[st.session_state.language]["raw_data"]):
            st.dataframe(st.session_state["df"])

# 主区域分为左右两列
main_col1, main_col2 = st.columns([2, 1])

# 左侧列：分析结果
with main_col1:
    st.write(f"## {LANG_CONFIG[st.session_state.language]['main_title']}")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    query = st.text_area(
        LANG_CONFIG[st.session_state.language]["query_placeholder"],
        disabled="df" not in st.session_state
    )
    button = st.button(LANG_CONFIG[st.session_state.language]["button_text"])

    if button and not data:
        st.info(LANG_CONFIG[st.session_state.language]["info_text"])
        st.stop()

    if query:
        # 添加查询历史记录
        add_to_history(LANG_CONFIG[st.session_state.language]["history_query"].format(query))

        with st.spinner(LANG_CONFIG[st.session_state.language]["spinner_text"]):
            result = dataframe_agent(st.session_state["df"], query)
            if "answer" in result:
                st.write(result["answer"])
            if "table" in result:
                st.table(pd.DataFrame(result["table"]["data"],
                                    columns=result["table"]["columns"]))
            if "bar" in result:
                create_chart(result["bar"], "bar")
            if "line" in result:
                create_chart(result["line"], "line")
    st.markdown('</div>', unsafe_allow_html=True)

# 右侧列：历史记录
with main_col2:
    st.write(f"## {LANG_CONFIG[st.session_state.language]['history_title']}")
    with st.container():
        st.markdown('<div class="history-container">', unsafe_allow_html=True)
        query_history = [event for event in st.session_state.history if "用户查询" in event or "User query" in event]
        if len(query_history) > 2:
            if st.session_state.is_expanded:
                for event in query_history:
                    st.write(event)
                if st.button(LANG_CONFIG[st.session_state.language]["toggle_collapse"]):
                    st.session_state.is_expanded = False
                    st.experimental_rerun()
            else:
                for event in query_history[:2]:
                    st.write(event)
                if st.button(LANG_CONFIG[st.session_state.language]["toggle_expand"]):
                    st.session_state.is_expanded = True
                    st.experimental_rerun()
        else:
            for event in query_history:
                st.write(event)
        st.markdown('</div>', unsafe_allow_html=True)

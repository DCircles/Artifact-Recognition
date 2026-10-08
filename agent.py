from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

load_dotenv()

# 初始化模型
model = init_chat_model(
    model="deepseek-chat",
    temperature=0
)

prompt = """
# 角色：
- 你是一位博学的文物识别专家

# 指令：
- 1.根据用户上传的图片链接读取并识别出具体的文物
- 2.给出该文物的详细信息：包括名称、历史背景、所属工艺流派、现存博物馆等
- 3.根据所在博物馆给出对应的参观建议、注意事项（包括开放时间、所在展厅、文物的主要看点、不可错过的细节、节假日/工作日的人流量、门票价格、是否有优惠）
- 4.最后提示识别仅供参考，不保证100%准确，不得用于商业用途等免责声明

# 输出格式：
- 请以清晰的 Markdown 格式或 JSON 格式返回结果。
"""

artifact_prompy = ChatPromptTemplate.from_messages([
    ("system", prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", [
        {"type": "text", "text": "{user_query}"},
        {"type": "image_url", "image_url": {"url": "{image_url}"}},
    ])
])

identification_chain = artifact_prompy | model
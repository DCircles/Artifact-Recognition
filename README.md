# 文物识别 Agent

一个基于深度学习和大语言模型的智能文物识别系统，通过上传文物图片即可获得专业的文物解读和参观建议。

## 📋 项目简介

本项目是一个智能文物识别应用，用户可以上传文物图片，系统会：
- 识别图片中的文物
- 提供详细的文物信息（名称、历史背景、工艺流派、现存博物馆等）
- 根据文物所在博物馆提供参观建议（开放时间、展厅位置、门票价格等）
- 支持多轮对话，记住用户的查询历史
- 图片自动上传至阿里云 OSS，生成临时访问链接

## 🛠️ 技术栈

- **后端框架**: FastAPI
- **AI模型**: DeepSeek Chat (通过 LangChain 集成)
- **图片存储**: 阿里云 OSS (对象存储服务)
- **数据库**: SQLite (本地存储对话历史和图片缓存)
- **前端**: Vue 3 + Element Plus

[//]: # (- **可观测性**: LangSmith &#40;追踪和监控&#41;)
- **Python版本**: >= 3.13

## 📦 安装依赖

本项目使用 `uv` 作为包管理工具：

```bash
# 安装 uv (如果尚未安装)
pip install uv

# 安装项目依赖
uv sync
```

## 🔧 环境配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```env
# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key

# 阿里云 OSS 配置 (必需，用于图片存储)
OSS_ACCESS_KEY_ID=your_oss_access_key_id
OSS_ACCESS_KEY_SECRET=your_oss_access_key_secret
OSS_ENDPOINT=your_oss_endpoint
OSS_BUCKET_NAME=your_oss_bucket_name

# LangSmith 配置 (已注释，用于追踪和调试)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_project_name
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# TAVILY API Key (没用上)
TAVILY_API_KEY=your_tavily_api_key

# 和风天气 API Key (没用上)
QWEATHER_API_KEY=your_qweather_api_key
```

## 🚀 启动应用

```bash
# 方式1: 直接运行
python main.py

# 方式2: 使用 uvicorn
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

应用启动后：
API 服务: http://127.0.0.1:8080
前端页面: http://127.0.0.1:8080/static/index.html


## 📡 API 接口

### POST `/identify` - 文物识别

上传文物图片并获取识别结果。

**请求参数:**
- `user_id` (form-data, string, 必填): 用户ID
- `file` (form-data, file, 必填): 上传的图片文件 (支持 JPG/JPEG/PNG/WEBP 格式)
- `user_query` (form-data, string, 可选): 用户问题，默认为"请识别图中的文物"

**响应示例:**
```json
{
  "status": "success",
  "user_id": "user123",
  "result": "## 文物识别结果\n\n### 文物信息\n- **名称**: ...\n- **历史背景**: ...\n..."
}
```

**缓存机制:**
- 系统会对相同图片+问题的查询进行缓存
- 重复查询会直接返回缓存结果，提升响应速度

## 📁 项目结构

```
Agent/
├── main.py              # FastAPI 应用入口和路由定义
├── agent.py             # AI Agent 核心逻辑 (模型初始化、提示词、链式调用)
├── memory.py            # 记忆模块 (对话历史存储、图片缓存)
├── oss_utils.py         # 阿里云 OSS 工具模块 (图片上传、临时链接生成)
├── pyproject.toml       # 项目依赖配置
├── .env                 # 环境变量配置
├── artifact_memory.db   # SQLite 数据库文件 (自动生成)
└── static/
    └── index.html       # 前端页面 (Vue 3 + Element Plus)
```

🔍 核心功能
1. 文物识别
基于 DeepSeek 视觉模型识别图片中的文物
提供结构化的文物信息输出
2. 图片云存储
图片自动上传至阿里云 OSS
生成一小时有效期的临时访问链接
保证图片访问的安全性和隐私性
3. 对话历史
支持多用户对话历史管理
自动保存最近 5 条对话记录用于上下文理解
4. 图片缓存
基于图片 MD5 哈希实现智能缓存
避免重复计算，提升性能
5. 前端界面
基于 Vue 3 + Element Plus 构建
支持图片上传预览、Markdown 格式渲染
简洁友好的用户交互体验
6. 可观测性
集成 LangSmith 实现全链路追踪
方便调试和优化 Agent 性能
📝 使用示例
方式1: 使用前端页面
访问 http://127.0.0.1:8080/static/index.html，
在界面上：
输入用户ID
上传文物图片
可选填写补充描述
点击"开始识别"按钮

方式2: 使用 curl 发送请求
```bash
curl -X POST "http://127.0.0.1:8080/identify" \
  -F "user_id=user123" \
  -F "file=@path/to/your/image.jpg" \
  -F "user_query=请识别图中的文物"
```

## ⚠️ 注意事项

- 文物识别结果仅供参考，不保证100%准确
- 识别结果不得用于商业用途
- 建议结合专业资料进行深入研究
- 请确保阿里云 OSS 配置正确，否则图片上传功能将无法使用



```
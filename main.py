import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.params import Form
from fastapi.responses import JSONResponse
# CORS中间件，解决跨域问题
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from agent import identification_chain
from memory import save_message, save_assistant_messages, get_history, calc_img_hash, get_history_hash
from oss_utils import upload_to_oss

app = FastAPI(title="文物识别 Agent", description="一个用于识别文物的 FastAPI 应用")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # 允许的来源
    allow_credentials=True,  # 是否允许验证
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)

@app.post("/identify")
async def artifact_identify(
    user_id: str = Form(..., description="用户ID"),
    file: UploadFile = File(..., description="用户上传的图片"),
    user_query: str = Form("请识别图中的文物", description="用户提出的问题")
):
    if file.content_type not in ["image/png", "image/jpg", "image/jpeg", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="仅支持解析格式为 JPG/JPEG/PNG/WEBP 的图片"
        )
    try:
        image_bytes = await file.read()
        image_hash = calc_img_hash(image_bytes)
        image_url, image_name = upload_to_oss(image_bytes, file.filename)

        # 获取历史数据
        history = get_history(user_id)
        # 是否存在重复图片+问题
        repeat_history = get_history_hash(user_id, image_hash, user_query)
        print(repeat_history)
        # 命中
        if repeat_history:
            content = repeat_history
            save_message(user_id, "user", f"{user_query}[上传了图片]")
            save_message(user_id, "assistant", content)
            return {
                "status": "success",
                "source": "cache",
                "user_id": user_id,
                "result": content
            }
        # 新图片
        responses = await identification_chain.ainvoke({
            "history": history,
            "user_query": user_query,
            "image_url": image_url
        })
        #保存对话
        ai_content = responses.content
        save_message(user_id, "user", f"{user_query}:{image_name}")
        save_message(user_id, "assistant", ai_content)
        save_assistant_messages(user_id, image_hash, user_query, ai_content)

        return {
            "status": 'success',
            "user_id": user_id,
            "result": ai_content
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": 'error', "detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
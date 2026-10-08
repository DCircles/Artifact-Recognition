import oss2
from dotenv import load_dotenv
import os

# 加载配置
load_dotenv()

auth = oss2.Auth(os.getenv("OSS_ACCESS_KEY_ID"), os.getenv("OSS_ACCESS_KEY_SECRET"))
bucket = oss2.Bucket(auth, os.getenv("OSS_ENDPOINT"), os.getenv("OSS_BUCKET_NAME"))

try:
    # 列出 Bucket 里的文件
    for obj in oss2.ObjectIterator(bucket):
        pass
    print("✅ OSS 连接成功！配置正确。")
except oss2.exceptions.OssError as e:
    print(f"❌ 连接失败: {e}")
import oss2
import os
from dotenv import load_dotenv
import uuid  # 通用唯一识别码

load_dotenv()

auth = oss2.Auth(os.getenv("OSS_ACCESS_KEY_ID"), os.getenv("OSS_ACCESS_KEY_SECRET"))
bucket = oss2.Bucket(auth, os.getenv("OSS_ENDPOINT"), os.getenv("OSS_BUCKET_NAME"))


""" 把图片（二进制格式）上传到OSS """
def upload_to_oss(file_bytes, original_filename):
    # 生成唯一文件名
    ext_name = os.path.splitext(original_filename)[1]
    file_name = f"artifact/{uuid.uuid4().hex}{ext_name}"

    try:
        bucket.put_object(file_name, file_bytes)
        # url = f"http:{os.getenv("OSS_BUCKET_NAME")}.{os.getenv("OSS_ENDPOINT").replace('http://', '').replace('https://', '')}/{file_name}"
        # 有效期为一小时的访问链接（私有访问权限）
        url = bucket.sign_url('GET', file_name, 3600)
        return url, file_name
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return None, None

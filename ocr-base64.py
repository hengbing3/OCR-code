from paddlex import create_pipeline
import base64
import numpy as np
from PIL import Image
import io
import os

# 创建 OCR 产线对象
pipeline = create_pipeline(pipeline="ocr", device="cpu")

# 读取图片并进行 base64 编码（模拟客户端操作）
with open("/Users/christer/Downloads/general_ocr_001.png", "rb") as image_file:
    base64_str = base64.b64encode(image_file.read()).decode('utf-8')

# 服务端接收到 base64 字符串，进行解码
img_data = base64.b64decode(base64_str)
# 将字节数据转换为 PIL 图像
image = Image.open(io.BytesIO(img_data)).convert('RGB')
# 将 PIL 图像转换为 numpy.ndarray
image_array = np.array(image)

# 调用 predict 方法进行预测
output = pipeline.predict(image_array)

# 确保输出目录存在
output_dir = "./output/"
os.makedirs(output_dir, exist_ok=True)

# 处理并保存结果
for res in output:
    res.print()
    res.save_to_img(output_dir)
    res.save_to_json(output_dir)

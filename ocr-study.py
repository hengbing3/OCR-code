from paddlex import create_pipeline

import io
import base64
import os
from PIL import Image


pipeline = create_pipeline(pipeline="ocr",device="cpu")

output = pipeline.predict("/Users/christer/Downloads/general_ocr_001.png")

for res in output:
    res.print()
    res.save_to_img("./output/")
    res.save_to_json("./output/")
    # 检查 res 对象有哪些属性
    print(dir(res))

    # 获取结果图像
result_image = res.img

if result_image is None:
    print("无法获取结果图像。")
else:
    # 创建字节流对象
    img_buffer = io.BytesIO()
    # 将图像保存到字节流中，格式可根据需要调整（如 'PNG'、'JPEG'）
    result_image.save(img_buffer, format='PNG')
    # 获取字节数据
    img_bytes = img_buffer.getvalue()
    # 将字节数据编码为 Base64 字符串
    img_base64_str = base64.b64encode(img_bytes).decode('utf-8')
    
    # 打印 Base64 字符串（可选）
    print("Base64 编码的图像字符串：")
    print(img_base64_str)
    
    # 保存 Base64 字符串到文件
    base64_file_path = './output/result_image_base64.txt'
    os.makedirs(os.path.dirname(base64_file_path), exist_ok=True)
    with open(base64_file_path, 'w') as f:
        f.write(img_base64_str)
    print(f"Base64 编码的图像已保存到 {base64_file_path}")
    
    # 也可以将图像直接保存为文件
    image_file_path = './output/result_image.png'
    result_image.save(image_file_path)
    print(f"结果图像已保存到 {image_file_path}")

        

# from paddlex import create_model
# model = create_model("PP-OCRv4_mobile_rec")
# output = model.predict("/Users/christer/Downloads/general_ocr_001.png", batch_size=1)
# for res in output:
#     res.print(json_format=False)
#     res.save_to_img("./output/")
#     res.save_to_json("./output/res.json")
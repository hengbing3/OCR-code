from flask import Flask, request, jsonify, make_response
from paddlex import create_pipeline
import base64
import logging
import json
import io
import os
import requests
import numpy as np
from PIL import Image

# 创建 Flask 应用
app = Flask(__name__)

# 创建 OCR 产线对象
pipeline = create_pipeline(pipeline="ocr", device="cpu")

# 设置日志级别为 INFO
logging.basicConfig(level=logging.INFO)

# 定义 /ocr 路由，接受 POST 请求
@app.route('/ocr', methods=['POST'])
def ocr_infer():
    try:
        # 获取请求体中的 JSON 数据
        data = request.get_json()
        if not data:
            # 如果请求体为空，返回错误响应，设置 ensure_ascii=False 确保中文不被转义
            return make_response(json.dumps({
                "errorCode": 400,
                "errorMsg": "无效的 JSON 请求"
            }, ensure_ascii=False), 400, {'Content-Type': 'application/json; charset=utf-8'})

        # 获取图像数据，可能是 'img'（图片路径）、'image'（URL或Base64）、'img_base64'（Base64）
        image_data_list = data.get('img') or data.get('image') or data.get('img_base64')
        if not image_data_list:
            # 如果没有提供图像数据，返回错误响应
            return make_response(json.dumps({
                "errorCode": 400,
                "errorMsg": "请求中缺少 'img'、'image' 或 'img_base64'"
            }, ensure_ascii=False), 400, {'Content-Type': 'application/json; charset=utf-8'})

        # 确保 image_data_list 是列表类型，如果是单个数据则转换为列表
        if not isinstance(image_data_list, list):
            image_data_list = [image_data_list]

        # 解析推理参数
        inference_params = data.get('inferenceParams', {})
        max_long_side = inference_params.get('maxLongSide')

        # 存储处理后的图像数据
        images_to_predict = []

        for image_data in image_data_list:
            image = None  # 初始化图像变量

            # 判断 image_data 是否为本地文件路径
            if isinstance(image_data, str) and os.path.exists(image_data):
                # 从本地路径读取图像
                image = Image.open(image_data).convert('RGB')
            elif isinstance(image_data, str) and (image_data.startswith('http://') or image_data.startswith('https://')):
                # 如果是 URL，下载图像
                try:
                    response = requests.get(image_data)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content)).convert('RGB')
                except Exception as e:
                    logging.error(f"无法从 URL 下载图像: {e}")
                    continue  # 跳过此图像，处理下一个
            else:
                # 尝试将其作为 base64 编码的图像处理
                try:
                    img_data = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(img_data)).convert('RGB')
                except Exception as e:
                    logging.error(f"无法解码 base64 图像: {e}")
                    continue  # 跳过此图像，处理下一个

            if image is None:
                logging.error("无法加载图像")
                continue  # 跳过此图像，处理下一个

            # 可选：调整图像大小
            if max_long_side:
                # 计算缩放比例
                scale = max_long_side / max(image.size)
                if scale < 1:
                    new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
                    image = image.resize(new_size, Image.ANTIALIAS)

            # 将 PIL 图像转换为 numpy.ndarray
            image_array = np.array(image)
            images_to_predict.append(image_array)

        # 如果没有有效的图像数据，返回错误响应
        if not images_to_predict:
            return make_response(json.dumps({
                "errorCode": 400,
                "errorMsg": "没有有效的图像可供处理"
            }, ensure_ascii=False), 400, {'Content-Type': 'application/json; charset=utf-8'})

        # 调用 predict 方法进行预测，传入图像数据列表
        outputs = pipeline.predict(images_to_predict)

        results = []

        # 处理预测结果
        for res in outputs:
            print(res)
            res.save_to_img("./output/")
            # 从结果中获取检测到的多边形、识别的文本和得分
            dt_polys = res['dt_polys']      # 文本检测的多边形顶点坐标
            rec_text = res['rec_text']      # 识别的文本内容
            rec_score = res['rec_score']    # 识别得分

            result_texts = []
            # 遍历每个检测结果，组合多边形、文本和得分
            for poly, text, score in zip(dt_polys, rec_text, rec_score):
                result_texts.append({
                    "poly": poly.tolist(),  # 将多边形坐标转换为列表
                    "text": text,           # 文本内容
                    "score": score          # 识别得分
                })

            # 获取结果图像并进行 Base64 编码
            # 获取结果图像
            result_image = res.img

            if result_image is None:
                print("无法获取结果图像。")
            else:
                # 创建字节流对象
                img_buffer = io.BytesIO()
                # 将图像保存到字节流中，格式可根据需要调整（如 'PNG'、'JPEG'）
                result_image.save(img_buffer, format='JPEG')
                # 获取字节数据
                img_bytes = img_buffer.getvalue()
                # 将字节数据编码为 Base64 字符串
                img_base64_str = base64.b64encode(img_bytes).decode('utf-8')
    
                # 打印 Base64 字符串（可选）
                print("Base64 编码的图像字符串：")
                print(img_base64_str)

                # # 保存 Base64 字符串到文件
                # base64_file_path = './output/result_image_base64.txt'
                # os.makedirs(os.path.dirname(base64_file_path), exist_ok=True)
                # with open(base64_file_path, 'w') as f:
                #     f.write(img_base64_str)
                # print(f"Base64 编码的图像已保存到 {base64_file_path}")
    
                # # 也可以将图像直接保存为文件
                # image_file_path = './output/result_image.png'
                # result_image.save(image_file_path)
                # print(f"结果图像已保存到 {image_file_path}")

            # 将单张图像的结果添加到结果列表中
            results.append({
                "texts": result_texts,     # 文本检测和识别结果
                "image": img_base64_str      # 可视化的结果图像（Base64 编码）
            })

        # 构建响应体
        response = {
            "errorCode": 0,
            "errorMsg": "Success",
            "result": results  # 包含所有图像的结果列表
        }

        # 将响应体序列化为 JSON 字符串，设置 ensure_ascii=False，避免中文被转义
        json_str = json.dumps(response, ensure_ascii=False)
        # 返回响应，设置 Content-Type 为 'application/json; charset=utf-8'
        return make_response(json_str, 200, {'Content-Type': 'application/json; charset=utf-8'})

    except Exception as e:
        # 捕获异常，记录错误日志
        logging.error(f"内部服务器错误: {e}")
        # 构建错误响应
        error_response = {
            "errorCode": 500,
            "errorMsg": "Internal server error"
        }
        # 将错误响应序列化为 JSON 字符串，设置 ensure_ascii=False
        json_str = json.dumps(error_response, ensure_ascii=False)
        # 返回错误响应
        return make_response(json_str, 500, {'Content-Type': 'application/json; charset=utf-8'})

# 启动 Flask 应用，监听 6666 端口
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666)

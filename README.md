# OCR 服务端应用

> 该项目是一个基于 Flask 和 PaddleX 的 OCR（光学字符识别）服务端应用。它提供了一个 `/ocr` 接口，支持通过图片路径、URL 或 Base64 编码的图片进行文字识别，并返回识别结果和可视化的结果图像。

## 功能特性

- **多种图片输入方式**：支持本地图片路径、网络图片 URL、Base64 编码的图片数据。
- **批量处理**：一次请求可处理多张图片，提高处理效率。
- **结果返回**：返回识别的文本、位置、多边形坐标、识别得分，以及可视化的结果图像（Base64 编码）。
- **错误处理**：对异常情况进行捕获和处理，确保服务稳定运行。

## 目录

- [OCR 服务端应用](#ocr-服务端应用)
  - [功能特性](#功能特性)
  - [目录](#目录)
  - [安装依赖](#安装依赖)
  - [API 使用指南](#api-使用指南)
    - [请求地址](#请求地址)
    - [请求方法](#请求方法)
    - [请求参数](#请求参数)
    - [响应结果](#响应结果)
    - [示例请求](#示例请求)
      - [1. 使用本地图片路径](#1-使用本地图片路径)
      - [2. 使用图片 URL](#2-使用图片-url)
      - [3. 使用 Base64 编码的图片](#3-使用-base64-编码的图片)
    - [示例响应](#示例响应)
    - [注意事项](#注意事项)

## 安装依赖

在运行该项目之前，请确保已安装以下 Python 库以及相关环境：

```bash
pip install paddlepaddle==3.0.0b1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/whl/paddlex-3.0.0b1-py3-none-any.whl

pip install ujson

pip install flask numpy pillow requests
#flask：用于创建 Web 服务。
#numpy 和 pillow：用于图像处理。
#requests：用于处理网络请求（下载图片）。
```

## API 使用指南

### 请求地址

```bash
POST http://localhost:6666/ocr
```
### 请求方法
- post
### 请求参数

请求体为 JSON 格式，支持以下字段：

- img：图片路径或图片路径列表（本地路径）。
- image：图片 URL 或图片 URL 列表。
- img_base64：Base64 编码的图片数据或列表。
- inferenceParams（可选）：推理参数，支持以下字段：
  - maxLongSide：指定图像的最长边，用于调整图像大小。
### 响应结果
响应为 JSON 格式，包含以下字段：

- errorCode：错误码，0 表示成功，非 0 表示失败。
- errorMsg：错误信息。
- result：识别结果列表，每个元素对应一张输入的图片，包含：
- texts：识别的文本列表，每个元素包含：
  - poly：文本区域的多边形顶点坐标。
  - text：识别的文本内容。
  - score：识别得分。
- image：可视化的结果图像（Base64 编码）。

### 示例请求

#### 1. 使用本地图片路径

```json
  {
  "img": [
    "/path/to/local/image1.jpg",
    "/path/to/local/image2.jpg"
  ],
  "inferenceParams": {
    "maxLongSide": 960
  }
}
```

#### 2. 使用图片 URL

```json
  {
  "image": [
    "http://example.com/image1.jpg",
    "http://example.com/image2.jpg"
  ],
  "inferenceParams": {
    "maxLongSide": 960
  }
}
```

#### 3. 使用 Base64 编码的图片

```json
{
  "img_base64": [
    "iVBORw0KGgoAAAANSUhEUgAA...",
    "iVBORw0KGgoAAAANSUhEUgAA..."
  ],
  "inferenceParams": {
    "maxLongSide": 960
  }
}
```

### 示例响应

```json
{
  "errorCode": 0,
  "errorMsg": "Success",
  "result": [
    {
      "texts": [
        {
          "poly": [[x1, y1], [x2, y2], ...],
          "text": "识别的文本内容1",
          "score": 0.95
        },
        {
          "poly": [[x1, y1], [x2, y2], ...],
          "text": "识别的文本内容2",
          "score": 0.90
        }
      ],
      "image": "<Base64 编码的结果图像1>"
    },
    {
      "texts": [
        {
          "poly": [[x1, y1], [x2, y2], ...],
          "text": "识别的文本内容3",
          "score": 0.93
        }
      ],
      "image": "<Base64 编码的结果图像2>"
    }
  ]
}
```

### 注意事项

- 图片路径：当使用 img 参数传递本地图片路径时，确保服务端有权限访问这些路径，且路径格式正确。
- 图片 URL：当使用 image 参数传递图片 URL 时，确保 URL 可访问，且图片格式受支持。
- Base64 编码：当使用 img_base64 参数传递 Base64 编码的图片时，确保编码正确，无额外的前缀或换行符。
- 字符编码：为了避免中文字符显示乱码，响应中设置了 ensure_ascii=False，并指定了 utf-8 编码。

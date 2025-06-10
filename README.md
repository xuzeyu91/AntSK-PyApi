# Embedding API

基于FastAPI的文本嵌入向量生成API，支持多种embedding模型。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
python main.py
```

或者使用uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API接口

### 生成嵌入向量

**POST** `/v1/embeddings`

#### 请求参数

```json
{
    "model": "BAAI/bge-m3",
    "input": ["你好", "你"]
}
```

#### 响应格式

```json
{
    "data": [
        {
            "object": "embedding",
            "index": 0,
            "embedding": [0.1, 0.2, 0.3, ...]
        },
        {
            "object": "embedding",
            "index": 1,
            "embedding": [0.4, 0.5, 0.6, ...]
        }
    ],
    "object": "list",
    "model": "modelname",
    "usage": {
        "prompt_tokens": 9,
        "total_tokens": 9
    }
}
```

### 文档重排序

**POST** `/v1/rerank`

#### 请求参数

```json
{
    "model": "BAAI/bge-reranker-v2-m3",
    "query": "Apple",
    "documents": [
        "apple",
        "banana",
        "fruit",
        "vegetable"
    ],
    "top_n": 4,
    "return_documents": false,
    "max_chunks_per_doc": 1024,
    "overlap_tokens": 80
}
```

#### 参数说明

- `model`: 重排序模型名称
- `query`: 查询文本
- `documents`: 待排序的文档列表
- `top_n`: 返回前N个结果（可选，默认返回所有）
- `return_documents`: 是否在结果中返回文档内容（默认false）
- `max_chunks_per_doc`: 每个文档的最大块数（可选）
- `overlap_tokens`: 重叠token数（可选）

#### 响应格式

```json
{
    "id": "uuid-string",
    "results": [
        {
            "document": {
                "text": "apple"
            },
            "index": 0,
            "relevance_score": 0.95
        },
        {
            "document": {
                "text": "fruit"
            },
            "index": 2,
            "relevance_score": 0.85
        }
    ],
    "tokens": {
        "input_tokens": 15,
        "output_tokens": 0
    }
}
```

### 其他接口

- **GET** `/` - 根路径，返回API状态
- **GET** `/health` - 健康检查
- **GET** `/models` - 查看已加载的模型列表
- **GET** `/docs` - Swagger API文档

## 使用示例

### Python客户端

```python
import requests

url = "http://localhost:8000/v1/embeddings"
data = {
    "model": "BAAI/bge-large-zh-v1.5",
    "input": ["你好", "你"]
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### curl命令

```bash
curl -X POST "http://localhost:8000/v1/embeddings" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "BAAI/bge-large-zh-v1.5",
       "input": ["你好", "你"]
     }'
```

## 配置说明

### 环境变量配置

可以通过环境变量来配置API服务：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `MODEL_STORAGE_PATH` | `D:\git\AntBlazor\model` | 模型路径信息存储目录 |
| `API_HOST` | `0.0.0.0` | API服务监听地址 |
| `API_PORT` | `8000` | API服务端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `USE_FP16` | `true` | 是否使用FP16精度 |

### 启动方式

1. **使用批处理文件（推荐）**：
   ```bash
   start.bat
   ```

2. **直接启动**：
   ```bash
   python start.py
   ```

3. **自定义环境变量启动**：
   ```bash
   set MODEL_STORAGE_PATH=你的路径
   python start.py
   ```

### 其他配置

- 支持的模型：任何FlagEmbedding兼容的模型
- 模型会自动下载并缓存路径信息

## 注意事项

1. 首次使用某个模型时会自动下载，请确保网络连接正常
2. 模型会被缓存在本地，避免重复下载
3. 大模型可能需要较多内存，请根据服务器配置选择合适的模型 
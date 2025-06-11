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

## 🐳 Docker 部署

### 📦 构建镜像

#### 方法一：使用 Docker 命令
```bash
# 构建镜像
docker build -t antsk-py-api:latest .

# 运行容器
docker run -d \
  --name antsk-py-api \
  -p 8000:8000 \
  -v ./models:/app/models \
  -e MODEL_STORAGE_PATH=/app/models \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  -e LOG_LEVEL=INFO \
  -e USE_FP16=true \
  antsk-py-api:latest
```

#### 方法二：使用 Docker Compose（推荐）
```bash
# 构建并启动服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

### 🔧 Docker环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MODEL_STORAGE_PATH` | `/app/models` | 模型存储路径 |
| `API_HOST` | `0.0.0.0` | API服务监听地址 |
| `API_PORT` | `8000` | API服务端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `USE_FP16` | `true` | 是否使用FP16精度 |

### 📁 数据卷挂载

- `./models:/app/models` - 模型存储目录，避免重复下载
- `./logs:/app/logs` - 日志目录（可选）

### 🌐 Docker访问地址

容器启动后，您可以通过以下地址访问服务：

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **模型列表**: http://localhost:8000/models
- **配置信息**: http://localhost:8000/config

### 🔍 Docker常用命令

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f antsk-py-api

# 进入容器
docker-compose exec antsk-py-api bash

# 重新构建镜像
docker-compose build --no-cache

# 清理未使用的镜像
docker image prune -f
```

### 🚀 Docker环境API测试

#### 生成嵌入向量
```bash
curl -X POST "http://localhost:8000/v1/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "BAAI/bge-small-zh-v1.5",
    "input": ["你好世界", "Hello World"]
  }'
```

#### 文档重排序
```bash
curl -X POST "http://localhost:8000/v1/rerank" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "BAAI/bge-reranker-base",
    "query": "什么是人工智能？",
    "documents": [
      "人工智能是计算机科学的一个分支",
      "今天天气很好",
      "机器学习是人工智能的子领域"
    ],
    "top_n": 2
  }'
```

### ⚠️ Docker注意事项

1. **首次运行**：首次启动时会自动下载模型，可能需要较长时间
2. **存储空间**：确保有足够的磁盘空间存储模型文件
3. **内存要求**：建议至少4GB内存，使用FP16可以减少内存占用
4. **网络访问**：需要网络连接来下载模型文件

### 🐛 故障排除

#### 容器无法启动
```bash
# 查看详细日志
docker-compose logs antsk-py-api

# 检查端口占用
netstat -tulpn | grep 8000
```

#### 模型下载失败
```bash
# 检查网络连接
docker-compose exec antsk-py-api ping huggingface.co

# 手动重新下载模型
docker-compose exec antsk-py-api rm -rf /app/models/*
docker-compose restart
``` 
# Docker 使用说明

## 📦 构建镜像

### 方法一：使用 Docker 命令
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

### 方法二：使用 Docker Compose（推荐）
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

## 🔧 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MODEL_STORAGE_PATH` | `/app/models` | 模型存储路径 |
| `API_HOST` | `0.0.0.0` | API服务监听地址 |
| `API_PORT` | `8000` | API服务端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `USE_FP16` | `true` | 是否使用FP16精度 |

## 📁 数据卷挂载

- `./models:/app/models` - 模型存储目录，避免重复下载
- `./logs:/app/logs` - 日志目录（可选）

## 🌐 访问地址

容器启动后，您可以通过以下地址访问服务：

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **模型列表**: http://localhost:8000/models
- **配置信息**: http://localhost:8000/config

## 🔍 常用命令

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

## 🚀 API 使用示例

### 生成嵌入向量
```bash
curl -X POST "http://localhost:8000/v1/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "BAAI/bge-small-zh-v1.5",
    "input": ["你好世界", "Hello World"]
  }'
```

### 文档重排序
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

## ⚠️ 注意事项

1. **首次运行**：首次启动时会自动下载模型，可能需要较长时间
2. **存储空间**：确保有足够的磁盘空间存储模型文件
3. **内存要求**：建议至少4GB内存，使用FP16可以减少内存占用
4. **网络访问**：需要网络连接来下载模型文件

## 🐛 故障排除

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs antsk-py-api

# 检查端口占用
netstat -tulpn | grep 8000
```

### 模型下载失败
```bash
# 检查网络连接
docker-compose exec antsk-py-api ping huggingface.co

# 手动重新下载模型
docker-compose exec antsk-py-api rm -rf /app/models/*
docker-compose restart
``` 
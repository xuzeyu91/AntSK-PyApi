# AntSK Python Embedding API

🚀 基于FastAPI、FlagEmbedding的高性能文本嵌入向量生成与文档重排序API，支持多种embedding和rerank模型。

## ✨ 功能特性

- 🧠 **多模型支持**: 支持FlagEmbedding系列的所有embedding和rerank模型
- ⚡ **高性能**: 模型智能缓存，避免重复加载
- 🔧 **灵活配置**: 支持环境变量和配置文件
- 📊 **完整监控**: 健康检查、模型列表、配置查看
- 🐳 **容器化**: 完整的Docker和Docker Compose支持
- 🛡️ **错误处理**: 全局异常处理和输入验证
- 📝 **标准API**: 兼容OpenAI API格式

## 🔧 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

#### 方法一：使用Python脚本（推荐）
```bash
python start.py
```

#### 方法二：使用批处理文件（Windows）
```bash
start.bat
```

#### 方法三：直接使用uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **模型列表**: http://localhost:8000/models

## 📚 API接口文档

### 🔗 生成嵌入向量

生成文本的语义向量表示，支持所有FlagEmbedding embedding模型。

**POST** `/v1/embeddings`

#### 请求示例

```json
{
    "model": "BAAI/bge-large-zh-v1.5",
    "input": ["你好世界", "人工智能技术"]
}
```

#### 支持的模型

- `BAAI/bge-large-zh-v1.5` - 中文大型模型（推荐）
- `BAAI/bge-base-zh-v1.5` - 中文基础模型
- `BAAI/bge-small-zh-v1.5` - 中文小型模型
- `BAAI/bge-m3` - 多语言模型
- `BAAI/bge-large-en-v1.5` - 英文大型模型
- 其他FlagEmbedding兼容模型

#### 响应格式

```json
{
    "data": [
        {
            "object": "embedding",
            "index": 0,
            "embedding": [0.1, 0.2, 0.3, ...]
        }
    ],
    "object": "list",
    "model": "BAAI/bge-large-zh-v1.5",
    "usage": {
        "prompt_tokens": 12,
        "total_tokens": 12
    }
}
```

### 🔄 文档重排序

根据查询相关性对文档进行重新排序，支持所有FlagEmbedding rerank模型。

**POST** `/v1/rerank`

#### 请求示例

```json
{
    "model": "BAAI/bge-reranker-v2-m3",
    "query": "什么是人工智能？",
    "documents": [
        "人工智能是计算机科学的一个分支",
        "今天天气很好",
        "机器学习是人工智能的子领域",
        "深度学习属于机器学习范畴"
    ],
    "top_n": 3,
    "return_documents": true
}
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | string | ✅ | - | 重排序模型名称 |
| `query` | string | ✅ | - | 查询文本 |
| `documents` | array | ✅ | - | 待排序的文档列表 |
| `top_n` | integer | ❌ | null | 返回前N个结果 |
| `return_documents` | boolean | ❌ | false | 是否返回文档内容 |
| `max_chunks_per_doc` | integer | ❌ | 1024 | 每个文档的最大块数 |
| `overlap_tokens` | integer | ❌ | 80 | 重叠token数 |

#### 支持的重排序模型

- `BAAI/bge-reranker-v2-m3` - 多语言重排序模型（推荐）
- `BAAI/bge-reranker-base` - 基础重排序模型
- `BAAI/bge-reranker-large` - 大型重排序模型
- 其他FlagEmbedding rerank模型

#### 响应格式

```json
{
    "id": "uuid-string",
    "results": [
        {
            "document": {
                "text": "人工智能是计算机科学的一个分支"
            },
            "index": 0,
            "relevance_score": 0.95
        }
    ],
    "tokens": {
        "input_tokens": 25,
        "output_tokens": 0
    }
}
```

### 🔍 其他接口

#### 健康检查
**GET** `/health`
```json
{"status": "healthy"}
```

#### 模型列表
**GET** `/models`
```json
{"loaded_models": ["BAAI/bge-large-zh-v1.5", "BAAI/bge-reranker-v2-m3"]}
```

#### 配置信息
**GET** `/config`
```json
{
    "model_storage_path": "D:\\git\\AntBlazor\\model",
    "api_host": "0.0.0.0",
    "api_port": 8000,
    "log_level": "INFO",
    "use_fp16": true
}
```

## ⚙️ 配置说明

### 环境变量配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `MODEL_STORAGE_PATH` | `D:\git\AntBlazor\model` | 模型存储路径 |
| `API_HOST` | `0.0.0.0` | API服务监听地址 |
| `API_PORT` | `8000` | API服务端口 |
| `LOG_LEVEL` | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `USE_FP16` | `true` | 是否使用FP16精度（节省内存） |

### 配置文件方式

编辑 `config.py` 文件修改默认配置：

```python
# 模型存储路径
MODEL_STORAGE_PATH = r"D:\your\model\path"

# API服务配置
API_HOST = "127.0.0.1"
API_PORT = 8080

# 启用FP16精度
DEFAULT_USE_FP16 = True
```

### 自定义启动

```bash
# 设置环境变量
set MODEL_STORAGE_PATH=E:\models
set API_PORT=9000
set USE_FP16=false

# 启动服务
python start.py
```

## 📋 使用示例

### Python客户端

#### 生成嵌入向量
```python
import requests

url = "http://localhost:8000/v1/embeddings"
data = {
    "model": "BAAI/bge-large-zh-v1.5",
    "input": ["你好世界", "人工智能技术"]
}

response = requests.post(url, json=data)
result = response.json()

# 获取向量
embeddings = [item["embedding"] for item in result["data"]]
print(f"生成了 {len(embeddings)} 个向量，维度: {len(embeddings[0])}")
```

#### 文档重排序
```python
import requests

url = "http://localhost:8000/v1/rerank"
data = {
    "model": "BAAI/bge-reranker-v2-m3",
    "query": "机器学习算法",
    "documents": [
        "深度学习是机器学习的一个分支",
        "今天天气不错",
        "神经网络是深度学习的基础",
        "Python是编程语言"
    ],
    "top_n": 2,
    "return_documents": True
}

response = requests.post(url, json=data)
result = response.json()

# 打印排序结果
for item in result["results"]:
    print(f"相关度: {item['relevance_score']:.3f} - {item['document']['text']}")
```

### curl命令

#### 生成嵌入向量
```bash
curl -X POST "http://localhost:8000/v1/embeddings" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "BAAI/bge-large-zh-v1.5",
       "input": ["你好", "世界"]
     }'
```

#### 文档重排序
```bash
curl -X POST "http://localhost:8000/v1/rerank" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "BAAI/bge-reranker-v2-m3",
       "query": "人工智能",
       "documents": ["AI技术发展", "天气预报", "机器学习应用"],
       "top_n": 2,
       "return_documents": true
     }'
```

## 💡 最佳实践

### 模型选择建议

#### Embedding模型推荐
- **中文场景**: `BAAI/bge-large-zh-v1.5` (性能最佳) 或 `BAAI/bge-base-zh-v1.5` (平衡选择)
- **英文场景**: `BAAI/bge-large-en-v1.5` 
- **多语言场景**: `BAAI/bge-m3`
- **资源受限**: `BAAI/bge-small-zh-v1.5`

#### Rerank模型推荐
- **通用场景**: `BAAI/bge-reranker-v2-m3` (多语言支持)
- **中文优化**: `BAAI/bge-reranker-base`
- **高精度需求**: `BAAI/bge-reranker-large`

### 性能优化

#### 内存优化
```bash
# 启用FP16精度，减少内存占用
export USE_FP16=true

# 设置合适的模型存储路径
export MODEL_STORAGE_PATH=/path/to/fast/storage
```

#### 并发处理
- API支持并发请求，自动进行模型缓存
- 建议根据服务器配置调整并发数
- 大批量文本处理时，建议分批请求

### 错误处理

#### 常见错误及解决方案

1. **模型下载失败**
   ```bash
   # 检查网络连接
   ping huggingface.co
   
   # 清理缓存重新下载
   rm -rf /path/to/models/*
   ```

2. **内存不足**
   ```bash
   # 使用小型模型
   export USE_FP16=true
   # 或选择更小的模型，如 bge-small-zh-v1.5
   ```

3. **端口占用**
   ```bash
   # 修改端口
   export API_PORT=8001
   ```

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

## 📋 技术栈

### 核心依赖
- **FastAPI** `0.104.1` - 现代、快速的Web框架
- **FlagEmbedding** `1.2.10` - 文本嵌入向量生成
- **ModelScope** `1.9.5` - 模型下载和管理
- **Transformers** `>=4.21.0` - Hugging Face模型库
- **PyTorch** `>=1.13.0` - 深度学习框架
- **Uvicorn** `0.24.0` - ASGI服务器
- **Pydantic** `2.5.0` - 数据验证

### 系统要求
- **Python**: 3.8+
- **内存**: 建议4GB+（使用FP16可降低需求）
- **存储**: 根据模型大小，建议10GB+可用空间
- **GPU**: 可选，支持CUDA加速

## ⚠️ 注意事项

### 模型下载
1. 首次使用某个模型时会自动从ModelScope下载
2. 模型文件较大，请确保网络连接稳定
3. 模型会缓存在本地，避免重复下载
4. 支持断点续传，下载失败可重试

### 资源管理
1. 大型模型需要较多内存，建议使用`USE_FP16=true`
2. 多个模型会同时加载到内存中
3. 根据服务器配置选择合适的模型规模
4. 可以通过`/models`接口查看已加载的模型

### 生产环境建议
1. 使用Docker部署，确保环境一致性
2. 配置适当的日志级别和监控
3. 设置健康检查和自动重启
4. 考虑使用负载均衡处理高并发
5. 定期备份模型缓存目录

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目！

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd AntSK-PyApi

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python start.py
```

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 提交前运行测试

## 📄 许可证

本项目采用开源许可证，详见LICENSE文件。

## 🔗 相关链接

- [FlagEmbedding官方文档](https://github.com/FlagOpen/FlagEmbedding)
- [ModelScope模型库](https://modelscope.cn/models?page=1&tabKey=task&tasks=sentence-embedding)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)

---

**🎉 感谢使用 AntSK Python Embedding API！**

如有问题或建议，欢迎提交Issue或联系开发团队。 
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any
import os
import logging
import FlagEmbedding
from modelscope.hub.snapshot_download import snapshot_download
import numpy as np
from config import MODEL_STORAGE_PATH, DEFAULT_USE_FP16, LOG_LEVEL

# 配置日志
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

app = FastAPI(title="Embedding API", version="1.0.0")

# 全局异常处理器
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """处理Pydantic验证错误"""
    logger.error(f"请求验证失败: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "请求参数验证失败",
            "detail": str(exc),
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "detail": "服务器遇到了一个意外的错误，请稍后重试"
        }
    )

# 请求模型
class EmbeddingRequest(BaseModel):
    model: str
    input: List[str]

# rerank请求模型
class RerankRequest(BaseModel):
    model: str
    query: str
    documents: List[str]
    top_n: int = None
    return_documents: bool = False
    max_chunks_per_doc: int = 1024
    overlap_tokens: int = 80

# 响应模型
class EmbeddingData(BaseModel):
    object: str = "embedding"
    index: int
    embedding: List[float]

# rerank响应模型
class RerankDocument(BaseModel):
    text: str

class RerankResult(BaseModel):
    document: RerankDocument = None
    index: int
    relevance_score: float

class RerankTokens(BaseModel):
    input_tokens: int
    output_tokens: int

class RerankResponse(BaseModel):
    id: str
    results: List[RerankResult]
    tokens: RerankTokens

class Usage(BaseModel):
    prompt_tokens: int
    total_tokens: int

class EmbeddingResponse(BaseModel):
    data: List[EmbeddingData]
    object: str = "list"
    model: str
    usage: Usage

# 全局变量存储已加载的模型
loaded_models: Dict[str, Any] = {}

def load_model(model_name: str):
    """加载或获取已缓存的模型"""
    if model_name in loaded_models:
        return loaded_models[model_name]
    
    try:
        # 使用配置文件中的模型存储路径
        directory_path = MODEL_STORAGE_PATH
        # 将模型名称中的斜杠替换为下划线，避免文件路径问题
        safe_model_name = model_name.replace("/", "_").replace("\\", "_")
        filename = f"{safe_model_name}-key"
        file_path = os.path.join(directory_path, filename)
        
        # 确保storage目录存在
        try:
            os.makedirs(directory_path, exist_ok=True)
        except OSError as e:
            logger.error(f"创建模型存储目录失败: {e}")
            raise HTTPException(status_code=500, detail=f"创建模型存储目录失败: {str(e)}")
        
        # 检查本地是否存在model_dir
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    model_dir = f.read().strip()
                logger.info(f"从缓存加载模型路径: {model_dir}")
                
                # 验证模型目录是否存在
                if not os.path.exists(model_dir):
                    logger.warning(f"缓存的模型路径不存在，重新下载: {model_dir}")
                    os.remove(file_path)  # 删除无效的缓存文件
                    raise FileNotFoundError("缓存的模型路径无效")
                    
            except (IOError, OSError) as e:
                logger.error(f"读取模型缓存文件失败: {e}")
                raise HTTPException(status_code=500, detail=f"读取模型缓存失败: {str(e)}")
        else:
            logger.info(f"下载模型: {model_name}")
            try:
                # 指定下载到配置的模型存储路径
                cache_dir = os.path.join(directory_path, "cache")
                model_dir = snapshot_download(model_name, revision="master", cache_dir=cache_dir)
                
                # 保存模型物理路径
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(model_dir)
                logger.info(f"模型下载完成，路径: {model_dir}")
                
            except Exception as e:
                logger.error(f"模型下载失败: {e}")
                raise HTTPException(status_code=500, detail=f"模型下载失败: {str(e)}")
        
        # 初始化模型
        try:
            # 根据模型名称判断使用哪种类型的模型
            if "rerank" in model_name.lower():
                # 重排序模型
                model = FlagEmbedding.FlagReranker(model_dir, use_fp16=DEFAULT_USE_FP16)
            else:
                # 嵌入模型
                model = FlagEmbedding.FlagModel(model_dir, use_fp16=DEFAULT_USE_FP16)
            
            loaded_models[model_name] = model
            logger.info(f"模型 {model_name} 加载完成")
            return model
            
        except Exception as e:
            logger.error(f"初始化模型失败: {e}")
            raise HTTPException(status_code=500, detail=f"模型初始化失败: {str(e)}")
            
    except HTTPException:
        # 重新抛出HTTPException
        raise
    except Exception as e:
        logger.error(f"加载模型时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")

def count_tokens(texts: List[str]) -> int:
    """简单的token计数，你可以根据实际需要调整"""
    total_chars = sum(len(text) for text in texts)
    # 简单估算：中文大约1个字符=1个token，英文大约4个字符=1个token
    return total_chars

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """创建文本嵌入向量"""
    try:
        # 输入验证
        if not request.model or not request.model.strip():
            raise HTTPException(status_code=400, detail="模型名称不能为空")
        
        if not request.input or len(request.input) == 0:
            raise HTTPException(status_code=400, detail="输入文本不能为空")
        
        # 检查输入文本是否都为空
        if all(not text.strip() for text in request.input):
            raise HTTPException(status_code=400, detail="输入文本不能全部为空")
        
        # 加载模型
        model = load_model(request.model)
        
        # 生成嵌入向量
        embeddings = model.encode(request.input)
        
        # 确保embeddings是numpy数组
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings)
        
        # 如果是单个文本，确保是2D数组
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # 构建响应数据
        data = []
        for i, embedding in enumerate(embeddings):
            data.append(EmbeddingData(
                index=i,
                embedding=embedding.tolist()
            ))
        
        # 计算token使用量
        prompt_tokens = count_tokens(request.input)
        
        response = EmbeddingResponse(
            data=data,
            model=request.model,
            usage=Usage(
                prompt_tokens=prompt_tokens,
                total_tokens=prompt_tokens
            )
        )
        
        return response
        
    except Exception as e:
        logger.error(f"生成嵌入向量时出错: {e}")
        raise HTTPException(status_code=500, detail=f"生成嵌入向量失败: {str(e)}")

@app.post("/v1/rerank", response_model=RerankResponse)
async def create_rerank(request: RerankRequest):
    """文档重排序"""
    try:
        # 输入验证
        if not request.model or not request.model.strip():
            raise HTTPException(status_code=400, detail="模型名称不能为空")
        
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="查询文本不能为空")
        
        if not request.documents or len(request.documents) == 0:
            raise HTTPException(status_code=400, detail="文档列表不能为空")
        
        # 检查文档是否都为空
        if all(not doc.strip() for doc in request.documents):
            raise HTTPException(status_code=400, detail="文档内容不能全部为空")
        
        # 验证top_n参数
        if request.top_n is not None and request.top_n < 0:
            raise HTTPException(status_code=400, detail="top_n参数不能为负数")
        
        # 加载模型
        model = load_model(request.model)
        
        # 添加调试日志
        logger.info(f"Rerank请求 - 查询: {request.query}")
        logger.info(f"Rerank请求 - 文档数量: {len(request.documents)}")
        logger.info(f"Rerank请求 - 文档内容: {request.documents}")
        logger.info(f"Rerank请求 - top_n: {request.top_n}")
        
        # 准备查询和文档对
        pairs = [[request.query, doc] for doc in request.documents]
        logger.info(f"准备的查询-文档对数量: {len(pairs)}")
        
        # 计算相关性分数，使用内置的标准化功能
        scores = model.compute_score(pairs, normalize=True)
        logger.info(f"模型返回的标准化分数: {scores}")
        logger.info(f"分数类型: {type(scores)}")
        
        # 确保scores是列表
        if not isinstance(scores, list):
            if hasattr(scores, 'tolist'):
                scores_converted = scores.tolist()
                # 如果tolist()返回的仍然不是列表，则包装成列表
                if not isinstance(scores_converted, list):
                    scores = [scores_converted]
                else:
                    scores = scores_converted
            else:
                scores = [float(scores)]
        
        logger.info(f"处理后的分数列表: {scores}")
        logger.info(f"分数列表长度: {len(scores)}")
        
        # 创建结果列表，包含原始索引
        results_with_index = [(i, score) for i, score in enumerate(scores)]
        logger.info(f"带索引的结果: {results_with_index}")
        
        # 按分数降序排序
        results_with_index.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"排序后的结果: {results_with_index}")
        
        # 如果指定了top_n，则只返回前top_n个结果
        if request.top_n is not None and request.top_n > 0:
            logger.info(f"应用top_n限制: {request.top_n}")
            results_with_index = results_with_index[:request.top_n]
            logger.info(f"top_n过滤后的结果: {results_with_index}")
        elif request.top_n is not None and request.top_n <= 0:
            logger.info(f"top_n为0或负数({request.top_n})，返回所有结果")
            # 当top_n为0或负数时，返回所有结果
        
        # 构建响应结果
        results = []
        for original_index, score in results_with_index:
            logger.info(f"处理结果 - 索引: {original_index}, 分数: {score}")
            result = RerankResult(
                index=original_index,
                relevance_score=float(score)
            )
            
            # 如果需要返回文档内容
            if request.return_documents:
                try:
                    result.document = RerankDocument(text=request.documents[original_index])
                except IndexError as e:
                    logger.error(f"文档索引越界: {original_index}, 文档总数: {len(request.documents)}")
                    raise HTTPException(status_code=500, detail=f"文档索引错误: {str(e)}")
            
            results.append(result)
        
        logger.info(f"最终结果数量: {len(results)}")
        
        # 计算token使用量
        input_tokens = count_tokens([request.query] + request.documents)
        
        # 生成唯一ID
        import uuid
        response_id = str(uuid.uuid4())
        
        response = RerankResponse(
            id=response_id,
            results=results,
            tokens=RerankTokens(
                input_tokens=input_tokens,
                output_tokens=0  # rerank通常不产生输出token
            )
        )
        
        return response
        
    except Exception as e:
        logger.error(f"重排序时出错: {e}")
        raise HTTPException(status_code=500, detail=f"重排序失败: {str(e)}")

@app.get("/")
async def root():
    """根路径"""
    return {"message": "Embedding API is running"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

@app.get("/models")
async def list_models():
    """列出已加载的模型"""
    return {"loaded_models": list(loaded_models.keys())}

@app.get("/config")
async def get_config():
    """获取当前配置信息"""
    try:
        from config import get_config
        return get_config()
    except Exception as e:
        logger.error(f"获取配置信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置信息失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
#!/usr/bin/env python3
"""
Embedding API 启动脚本
"""
import uvicorn
import sys
import os
from config import API_HOST, API_PORT, print_config

def main():
    """启动FastAPI应用"""
    print("🚀 正在启动 Embedding API...")
    print_config()
    print(f"📍 API文档地址: http://{API_HOST}:{API_PORT}/docs")
    print(f"🔍 健康检查: http://{API_HOST}:{API_PORT}/health")
    print(f"📋 模型列表: http://{API_HOST}:{API_PORT}/models")
    print(f"⚡ 嵌入接口: POST http://{API_HOST}:{API_PORT}/v1/embeddings")
    print(f"⚡ 重排接口: POST http://{API_HOST}:{API_PORT}/v1/rerank")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host=API_HOST,
            port=API_PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
"""
AntSK-PyApi API 配置文件
"""
import os

# 模型存储路径配置
MODEL_STORAGE_PATH = os.getenv("MODEL_STORAGE_PATH", r"D:\git\AntBlazor\model")

# API服务配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 模型配置
DEFAULT_USE_FP16 = os.getenv("USE_FP16", "true").lower() == "true"

def get_config():
    """获取当前配置信息"""
    return {
        "model_storage_path": MODEL_STORAGE_PATH,
        "api_host": API_HOST,
        "api_port": API_PORT,
        "log_level": LOG_LEVEL,
        "use_fp16": DEFAULT_USE_FP16
    }

def print_config():
    """打印当前配置"""
    config = get_config()
    print("📋 当前配置:")
    print(f"  模型存储路径: {config['model_storage_path']}")
    print(f"  API地址: {config['api_host']}:{config['api_port']}")
    print(f"  日志级别: {config['log_level']}")
    print(f"  使用FP16: {config['use_fp16']}")
    print("-" * 50) 

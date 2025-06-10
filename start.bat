@echo off
echo 🚀 启动 Embedding API 服务...
echo.

REM 设置环境变量（如果需要自定义路径，可以修改这里）
set MODEL_STORAGE_PATH=D:\git\AntBlazor\model
set API_HOST=0.0.0.0
set API_PORT=8000
set LOG_LEVEL=INFO
set USE_FP16=true

echo 📋 环境变量配置:
echo   模型存储路径: %MODEL_STORAGE_PATH%
echo   API地址: %API_HOST%:%API_PORT%
echo   日志级别: %LOG_LEVEL%
echo   使用FP16: %USE_FP16%
echo.

REM 启动服务
python start.py

pause 
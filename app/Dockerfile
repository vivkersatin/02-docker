# 使用官方的 Python 映像檔
FROM python:3.11-slim

# 設定環境變數，防止 Python 寫入 .pyc 文件和緩衝輸出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
# 安裝編譯 C 擴充套件（如 bcrypt）所需的建置工具，然後安裝 Python 依賴，最後清理以保持映像檔小巧。
# 移除了 --no-binary :all: 以加快建置速度；現代的 Python wheel 通常具有良好的跨平台相容性。
# 如果特定套件有問題，可以針對性地使用 --no-binary <package_name>
RUN apt-get update && \
    apt-get install -y build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential && rm -rf /var/lib/apt/lists/*

# 將目前目錄（即 app 目錄）的所有內容複製到工作目錄中
COPY . .

# 聲明容器在執行時監聽的網路端口
EXPOSE 8000

# 執行 uvicorn 伺服器。移除了 --reload，因其僅適用於開發環境。
# 在生產環境中，建議使用 Gunicorn 等程序管理器來運行 Uvicorn。
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
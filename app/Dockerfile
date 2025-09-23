# --- Stage 1: Builder ---
# 這個階段的任務是安裝所有依賴，包括需要編譯的套件。
# 我們使用完整的 Python 映像檔，因为它包含了建置工具。
FROM python:3.11 as builder

# 設定環境變數，防止 Python 寫入 .pyc 文件和緩衝輸出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 設定工作目錄
WORKDIR /opt/venv

# 建立一個虛擬環境
RUN python -m venv .
ENV PATH="/opt/venv/bin:$PATH"

# 安裝編譯 C 擴充套件（如 bcrypt）所需的建置工具
RUN apt-get update && apt-get install -y build-essential

# 複製 requirements.txt 並在虛擬環境中安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final ---
# 這個階段的任務是建立最終的、輕量的執行映像檔。
FROM python:3.11-slim

# 從 builder 階段複製已安裝好的虛擬環境
COPY --from=builder /opt/venv /opt/venv

# 將目前目錄（即 app 目錄）的所有內容複製到工作目錄中
WORKDIR /app
COPY . .

# 聲明容器在執行時監聽的網路端口
EXPOSE 8000

# 設定 PATH，讓 shell 可以找到虛擬環境中的執行檔
ENV PATH="/opt/venv/bin:$PATH"

# 執行 uvicorn 伺服器
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

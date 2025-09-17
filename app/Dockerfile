# 使用官方的 Python 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 只複製應用程式相關的程式碼到工作目錄中
COPY app/ .

# 執行 uvicorn 伺服器，並啟用自動重載
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
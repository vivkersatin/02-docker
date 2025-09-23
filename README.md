# Dockerized FastAPI 應用程式

這是一個使用 Docker Compose 容器化的 FastAPI 應用程式，包含一個 FastAPI 後端、一個 PostgreSQL 資料庫和一個 Nginx 前端。前端是一個單頁應用程式 (SPA)，用於使用者登入和書籍管理。

## 專案結構

```
.
├── .dockerignore
├── .gitignore
├── create_user.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   └── users.py
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── default.conf
    ├── Dockerfile
    └── index.html
```

## 文件和目錄說明

### 根目錄 (`./`)

*   `.dockerignore`: 指定 Docker 構建過程中應忽略的文件和目錄，類似於 `.gitignore`。
*   `.gitignore`: 指定 Git 應忽略的文件和目錄。
*   `create_user.py`: 一個用於在資料庫中創建測試使用者的臨時 Python 腳本。
*   `docker-compose.yml`: 定義和配置應用程式的 Docker 服務（`db`、`web_app`、`frontend`）。
*   `Dockerfile`: 用於構建 `web_app` 服務（FastAPI 後端）的 Docker 映像檔。
*   `requirements.txt`: 列出整個專案的 Python 依賴項。

### `app/` 目錄 (FastAPI 後端)

這是 FastAPI 後端應用程式的根目錄。

*   `api/`: 包含所有 FastAPI API 相關的模組。
    *   `__init__.py`: 將 `api` 目錄標記為 Python 套件。
    *   `auth.py`: 處理使用者認證相關的路由和邏輯（登入、JWT 生成）。
    *   `books.py`: 處理書籍管理相關的 API 路由（CRUD 操作）。
    *   `models.py`: 定義 Tortoise ORM 模型，映射到資料庫表格（例如 `User` 和 `Book` 模型）。
    *   `schemas.py`: 定義 Pydantic 模型，用於請求和響應資料驗證和序列化。
    *   `security.py`: 包含安全相關的工具函數，如密碼哈希和 JWT 處理。
    *   `users.py`: 處理使用者管理相關的 API 路由。
*   `Dockerfile`: 用於構建 `app` 目錄內 FastAPI 應用程式的 Docker 映像檔。
*   `main.py`: FastAPI 應用程式的主入口點，負責初始化應用、設定 CORS、連接資料庫和掛載 API 路由。
*   `requirements.txt`: 列出 FastAPI 後端服務的 Python 依賴項。

### `frontend/` 目錄 (Nginx 前端)

這是 Nginx 靜態文件伺服器和前端 SPA 的根目錄。

*   `default.conf`: Nginx 的配置檔，用於設定如何服務靜態文件和處理請求。
*   `Dockerfile`: 用於構建 `frontend` 服務（Nginx）的 Docker 映像檔。
*   `index.html`: 前端單頁應用程式 (SPA) 的主 HTML 文件，包含所有 HTML、CSS 和 JavaScript 邏輯，用於使用者登入和書籍管理。

## 如何運行

1.  **構建並啟動 Docker 容器：**
    ```bash
    docker-compose up --build
    ```
2.  **訪問應用程式：**
    在瀏覽器中打開 `http://localhost:8080`。
3.  **創建測試使用者 (如果需要)：**
    ```bash
    python create_user.py
    ```
    這將創建一個 `testuser` / `testpassword` 的使用者。
4.  **停止並清理容器：**
    ```bash
    docker-compose down --remove-orphans

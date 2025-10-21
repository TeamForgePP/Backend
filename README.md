# 🧩 TeamForgePP — Backend

Монолитный backend проекта **TeamForgePP**, реализованный на **FastAPI** с использованием **SQLAlchemy**, **Alembic**, **PostgreSQL** и **MinIO**.  
Проект запускается через `uv` и управляется с помощью `Makefile`.

---

## ⚙️ Технологический стек

- **Python 3.12+**
- **FastAPI** — основной веб-фреймворк
- **SQLAlchemy** — ORM и управление данными
- **Alembic** — миграции базы данных
- **PostgreSQL** — основная СУБД
- **MinIO** — хранилище файлов
- **uv** — менеджер зависимостей и среды исполнения
- **Docker Compose** — инфраструктура сервисов

---

## 🚀 Запуск проекта

Перед запуском убедись, что установлены:
- **Docker** и **Docker Compose**
- **make**
- **uv** (устанавливается через `pip install uv`)

### 1. Клонирование репозитория
```bash
git clone https://github.com/<your-org>/TeamForgePP.git
cd TeamForgePP
```
### 2. Настройка окружения
Скопируй .env.example (если есть) и укажи значения для:
cp .env.example .env
.env используется только для запуска БД и MinIO.
Основная конфигурация backend хранится в config.toml.
### 3. Установка зависимостей
```bash
uv sync
```
### 4. Запуск backend-сервера
```bash
make run
```
После запуска приложение будет доступно по адресу:
http://localhost:8000
## 🧰 Работа с миграциями (Alembic)
Миграции ещё не созданы, но Alembic уже подключён.
После определения моделей можно будет использовать стандартные команды:
```bash
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
```
## 📁 Структура проекта (предварительно)
```bash
TeamForgePP/
├── src/
│   ├── main.py             # Точка входа
│   ├── config/             # Настройки (config.toml)
│   ├── db/                 # Инициализация БД, Alembic
│   ├── api/                # Роутеры FastAPI
│   ├── schemas/            # DTO / Pydantic-схемы
│   ├── services/           # Логика приложения
│   └── core/               # Утилиты, константы, logger
├── Makefile
├── Dockerfile
├── docker-compose.yaml
├── .env
└── config.toml
```
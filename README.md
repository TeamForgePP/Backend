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
git clone git@github.com:TeamForgePP/Backend.git
cd TeamForgePP
```
### 2. Настройка окружения
Скопируй .env и config.toml из документации и расположи их в корне проекта
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
## 🧰 Работа с _коммитами_ (commitizen)
На проекте подключен линтёр и проверка на типизацию перед коммитом, а так же строгая проверка на следование правилам Conventional Commits. 

Чтобы подключить прекоммиты и commitizen выполните команду:
```bash
make hooks
```
## 🧰 Работа с _миграциями_ (Alembic)
Миграции ещё не созданы, но Alembic уже подключён.
После определения моделей можно будет использовать стандартные команды:
```bash
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
```

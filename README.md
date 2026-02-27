# Тестовое задание: система аутентификации и RBAC

Django + DRF приложение с собственной реализацией JWT-аутентификации и ролевой системы разграничения доступа (RBAC), без использования `django.contrib.auth` для авторизации.

## Описание проекта

Проект реализует backend-часть системы с:

- **Кастомной моделью пользователя** — не наследуется от `AbstractUser`, только нужные поля.
- **JWT-аутентификацией** — токены создаются через `PyJWT`, хранятся только на клиенте. При выходе jti токена помещается в таблицу-чёрный список.
- **Мягким удалением** — `is_active=False` вместо физического удаления записи.
- **RBAC** — роли и права хранятся в отдельных таблицах, назначаются через Admin API.
- **Хешированием паролей** — используется `django.contrib.auth.hashers` (только хеширование, без auth-моделей).

## Структура проекта

```
effective_mobile_testing_task/
├── backend/
│   ├── apps/
│   │   ├── auth_core/       # JWT-аутентификация (backends.py, jwt_utils.py)
│   │   ├── business/        # Демо-эндпоинты с проверкой прав
│   │   ├── core/            # Модели (User, Role, Permission, TokenBlacklist)
│   │   ├── rbac/            # RBAC: права, роли, Admin API, сервис проверки
│   │   └── users/           # Регистрация, Login, Logout, Профиль
│   ├── config/              # Django-настройки и маршруты
│   └── tests/               # Pytest-тесты
├── docker-compose.yml
├── .env.example
└── plan.md
```

## Архитектура запроса

```
Входящий запрос
       │
       ▼
  JWTAuthentication.authenticate()
       ├── Нет заголовка → AnonymousUser (request.user = None)
       ├── Невалидный / истёкший токен → 401
       ├── Токен в чёрном списке → 401
       └── Валидный токен, активный пользователь → request.user = User
       │
       ▼
  RBACPermission.has_permission()
       ├── Не аутентифицирован → 401
       ├── required_permission = None → доступ разрешён (profile-эндпоинты)
       ├── has_permission(user, codename) = True → доступ разрешён
       └── has_permission(user, codename) = False → 403
       │
       ▼
  View / Бизнес-логика
```

## Схема базы данных

```mermaid
erDiagram
    users {
        bigint id PK
        varchar full_name
        varchar email
        varchar password_hash
        bool is_active
        timestamp created_at
        timestamp updated_at
    }
    roles {
        bigint id PK
        varchar name
        text description
    }
    permissions {
        bigint id PK
        varchar codename
        varchar name
    }
    role_permissions {
        bigint id PK
        bigint role_id FK
        bigint permission_id FK
    }
    user_roles {
        bigint id PK
        bigint user_id FK
        bigint role_id FK
    }
    token_blacklist {
        bigint id PK
        varchar token_jti
        timestamp expires_at
        timestamp created_at
    }

    users ||--o{ user_roles : ""
    roles ||--o{ user_roles : ""
    roles ||--o{ role_permissions : ""
    permissions ||--o{ role_permissions : ""
```

## Матрица доступа

| Эндпоинт | Без токена | User | Manager | Admin |
|---|---|---|---|---|
| `POST /api/v1/auth/register/` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/v1/auth/login/` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/v1/auth/logout/` | ❌ 401 | ✅ | ✅ | ✅ |
| `GET/PATCH /api/v1/users/me/` | ❌ 401 | ✅ | ✅ | ✅ |
| `POST /api/v1/users/me/delete/` | ❌ 401 | ✅ | ✅ | ✅ |
| `GET /api/v1/profile/` | ❌ 401 | ✅ | ✅ | ✅ |
| `GET /api/v1/reports/` (`can_view_reports`) | ❌ 401 | ❌ 403 | ✅ | ✅ |
| `GET /api/v1/admin/stats/` (`can_view_stats`) | ❌ 401 | ❌ 403 | ❌ 403 | ✅ |
| `GET/POST /api/admin/roles/` (`can_manage_roles`) | ❌ 401 | ❌ 403 | ❌ 403 | ✅ |
| `POST /api/admin/roles/{id}/permissions/` | ❌ 401 | ❌ 403 | ❌ 403 | ✅ |
| `POST /api/admin/users/{id}/roles/` | ❌ 401 | ❌ 403 | ❌ 403 | ✅ |

---

## Запуск через Docker (рекомендуется)

### 1. Создать файл переменных окружения

```bash
cp .env.example .env
```

Обязательные переменные в `.env`:

```dotenv
SECRET_KEY=your-django-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
```

### 2. Собрать и запустить

```bash
docker compose up --build -d
```

Это запустит два контейнера:
- `web` — Django + Gunicorn (порт 8000)
- `db` — PostgreSQL 16

### 3. Применить миграции (при первом запуске)

```bash
docker compose exec web python manage.py migrate
```

### 4. Проверить работоспособность

```bash
curl http://localhost:8000/api/v1/health/
# {"status": "ok"}
```

### Остановка

```bash
docker compose down
```

---

## Локальный запуск (без Docker)

Для локального запуска нужен PostgreSQL и Python 3.12+.

### 1. Создать виртуальное окружение

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Настроить окружение

```bash
cp .env.example .env
# Отредактировать DATABASE_URL: указать localhost вместо db
# DATABASE_URL=postgres://postgres:postgres@localhost:5432/mydb
```

### 3. Применить миграции и запустить

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

---

## Примеры запросов API

### Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Иван Иванов", "email": "ivan@example.com", "password": "Secret123!", "password_confirm": "Secret123!"}'
```

### Вход

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "ivan@example.com", "password": "Secret123!"}'
# Ответ: {"access": "<jwt-token>", "user": {...}}
```

### Запрос с JWT-токеном

```bash
TOKEN="<access-token из ответа login>"

curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

### Выход (инвалидация токена)

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer $TOKEN"
```

### Создание роли (только admin)

```bash
curl -X POST http://localhost:8000/api/admin/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "manager", "description": "Менеджер"}'
```

### Назначение права роли

```bash
curl -X POST http://localhost:8000/api/admin/roles/1/permissions/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"permission_id": 1}'
```

### Назначение роли пользователю

```bash
curl -X POST http://localhost:8000/api/admin/users/2/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role_id": 1}'
```

---

## Тесты

### В Docker

```bash
docker compose exec web pytest tests/ -v
```

### Локально

```bash
cd backend
DATABASE_URL=postgres://... JWT_SECRET_KEY=... pytest tests/ -v
```

Тесты покрывают:
- Регистрацию нового пользователя
- Успешный вход
- Вход для soft-deleted пользователя (ожидается 401)
- Чёрный список — после logout токен отклоняется (401)
- Доступ к профилю без токена (401)
- Доступ к профилю с токеном (200)
- Запрос к защищённому ресурсу без нужных прав (403)
- Запрос к защищённому ресурсу с назначенной ролью (200)

---

## Линтеры

Проверка кода перед пушем:

```bash
cd backend && isort . && black . && flake8
```

Настройка хука `pre-push` (запускается автоматически при `git push`):

```bash
./scripts/install-hooks.sh
```

Конфигурация линтеров: `.flake8`, `pyproject.toml`.

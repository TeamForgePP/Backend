# CHANGELOG

<!-- version list -->

## v1.4.0 (2025-12-09)

### Bug Fixes

- **alembic**: Исправил использование ошибочной ссылки для алембика
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **logger**: Исправлена работа логгера, приведен к стандартизированному виду
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **pre-commit**: Исправил ошибку, когда ruff чекал файлы алембика
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **где-то**: Устал я уже от этих фиксов, помогите пж
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

### Chores

- **alembic**: Создал init миграцию (добавлены все модели таблиц)
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **pre-commit**: Настроил хуки на pre-commit и pre-push
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **pyproject**: Добавлены новые зависимости для хэширования, jwt и redis
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **uv**: Добавлен асинхронный движок asyncpg
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

### Continuous Integration

- **protect-main**: Создал action для защиты мержа в main не из dev
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

### Features

- **admin.user**: Добавлены админ ручки полный CRUD для юзера
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **auth**: Добавлена авторизация админа ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **config**: Добавлен рэдис и все что связано с токенами
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **docker**: Добавлен рэдис и исправлена ошибка монтирования волюма не в ту директорию
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **enums**: Добавлен новый enum для модели спринтов
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **groups**: Create groups table model ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **groups**: Добавить модель таблицы учебных групп
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **groups-repo**: Добавить репозиторий для модели групп
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **main**: Добавлено подключение сборщика роутеров и lifespan
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **main-router**: Создано единое монтирование роуеторов
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы invitations
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы performes
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы project_role
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы tasks ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы teams ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы для ролей в проекте
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы исполнителей тасков
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы команд ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы приглашений
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Добавить модель таблицы тасков ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **modules**: Создан скелет-структура блока модулей
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **project-reports**: Create project_reports link table model
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **project-reports**: Добавить модель связи проектов и отчетов
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **projects**: Create projects table model ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **projects**: Добавить модель таблицы проектов
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **projects-repo**: Добавить репозиторий для модели проектов
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **redis**: Добавлены файлы для удобной работы с редисом
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **reports**: Create reports table model ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **reports**: Добавить модель таблицы отчетов по проектам
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **reports-repo**: Добавить репозиторий для модели отчетов
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **repositories**: Добавить репозиторий для Invitations
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **repositories**: Репозиторий Notifications
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **repositories**: Репозиторий Sprints ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **repositories**: Репозиторий Tasks ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **repository**: Добавил интерфейс абстрактного репозитория и папку под них
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **security**: Добавлены jwt токены, а так же зависимости для проверки прав в будущих роутерах
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **sprints**: Create sprints table model ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **sprints**: Добавить модель таблицы спринтов
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **teams-repo**: Добавить репозиторий для модели teams
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **uow**: Добавлен uow для удобной работы с сессиями и репозиториями
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **users**: Add enums (user_role/level/faculty placeholders)
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **users**: Create users table model with mapped_column
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **users**: Добавить модель таблицы пользователей
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **users-repo**: Добавить репозиторий для модели пользователей
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

### Refactoring

- **alembic+models**: Провел индексирование полей + добавил поле группы в юзере как нулл
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **enums**: Провел рефрактор enum-ов добавил их в __init__
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Провел рефакторинг моделей таблиц бд
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **models**: Провел рефрактор импортов ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))

- **repo**: Провер рефрактор репозиториев, добавил новые методы, а так же репозитории к mtm моделям
  ([#52](https://github.com/TeamForgePP/Backend/pull/52),
  [`42194db`](https://github.com/TeamForgePP/Backend/commit/42194dbad4841334f6cb7ae617a0dbff10463ca5))


## v1.3.0 (2025-11-18)

### Bug Fixes

- Semantic-release push via PAT ([#40](https://github.com/TeamForgePP/Backend/pull/40),
  [`c24189b`](https://github.com/TeamForgePP/Backend/commit/c24189b94d62c50a71c1837acbccc86f8e9d8e1a))

- **alembic**: Исправил использование ошибочной ссылки для алембика
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **alembic**: Исправил использование ошибочной ссылки для алембика
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **alembic**: Исправил использование ошибочной ссылки для алембика
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **ci**: Использую PAT для семантик релиза, чтобы ообойти защиту ветки main
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **ci**: Использую PAT для семантик релиза, чтобы ообойти защиту ветки main
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **ci**: Использую PAT для семантик релиза, чтобы ообойти защиту ветки main
  ([#40](https://github.com/TeamForgePP/Backend/pull/40),
  [`c24189b`](https://github.com/TeamForgePP/Backend/commit/c24189b94d62c50a71c1837acbccc86f8e9d8e1a))

- **ci**: Исправил git config команду ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **ci**: Исправил git config команду ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **ci**: Исправил git config команду ([#41](https://github.com/TeamForgePP/Backend/pull/41),
  [`a3147a2`](https://github.com/TeamForgePP/Backend/commit/a3147a296fa455cb44decb9bbd5952983120b616))

- **ci**: Исправил git токен ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

### Chores

- **alembic**: Создал init миграцию (добавлены все модели таблиц)
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **alembic**: Создал init миграцию (добавлены все модели таблиц)
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **alembic**: Создал init миграцию (добавлены все модели таблиц)
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **pre-commit**: Настроил хуки на pre-commit и pre-push
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **pre-commit**: Настроил хуки на pre-commit и pre-push
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **pre-commit**: Настроил хуки на pre-commit и pre-push
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **uv**: Добавлен асинхронный движок asyncpg
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **uv**: Добавлен асинхронный движок asyncpg
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **uv**: Добавлен асинхронный движок asyncpg
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

### Continuous Integration

- **protect-main**: Создал action для защиты мержа в main не из dev
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **protect-main**: Создал action для защиты мержа в main не из dev
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **protect-main**: Создал action для защиты мержа в main не из dev
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

### Features

- **groups**: Create groups table model ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **groups**: Create groups table model ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **groups**: Create groups table model ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **groups**: Добавить модель таблицы учебных групп
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **groups**: Добавить модель таблицы учебных групп
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **groups**: Добавить модель таблицы учебных групп
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы invitations
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы invitations
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы invitations
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы performes
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы performes
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы performes
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы project_role
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы project_role
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы project_role
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы tasks ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы tasks ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы tasks ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы teams ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы teams ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы teams ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы для ролей в проекте
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы для ролей в проекте
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы для ролей в проекте
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы исполнителей тасков
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы исполнителей тасков
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы исполнителей тасков
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы команд ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы команд ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы команд ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы приглашений
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы приглашений
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы приглашений
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Добавить модель таблицы тасков ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Добавить модель таблицы тасков ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Добавить модель таблицы тасков ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **project-reports**: Create project_reports link table model
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **project-reports**: Create project_reports link table model
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **project-reports**: Create project_reports link table model
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **project-reports**: Добавить модель связи проектов и отчетов
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **project-reports**: Добавить модель связи проектов и отчетов
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **project-reports**: Добавить модель связи проектов и отчетов
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **projects**: Create projects table model ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **projects**: Create projects table model ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **projects**: Create projects table model ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **projects**: Добавить модель таблицы проектов
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **projects**: Добавить модель таблицы проектов
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **projects**: Добавить модель таблицы проектов
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **reports**: Create reports table model ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **reports**: Create reports table model ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **reports**: Create reports table model ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **reports**: Добавить модель таблицы отчетов по проектам
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **reports**: Добавить модель таблицы отчетов по проектам
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **reports**: Добавить модель таблицы отчетов по проектам
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **repository**: Добавил интерфейс абстрактного репозитория и папку под них
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **repository**: Добавил интерфейс абстрактного репозитория и папку под них
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **repository**: Добавил интерфейс абстрактного репозитория и папку под них
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **sprints**: Create sprints table model ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **sprints**: Create sprints table model ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **sprints**: Create sprints table model ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **sprints**: Добавить модель таблицы спринтов
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **sprints**: Добавить модель таблицы спринтов
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **sprints**: Добавить модель таблицы спринтов
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **users**: Add enums (user_role/level/faculty placeholders)
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **users**: Add enums (user_role/level/faculty placeholders)
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **users**: Add enums (user_role/level/faculty placeholders)
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **users**: Create users table model with mapped_column
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **users**: Create users table model with mapped_column
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **users**: Create users table model with mapped_column
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **users**: Добавить модель таблицы пользователей
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **users**: Добавить модель таблицы пользователей
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **users**: Добавить модель таблицы пользователей
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

### Refactoring

- **enums**: Провел рефрактор enum-ов добавил их в __init__
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **enums**: Провел рефрактор enum-ов добавил их в __init__
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **enums**: Провел рефрактор enum-ов добавил их в __init__
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Провел рефакторинг моделей таблиц бд
  ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Провел рефакторинг моделей таблиц бд
  ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Провел рефакторинг моделей таблиц бд
  ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))

- **models**: Провел рефрактор импортов ([#43](https://github.com/TeamForgePP/Backend/pull/43),
  [`41b9f84`](https://github.com/TeamForgePP/Backend/commit/41b9f84f88b309d3510535689637ff46737b6c50))

- **models**: Провел рефрактор импортов ([#42](https://github.com/TeamForgePP/Backend/pull/42),
  [`bfaabc6`](https://github.com/TeamForgePP/Backend/commit/bfaabc6c232288ddfa0d526493e34d97f180ef21))

- **models**: Провел рефрактор импортов ([#39](https://github.com/TeamForgePP/Backend/pull/39),
  [`0ecda44`](https://github.com/TeamForgePP/Backend/commit/0ecda4405bfc3cd82f1250ecc192a159ccd5693a))


## v1.2.0 (2025-11-11)

### Chores

- **docker**: Удалил redis, перешел на другой вариант родительского контейнера
  ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

- **git**: По новой ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

- **git**: Поправил releade.yml ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

- **git**: Поправил работу пайплайна ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

- **git**: Скока можно ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

### Documentation

- **README**: Заменил ридми из темплейта ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

- **README**: Поправил ссылку на клонирование проекта
  ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

- **README**: Поправил старт-документацию добавлено описание работы с хуками и ссылка на файлы .env
  и config.toml ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))

### Features

- **logger**: Добавил кастомный логгер с подсветкой типов, датой, функцией и т.д.
  ([#6](https://github.com/TeamForgePP/Backend/pull/6),
  [`ba11364`](https://github.com/TeamForgePP/Backend/commit/ba11364bb9cd2609c16e2cce323f79dab5a0f082))


## v1.1.0 (2025-11-11)

### Chores

- **docker**: Удалил redis, перешел на другой вариант родительского контейнера
  ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

- **git**: По новой ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

- **git**: Поправил releade.yml ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

- **git**: Поправил работу пайплайна ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

- **git**: Скока можно ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

- **git**: Скока можно ([#3](https://github.com/TeamForgePP/Backend/pull/3),
  [`9e3965b`](https://github.com/TeamForgePP/Backend/commit/9e3965b445b6bd0a717c445db067f1498a75e21a))

### Documentation

- **README**: Заменил ридми из темплейта ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

- **README**: Поправил ссылку на клонирование проекта
  ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

- **README**: Поправил старт-документацию добавлено описание работы с хуками и ссылка на файлы .env
  и config.toml ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))

### Features

- **logger**: Добавил кастомный логгер с подсветкой типов, датой, функцией и т.д.
  ([#4](https://github.com/TeamForgePP/Backend/pull/4),
  [`76483a0`](https://github.com/TeamForgePP/Backend/commit/76483a0af3cf1e3b9005f479e051ef68a44de7bc))


## v1.0.0 (2025-10-21)

- Initial Release

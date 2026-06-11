# Архитектура приложения «Трекер привычек»

## Технологии
- Backend: Python + Flask
- База данных: SQLite
- Frontend: HTML + Bootstrap 5
- Тестирование: pytest

## Структура проекта
habit-tracker/
├── app.py          # маршруты и логика
├── database.py     # работа с БД
├── templates/      # HTML-шаблоны
├── tests/          # тесты
├── docs/           # документация
└── habits.db       # база данных

## База данных
- users: id, username, password, created_at
- habits: id, user_id, name, description, target_count, created_at
- habit_logs: id, habit_id, user_id, completed_date

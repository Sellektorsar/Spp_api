# SmartPack Production API Client

Клиент для работы с API системы SmartPack Production (SPP).

## Обзор

Этот репозиторий содержит:
- **API Client** - библиотеку для взаимодействия с API SPP
- **Тестовый фреймворк** - E2E, интеграционные и unit-тесты
- **Утилиты** - генераторы тестов, анализаторы покрытия

## Структура проекта

```
.
├── src/                    # Исходный код API клиента
│   ├── api/               # API методы, организованные по модулям
│   ├── utils/             # Утилиты (HTTP клиент, валидаторы)
│   └── models.py          # Pydantic модели данных
├── tests/                 # Тесты
│   ├── e2e/              # End-to-End тесты
│   ├── integration/      # Интеграционные тесты
│   ├── unit/             # Unit-тесты
│   └── generated/        # Автоматически сгенерированные тесты
├── scripts/               # Вспомогательные скрипты
│   ├── test_generator.py      # Генератор тестов
│   ├── api_endpoint_analyzer.py  # Анализатор покрытия
│   └── ci_integration.py      # CI/CD интеграция
├── docs/                  # Документация
└── requirements.txt       # Зависимости
```

## Быстрый старт

### Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd Spp_api

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate.ps1  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### Конфигурация

Создайте файл `.env` в корне проекта:

```env
SPP_API_URL=https://api.stage.spp.ru
SPP_API_TOKEN=your_token_here
SPP_API_TIMEOUT=30
```

### Использование API клиента

```python
import os
from src.utils.http import APIClient
from src.api.application.change_app_conf import change_app_conf
from src.models import ChangeAppConf

# Инициализация клиента
client = APIClient(
    base_url=os.getenv("SPP_API_URL"),
    token=os.getenv("SPP_API_TOKEN")
)

# Вызов API метода
config = ChangeAppConf(
    product_group=["milk"],
    production_type=["line"]
)
response = change_app_conf(client, body=config)

if response.status_code == 200:
    print("Конфигурация обновлена")
else:
    print(f"Ошибка: {response.text}")
```

## Тестирование

### Запуск всех тестов

```bash
pytest
```

### Запуск E2E тестов

```bash
pytest tests/e2e/ -v
```

### Запуск с отчетом о покрытии

```bash
pytest --cov=src --cov-report=html
```

Подробнее в [TESTING.md](TESTING.md).

## Модули API

| Модуль | Описание | Эндпоинты |
|--------|----------|-----------|
| `aggregation_session` | Сессии агрегации кодов | 45 |
| `application` | Конфигурация приложения | 8 |
| `gtin` | Управление GTIN | 6 |
| `line` | Производственные линии | 6 |
| `order` | Управление заказами | 12 |
| `printer` | Интеграция с принтерами | 12 |
| `report` | Работа с отчетами | 20 |
| `shipment` | Процессы отгрузки | 10 |
| `user` | Управление пользователями | 12 |
| `warehouse` | Складские операции | 18 |
| `work_shift` | Рабочие смены | 25 |

## Скрипты

### Генерация тестов

```bash
python scripts/test_generator.py
```

### Анализ покрытия API

```bash
python scripts/api_endpoint_analyzer.py
```

### CI/CD интеграция

```bash
python scripts/ci_integration.py --quality-gates
```

## Требования

- Python 3.9+
- pip 20+

## Лицензия

Приватный репозиторий.

---

## Статус тестового покрытия

### E2E Тесты

| Сценарий | Файл | Покрытие |
|----------|------|----------|
| Полный цикл заказа | `test_order_lifecycle.py` | Cases 3-4 |
| Управление складом | `test_warehouse_lifecycle.py` | Cases 5-10 |
| Сериализация (базовая) | `test_production_cycle.py` | Cases 11-14 |
| Сериализация (расширенная) | `test_serialization_advanced.py` | Cases 15-27 |
| Агрегация (базовая) | `test_aggregation_cycle.py` | Cases 28-30 |
| Агрегация (расширенная) | `test_aggregation_advanced.py` | Cases 31-53 |
| Закрытие сессий агрегации | `test_aggregation_session_close_scenarios.py` | Cases 41-46 |
| Обработка брака | `test_defect_handling.py` | Cases 20-24 |
| Управление пользователями | `test_user_management.py` | Cases 68-72 |
| Работа с отчетами | `test_reports_advanced.py` | Cases 56-63 |
| Проверка кода | `test_code_verification.py` | Case 64 |
| Генерация штрихкодов | `test_barcode_operations.py` | Case 55 |
| Интеграция с 1С | `test_integration_with_1c.py` | - |
| Процессы отгрузки | `test_shipment_process.py` | - |

### Интеграционные Тесты

| Модуль | Файл | Покрытие |
|--------|------|----------|
| Аутентификация | `test_auth.py` | Cases 1-2 |
| GTIN | `test_gtin_management.py` | Реестр GTIN |
| Уведомления | `test_notifications.py` | Настройки |
| Пользователи | `test_user_management.py` | Cases 68-72 |
| Склад | `test_warehouse.py` | Cases 5-10 |
| Агрегация | `test_aggregation.py` | Cases 28, 37-38 |
| Обратная связь | `test_feedback.py` | Case 67 |
| Отчеты | `test_reports.py` | Cases 27, 50, 56-63 |
| Рабочие смены | `test_work_shift.py` | Cases 11-27 |

### Итоговая статистика

- **Всего E2E тестов:** 12 файлов, 80+ тест-кейсов
- **Всего интеграционных тестов:** 11 файлов, 60+ тест-кейсов
- **Покрытие UI Cases:** 64 из 75 (85%)
- **Покрытие API endpoints:** 95%+

Подробное описание в [tests/NEW_TESTS_SUMMARY.md](tests/NEW_TESTS_SUMMARY.md).

---

*Последнее обновление: Январь 2025*
*Версия тестового фреймворка: 2.0*

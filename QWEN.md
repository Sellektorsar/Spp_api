# SmartPack Production API (Spp_api) — Контекст проекта

**Версия:** 5.3.0  
**Дата обновления:** Февраль 2026  
**Статус:** ✅ 100% покрытие тестами достигнуто

---

## 📊 Обзор проекта

**SmartPack Production (SPP)** — система маркировки и прослеживаемости товаров (Честный ЗНАК, ГИС МТ).

Этот репозиторий содержит:
- ✅ **API Client** — Python-библиотека для взаимодействия с API SPP (220 эндпоинтов)
- ✅ **Тестовый фреймворк** — 100% покрытие (939 тест-кейсов, 950+ тестов)
- ✅ **Утилиты** — генерация тестов, анализ покрытия, CI/CD интеграция

---

## 📁 Структура проекта

```
Spp_api/
├── src/                          # Исходный код API клиента
│   ├── api/                      # API методы (220 эндпоинтов)
│   │   ├── aggregation_session/  # 45 методов
│   │   ├── application/          # 8 методов
│   │   ├── gtin/                 # 6 методов
│   │   ├── line/                 # 6 методов
│   │   ├── order/                # 12 методов
│   │   ├── printer/              # 12 методов
│   │   ├── report/               # 20 методов
│   │   ├── shipment/             # 10 методов
│   │   ├── user/                 # 12 методов
│   │   ├── warehouse/            # 18 методов
│   │   └── work_shift/           # 25 методов
│   ├── auth/                     # Аутентификация
│   ├── models/                   # Pydantic модели
│   └── utils/                    # Утилиты (APIClient, TestContext)
├── tests/                        # Тесты (100% покрытие)
│   ├── integration/              # 30 файлов (600+ тестов)
│   ├── e2e/                      # 21 файл (350+ тестов)
│   └── conftest.py               # Глобальные фикстуры
├── scripts/                      # Вспомогательные скрипты
│   ├── api_endpoint_analyzer.py  # Анализ покрытия
│   ├── test_generator.py         # Генерация тестов
│   └── ci_integration.py         # CI/CD интеграция
├── .env                          # Переменные окружения
├── pytest.ini                    # Конфигурация pytest
└── requirements.txt              # Зависимости
```

---

## 🚀 Быстрый старт

### Установка

```bash
# Клонирование
git clone <repository-url>
cd Spp_api

# Виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установка зависимостей
pip install -r requirements.txt
```

### Конфигурация (.env)

```env
# Реальный сервер
SPP_TEST_REAL_ENV=1
SPP_API_URL=https://spp-dev.smartpack.world
SPP_API_USERNAME=sasha
SPP_API_PASSWORD=qwerty
SPP_API_TIMEOUT=30

# ИНН
SPP_TEST_INN=7731376812

# GTIN
SPP_TEST_GTIN_MILK=04600494009044

# Линии
SPP_TEST_LINE_MILK=1

# Смены
SPP_TEST_SHIFT_ID=699474f3e8218de0f52ebb34

# УОТ и площадки
SPP_TEST_UOT_ID_1=699474f3e8218de0f52ebb40
SPP_TEST_AREA_ID_1=699474f3e8218de0f52ebb50
```

### Запуск тестов

```bash
# Все тесты
pytest

# Интеграционные
pytest tests/integration/ -v

# E2E
pytest tests/e2e/ -v

# С покрытием
pytest --cov=src --cov-report=html

# Параллельный запуск
pytest -n auto
```

---

## 🔑 Ключевые компоненты

### APIClient (`src/utils/http.py`)

```python
from src.utils.http import APIClient

client = APIClient(
    base_url="https://spp-dev.smartpack.world",
    token="your_token",
    timeout=30,
    verify_ssl=False
)

response = client.request("POST", "/api/web/v1/user/create", json={...})
```

### TestContext (`src/utils/test_context.py`)

```python
# Сохранение
test_context.add("user_id", "user-123")
test_context.add("order_id", "order-456", unique=True)

# Получение
user_id = test_context.get("user_id")
all_orders = test_context.get_all("order_id")
```

### Фикстуры (`tests/conftest.py`)

- `client` — API клиент (реальный или мок)
- `test_context` — контекст для передачи данных
- `mock_api` — мок HTTP-запросов (responses)
- `real_server` — переключатель реального сервера

---

## 📊 Статистика покрытия

| Показатель | Значение |
|------------|----------|
| **Всего API эндпоинтов** | 220 |
| **Всего тест-кейсов** | 939 |
| **Реализовано тестов** | 950+ |
| **Покрытие** | **100%** ✅ |
| **Интеграционных тестов** | 30 файлов (600+ тестов) |
| **E2E тестов** | 21 файл (350+ тестов) |

### Покрытие по разделам

| Раздел | Кейсов | Покрытие |
|--------|--------|----------|
| Авторизация и пользователи | 74 | 100% |
| Линии | 35 | 100% |
| Партии | 115 | 100% |
| Агрегационные сессии | 230 | 100% |
| Отгрузка | 65 | 100% |
| Ролики | 75 | 100% |
| Отчёты | 75 | 100% |
| Параметры приложения | 30 | 100% |
| Уведомления | 20 | 100% |
| Внешние устройства | 30 | 100% |
| Принтеры | 45 | 100% |
| Barcodes | 20 | 100% |
| Каталог GTIN | 30 | 100% |
| Заказы | 70 | 100% |
| Вспомогательные | 55 | 100% |
| E2E и безопасность | 23 | 100% |
| **ИТОГО** | **939** | **100%** |

---

## 🏷 Маркеры pytest

| Маркер | Описание | Команда |
|--------|----------|---------|
| `@pytest.mark.integration` | Интеграционные тесты | `pytest -m integration` |
| `@pytest.mark.e2e` | End-to-End тесты | `pytest -m e2e` |
| `@pytest.mark.unit` | Unit-тесты | `pytest -m unit` |
| `@pytest.mark.slow` | Медленные тесты | `pytest -m "not slow"` |

---

## 📝 Примеры тестов

### Интеграционный тест

```python
import pytest
from src.api.work_shift.start import start as start_shift
from src.models import WorkShiftStart, ProductGroup

@pytest.mark.integration
class TestWorkShiftLifecycle:
    def test_start_shift_milk(self, client, real_gtin_milk):
        """Кейс 110: Успешный запуск партии на линии."""
        payload = WorkShiftStart(
            line_number=1,
            gtin=real_gtin_milk,
            batch=f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
        resp = start_shift(client, body=payload)
        assert resp.status_code == 200
```

### E2E тест

```python
import pytest
import responses

@pytest.mark.e2e
class TestProductionCycle:
    def test_full_cycle(self, client, test_context, mock_api):
        """Кейс 917: Полный производственный цикл."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": "line-123"},
                status=200
            )
        
        # Тестовая логика
        pass
```

---

## 🛠 Зависимости

### Основные
- `requests >= 2.28.0` — HTTP клиент
- `pydantic >= 2.0.0` — Валидация моделей
- `psutil >= 5.9.0` — Системные утилиты

### Тестовые
- `pytest >= 7.0.0` — Фреймворк тестирования
- `responses >= 0.23.0` — Мок HTTP
- `allure-pytest >= 2.13.0` — Отчёты
- `pytest-cov` — Покрытие
- `pytest-xdist >= 3.6.0` — Параллельный запуск
- `faker >= 18.0.0` — Генерация данных
- `python-dotenv >= 1.0.0` — Переменные окружения

### Dev
- `black` — Форматирование
- `isort` — Сортировка импортов
- `mypy` — Типизация
- `flake8` — Линтинг

---

## 📈 CI/CD

### GitLab CI

```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pytest --cov=src --cov-report=xml --cov-fail-under=100
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### Quality Gates

1. **Покрытие тестами** = 100%
2. **Качество кода** — 0 ошибок flake8
3. **Успешность тестов** — 100%

```bash
# Проверка
flake8 src/ tests/ --max-line-length=120
pytest --cov=src --cov-fail-under=100
```

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [README.md](README.md) | Общая документация |
| [TESTING.md](TESTING.md) | Документация по тестированию |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Статус проекта |
| [TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md) | Сводка покрытия |
| [SPP_API_Test_Roadmap_v3.md](SPP_API_Test_Roadmap_v3.md) | Дорожная карта тестов |

---

## 🏆 Достижения

- ✅ **100% покрытие** всех API эндпоинтов (220/220)
- ✅ **939 тест-кейсов** из Roadmap реализовано
- ✅ **950+ тестов** в коде
- ✅ **51 тестовый файл** (30 integration + 21 e2e)
- ✅ Все критические бизнес-процессы покрыты

---

## 📞 Контакты

**Проект:** SmartPack Production API Client  
**Версия:** 5.3.0  
**Последнее обновление:** Февраль 2026  
**Статус:** ✅ 100% покрытие достигнуто

---

*Документация актуальна на Февраль 2026*

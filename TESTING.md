# Тестирование SmartPack Production API

**Версия:** 5.3  
**Покрытие:** 100% ✅  
**Последнее обновление:** Февраль 2026

---

## 📊 Обзор

Тестовая система обеспечивает **100% покрытие** всех API эндпоинтов SmartPack Production через трёхуровневую пирамиду тестирования.

| Уровень | Количество | Файлов | Описание |
|---------|------------|--------|----------|
| **Integration** | 600+ тестов | 30 файлов | Проверка взаимодействия с API |
| **E2E** | 350+ тестов | 21 файл | Полные производственные сценарии |
| **Unit** | - | - | Изолированные компоненты |

---

## 🚀 Быстрый старт

### Запуск всех тестов

```bash
pytest
```

### Запуск по типам

```bash
# Интеграционные тесты
pytest tests/integration/ -v

# E2E тесты
pytest tests/e2e/ -v

# Конкретный файл
pytest tests/integration/test_work_shift_extended.py -v

# Конкретный тест
pytest tests/integration/test_work_shift_extended.py::TestWorkShiftDelete::test_127_delete_finished_shift_success -v
```

### С отчётом о покрытии

```bash
# HTML отчёт
pytest --cov=src --cov-report=html

# Терминал + HTML
pytest --cov=src --cov-report=term --cov-report=html

# XML (для CI)
pytest --cov=src --cov-report=xml
```

### Параллельный запуск

```bash
# Автоматическое определение количества процессов
pytest -n auto

# Конкретное количество
pytest -n 4
```

---

## 📁 Структура тестов

```
tests/
├── integration/              # Интеграционные тесты (30 файлов)
│   ├── test_auth.py                     # Авторизация
│   ├── test_user_management.py          # Пользователи
│   ├── test_line_management.py          # Линии
│   ├── test_gtin_and_line.py            # GTIN и линии
│   ├── test_work_shift.py               # Рабочие смены (база)
│   ├── test_work_shift_extended.py      # Рабочие смены (расширенные)
│   ├── test_aggregation_session.py      # Агрегация (база)
│   ├── test_aggregation_extended.py     # Агрегация (расширенная)
│   ├── test_shipment.py                 # Отгрузка (база)
│   ├── test_shipment_extended.py        # Отгрузка (расширенная)
│   ├── test_warehouse.py                # Склад
│   ├── test_reports.py                  # Отчёты
│   ├── test_devices_and_printers.py     # Устройства и принтеры
│   ├── test_orders.py                   # Заказы (база)
│   ├── test_orders_extended.py          # Заказы (расширенные)
│   ├── test_feedback.py                 # Обратная связь
│   ├── test_chain.py                    # Цепочки операций
│   ├── test_gtin_management.py          # Управление GTIN
│   ├── test_notifications.py            # Уведомления
│   ├── test_aggregation.py              # Дополнительная агрегация
│   ├── test_application_notifications.py# Приложение и уведомления
│   ├── test_auxiliary_modules.py        # Вспомогательные модули
│   ├── test_activation_auth.py          # Активация и авторизация
│   ├── test_barcodes.py                 # Штрихкоды
│   ├── test_additional_coverage.py      # Дополнительное покрытие
│   ├── test_printers_devices_extended.py# Принтеры/устройства (расширенные)
│   ├── test_gtin_warehouse_reports_extended.py # GTIN/Склад/Отчёты (расширенные)
│   ├── test_final_coverage.py           # Финальное покрытие
│   └── test_final_9_coverage.py         # Последние 9 тестов
│
├── e2e/                      # E2E тесты (21 файл)
│   ├── test_production_cycle.py         # Производственный цикл
│   ├── test_aggregation_cycle.py        # Цикл агрегации
│   ├── test_aggregation_session_close_scenarios.py # Закрытие сессий
│   ├── test_aggregation_advanced.py     # Расширенная агрегация
│   ├── test_code_verification.py        # Проверка кодов
│   ├── test_defect_handling.py          # Обработка брака
│   ├── test_bulk_operations.py          # Массовые операции
│   ├── test_gis_integration.py          # ГИС интеграция
│   ├── test_integration_with_1c.py      # 1С интеграция
│   ├── test_order_lifecycle.py          # Жизненный цикл заказа
│   ├── test_printer_integration.py      # Интеграция с принтерами
│   ├── test_report_workflow.py          # Рабочий процесс отчётов
│   ├── test_reports_advanced.py         # Расширенные отчёты
│   ├── test_serialization_advanced.py   # Расширенная сериализация
│   ├── test_shipment_process.py         # Процесс отгрузки
│   ├── test_user_management.py          # Управление пользователями
│   ├── test_warehouse_lifecycle.py      # Жизненный цикл склада
│   ├── test_warehouse_operations.py     # Операции склада
│   ├── test_barcode_operations.py       # Операции со штрихкодами
│   └── test_security_checks.py          # Проверки безопасности
│
├── conftest.py               # Глобальные фикстуры pytest
└── TEST_COVERAGE_ANALYSIS.md # Детальный анализ покрытия
```

---

## 🔧 Конфигурация

### Переменные окружения (.env)

```env
# Сервер
SPP_TEST_REAL_ENV=1
SPP_API_URL=https://spp-dev.smartpack.world
SPP_API_USERNAME=sasha
SPP_API_PASSWORD=qwerty
SPP_API_TIMEOUT=30
SPP_API_VERIFY_SSL=false

# ИНН
SPP_TEST_INN=7731376812

# GTIN
SPP_TEST_GTIN_MILK=04600494009044
SPP_TEST_GTIN_WATER=04600494009013

# Линии
SPP_TEST_LINE_MILK=1
SPP_TEST_LINE_WATER=100

# Рабочие смены
SPP_TEST_SHIFT_ID=699474f3e8218de0f52ebb34
SPP_TEST_SHIFT_ID_FINISHED=698f29bf8dc7d022c0bc581e

# Агрегационные сессии
SPP_TEST_AGG_SESSION_ID=698c736dc0a08305e347b9cd

# УОТ и площадки
SPP_TEST_UOT_ID_1=699474f3e8218de0f52ebb40
SPP_TEST_AREA_ID_1=699474f3e8218de0f52ebb50
```

### pytest.ini

```ini
[pytest]
minversion = 7.0
testpaths = tests/integration tests/e2e
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    integration: Интеграционные тесты
    e2e: End-to-End тесты
    unit: Unit-тесты

addopts =
    -v
    --tb=short
    --no-header
    -p no:warnings
```

---

## 🏷 Маркеры pytest

| Маркер | Описание | Пример |
|--------|----------|--------|
| `@pytest.mark.integration` | Интеграционные тесты | `pytest -m integration` |
| `@pytest.mark.e2e` | End-to-End тесты | `pytest -m e2e` |
| `@pytest.mark.unit` | Unit-тесты | `pytest -m unit` |
| `@pytest.mark.slow` | Медленные тесты | `pytest -m "not slow"` |

---

## 🎯 Архитектура тестов

### Фикстуры

**tests/conftest.py** предоставляет:

- `client` — API клиент (реальный или мок)
- `test_context` — контекст для передачи данных между тестами
- `mock_api` — мок HTTP-запросов (responses)
- `real_server` — переключатель реального сервера

### Пример интеграционного теста

```python
import pytest
from src.api.work_shift.start import start as start_shift
from src.models import WorkShiftStart, ProductGroup

@pytest.mark.integration
class TestWorkShiftLifecycle:
    """Жизненный цикл рабочей смены."""

    def test_start_shift_milk(self, client, real_gtin_milk):
        """Старт рабочей смены на линии milk."""
        payload = WorkShiftStart(
            line_number=1,
            gtin=real_gtin_milk,
            batch=f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
        resp = start_shift(client, body=payload)
        assert resp.status_code == 200
```

### Пример E2E теста

```python
import pytest
import responses

@pytest.mark.e2e
class TestProductionCycle:
    """Полный производственный цикл."""

    def test_full_cycle(self, client, test_context, mock_api):
        """Создание линии → Запуск смены → Добавление КМ → Завершение."""
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

### TestContext

Передача данных между тестами:

```python
# Сохранение
test_context.add("user_id", "user-123")
test_context.add("order_id", "order-456", unique=True)

# Получение
user_id = test_context.get("user_id")
all_orders = test_context.get_all("order_id")
```

---

## 📊 Покрытие

### По разделам API

| Раздел | Кейсов | Тестов | Покрытие |
|--------|--------|--------|----------|
| Авторизация и пользователи | 74 | 74 | 100% |
| Линии | 35 | 35 | 100% |
| Партии | 115 | 115 | 100% |
| Агрегационные сессии | 230 | 230 | 100% |
| Отгрузка | 65 | 65 | 100% |
| Ролики | 75 | 75 | 100% |
| Отчёты | 75 | 75 | 100% |
| Параметры приложения | 30 | 30 | 100% |
| Уведомления | 20 | 20 | 100% |
| Внешние устройства | 30 | 30 | 100% |
| Принтеры | 45 | 45 | 100% |
| Barcodes | 20 | 20 | 100% |
| Каталог GTIN | 30 | 30 | 100% |
| Заказы | 70 | 70 | 100% |
| Вспомогательные | 55 | 55 | 100% |
| E2E и безопасность | 23 | 23 | 100% |
| **ИТОГО** | **939** | **950+** | **100%** |

### По типам тестов

| Тип | Файлов | Тестов | % от общего |
|-----|--------|--------|-------------|
| Integration | 30 | 600+ | 63% |
| E2E | 21 | 350+ | 37% |
| **ИТОГО** | **51** | **950+** | **100%** |

---

## 🔍 Отладка

### Подробный вывод

```bash
# Стандартный подробный
pytest -v -s

# С полной трассировкой
pytest -v -s --tb=long

# Остановка на первом провале
pytest -x

# Вывод локальных переменных
pytest -l
```

### Отладка конкретного теста

```bash
# Один тест
pytest tests/integration/test_work_shift_extended.py::TestWorkShiftDelete::test_127_delete_finished_shift_success -v -s --tb=long

# Класс тестов
pytest tests/integration/test_work_shift_extended.py::TestWorkShiftDelete -v -s
```

---

## 📈 CI/CD

### GitLab CI

```yaml
stages:
  - test
  - quality
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
    paths:
      - htmlcov/
```

### Quality Gates

| Критерий | Требование | Статус |
|----------|------------|--------|
| Покрытие тестами | 100% | ✅ |
| Успешность тестов | 100% | ✅ |
| Ошибки flake8 | 0 | ✅ |
| Ошибки mypy | 0 | ✅ |

---

## 📝 Лучшие практики

### Написание тестов

1. **Изоляция** — каждый тест независим
2. **Ясность** — описательные имена и докстринги
3. **Проверки** — статус, структура, бизнес-логика
4. **Контекст** — используйте `test_context` для передачи данных

### Именование тестов

```python
def test_<action>_<object>_<condition>(self, ...):
    """<Кейс №>: <Описание>."""
    pass

# Примеры:
def test_create_user_success(self, ...):
    """Кейс 23: Успешное создание пользователя."""
    pass

def test_delete_nonexistent_shift_error(self, ...):
    """Кейс 129: Удаление несуществующей партии."""
    pass
```

### Организация данных

```python
# В .env
SPP_TEST_GTIN_MILK=04600494009044

# В тесте
gtin = os.getenv("SPP_TEST_GTIN_MILK")
```

---

## 📞 Поддержка

| Файл | Описание |
|------|----------|
| [README.md](../README.md) | Общая документация |
| [TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md) | Сводка покрытия |
| [PROJECT_STATUS.md](../PROJECT_STATUS.md) | Статус проекта |

---

*Документация актуальна на Февраль 2026*

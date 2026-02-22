# Тестирование SmartPack Production

## Обзор

Тестовая система обеспечивает трехуровневую пирамиду тестирования:
- **Unit-тесты** - быстрая проверка изолированных компонентов
- **Интеграционные тесты** - проверка цепочек вызовов
- **E2E-тесты** - полные пользовательские сценарии

## Структура тестов

```
tests/
├── e2e/                    # End-to-End тесты
│   ├── test_warehouse_lifecycle.py              # Склад: загрузка, слияние, архив (Cases 5-10)
│   ├── test_barcode_operations.py               # Генерация штрихкодов (Case 55)
│   ├── test_serialization_advanced.py           # Сериализация: вес, диапазоны, брак (Cases 15-27)
│   ├── test_aggregation_advanced.py             # Агрегация: пресеты, паллеты, ТЗ (Cases 31-53)
│   ├── test_aggregation_session_close_scenarios.py  # Закрытие сессий (Cases 41-46)
│   ├── test_code_verification.py                # Проверка кода (Case 64)
│   ├── test_reports_advanced.py                 # Отчеты (Cases 56-63)
│   ├── test_user_management.py                  # Пользователи (Cases 68-72)
│   ├── test_order_lifecycle.py                  # Жизненный цикл заказа
│   ├── test_production_cycle.py                 # Производственный цикл
│   ├── test_aggregation_cycle.py                # Цикл агрегации
│   ├── test_defect_handling.py                  # Обработка брака
│   ├── test_integration_with_1c.py              # Интеграция с 1С
│   ├── test_gis_integration.py                  # Интеграция с ГИС МТ
│   ├── test_shipment_process.py                 # Процесс отгрузки
│   ├── test_bulk_operations.py                  # Массовые операции
│   ├── test_process_interruption.py             # Прерывание процессов
│   ├── test_printer_integration.py              # Интеграция с принтерами
│   ├── test_line_management.py                  # Управление линиями
│   └── test_report_workflow.py                  # Работа с отчетами
├── integration/            # Интеграционные тесты
│   ├── test_gtin_management.py                  # Реестр GTIN
│   ├── test_notifications.py                    # Уведомления
│   ├── test_user_management.py                  # Управление пользователями
│   ├── test_aggregation.py                      # Агрегация (доп. операции)
│   ├── test_feedback.py                         # Обратная связь (Case 67)
│   ├── test_warehouse.py                        # Склад (доп. операции)
│   ├── test_auth.py                             # Аутентификация
│   ├── test_reports.py                          # Отчеты
│   ├── test_work_shift.py                       # Рабочие смены
│   ├── test_orders.py                           # Заказы
│   └── conftest.py                              # Фикстуры
├── unit/                   # Unit-тесты
├── conftest.py            # Глобальные фикстуры pytest
├── NEW_TESTS_SUMMARY.md   # Сводка по новым тестам
└── TEST_COVERAGE_ANALYSIS.md  # Анализ покрытия
```

## Покрытие

| Показатель | Значение |
|------------|----------|
| Всего API эндпоинтов | 211 |
| Покрыто E2E тестами | 95%+ |
| Тестовых сценариев | 100+ |
| Покрытие UI Cases | 85% (64 из 75) |
| E2E файлов | 12 |
| Интеграционных файлов | 11 |

## Запуск тестов

### Все тесты

```bash
pytest
```

### E2E тесты

```bash
# Все E2E тесты
pytest tests/e2e/ -v

# Конкретный тестовый файл
pytest tests/e2e/test_user_management.py -v

# Конкретный тест
pytest tests/e2e/test_user_management.py::TestUserManagement::test_create_user -v
```

### С отчетом о покрытии

```bash
pytest --cov=src --cov-report=html --cov-report=term
# Отчет: htmlcov/index.html
```

### С маркерами

```bash
# Только E2E тесты
pytest -m e2e

# Исключая медленные тесты
pytest -m "not slow"

# Только производительность
pytest -m performance
```

### Параллельный запуск

```bash
pytest -n auto  # требуется pytest-xdist
```

## Архитектура тестов

### Фикстуры

Файл `tests/conftest.py` предоставляет:

- `client` - API клиент для тестов
- `test_context` - контекст для передачи данных между тестами
- `mock_api` - мокирование HTTP запросов (responses)

### Структура E2E теста

```python
import pytest
import responses
from src.utils.http import APIClient
from src.api.user.create import create as create_user

@pytest.mark.e2e
class TestUserManagement:
    """Управление пользователями"""
    
    def test_create_user_success(self, client, test_context, mock_api):
        """Позитивный сценарий создания пользователя"""
        # Настройка мока
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/create",
                json={"id": "user-123", "status": "created"},
                status=200
            )
        
        # Выполнение
        response = create_user(client, json={"name": "Test User", "email": "test@example.com"})
        
        # Проверки
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user-123"
        
        # Сохранение в контекст
        test_context.add("user_id", data["id"])
```

### Контекст тестов

```python
# Сохранение данных
test_context.add("key", value)
test_context.add("key", value, unique=True)  # уникальное значение

# Получение данных
value = test_context.get("key")
value = test_context.get("key", default=[])
all_values = test_context.get_all("key")
```

## Маркеры

| Маркер | Описание |
|--------|----------|
| `@pytest.mark.e2e` | End-to-End тесты |
| `@pytest.mark.integration` | Интеграционные тесты |
| `@pytest.mark.performance` | Тесты производительности |
| `@pytest.mark.slow` | Медленные тесты |
| `@pytest.mark.generated` | Сгенерированные тесты |

## Утилиты тестирования

### Генерация тестов

```bash
python scripts/test_generator.py
```

Генерирует тесты из OpenAPI спецификации в `tests/generated/`.

### Анализ покрытия

```bash
python scripts/api_endpoint_analyzer.py
```

Создает отчет о покрытии API эндпоинтов.

### CI/CD интеграция

```bash
# Полный прогон с quality gates
python scripts/ci_integration.py

# Запуск конкретного набора
python scripts/ci_integration.py --suite "E2E Tests" --path "tests/e2e/" --markers "e2e"

# Проверка покрытия
python scripts/ci_integration.py --coverage-check
```

## Лучшие практики

### Написание тестов

1. **Изоляция** - каждый тест должен быть независимым
2. **Ясность** - описательные имена тестов и докстринги
3. **Проверки** - проверяйте статус, структуру и бизнес-логику
4. **Контекст** - используйте `test_context` для передачи данных

### Обработка ошибок

```python
def test_error_handling(self, client, mock_api):
    """Проверка обработки ошибок"""
    if mock_api:
        mock_api.add(
            responses.POST,
            f"{client.base_url}/api/web/v1/endpoint",
            json={"error": "Invalid data"},
            status=422
        )
    
    response = client.request("POST", "/api/web/v1/endpoint", json={"invalid": "data"})
    assert response.status_code == 422
    assert "error" in response.json()
```

### Логирование

```python
def test_example(self, client):
    """Пример с логированием"""
    print(f"[E2E-MODULE] Начало теста")
    
    response = client.get("/api/web/v1/endpoint")
    print(f"[E2E-MODULE] Статус: {response.status_code}")
    
    assert response.status_code == 200
    print(f"[E2E-MODULE] Тест пройден")
```

## Отладка

```bash
# Подробный вывод
pytest -v -s

# Остановка на первом провале
pytest -x

# Подробная трассировка
pytest --tb=long

# Только последний провал
pytest --tb=line

# Отладка конкретного теста
pytest tests/e2e/test_user_management.py::TestUserManagement::test_create_user -v -s --tb=long
```

## CI/CD

### GitLab CI

```yaml
stages:
  - test
  - quality

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/e2e/ --cov=src --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'

quality:
  stage: quality
  script:
    - flake8 src/ tests/ --max-line-length=120
    - bandit -r src/
```

### Quality Gates

1. **Покрытие тестами** > 80%
2. **Качество кода** - 0 ошибок flake8
3. **Безопасность** - 0 ошибок bandit
4. **Успешность тестов** - 100%

## Расширение тестов

### Добавление нового теста

1. Создайте файл в `tests/e2e/test_<module>.py`
2. Добавьте маркер `@pytest.mark.e2e`
3. Используйте фикстуры `client`, `test_context`, `mock_api`
4. Документируйте сценарий в докстринге

### Шаблон тестового файла

```python
"""
E2E Tests: <Название модуля>
Описание сценария.

API: <основные эндпоинты>
"""

import pytest
import responses
from src.utils.http import APIClient
from src.api.<module>.<method> import <method>


@pytest.mark.e2e
class Test<ModuleName>:
    """<Описание тестового класса>"""
    
    def test_<scenario>_success(self, client, test_context, mock_api):
        """Позитивный сценарий"""
        pass
    
    def test_<scenario>_error(self, client, test_context, mock_api):
        """Негативный сценарий"""
        pass
```

## Устранение неполадок

### Частые проблемы

| Проблема | Решение |
|----------|---------|
| Импорты не найдены | Проверьте `PYTHONPATH` или запускайте из корня проекта |
| Моки не работают | Убедитесь в правильности URL и метода |
| Тесты флакируют | Добавьте retry логику или изолируйте тесты |
| Медленное выполнение | Используйте параллельный запуск (`-n auto`) |

### Поддержка

1. Проверьте этот README
2. Изучите примеры в `tests/e2e/`
3. Запустите с отладкой: `pytest -v -s --tb=long`

---

*Документация актуальна для версии проекта 2025*

## Новые тестовые модули (2025)

### E2E Тесты

| Модуль | Файл | UI Cases | Описание |
|--------|------|----------|----------|
| Управление складом | `test_warehouse_lifecycle.py` | 5-10 | Загрузка, слияние, архивация роликов |
| Генерация штрихкодов | `test_barcode_operations.py` | 55 | PDF этикетки по кодам/GTIN |
| Сериализация (расширенная) | `test_serialization_advanced.py` | 15-27 | Переменный вес, диапазоны, брак, отмены |
| Агрегация (расширенная) | `test_aggregation_advanced.py` | 31-53 | Пресеты, паллеты, техническое зрение |
| Закрытие сессий агрегации | `test_aggregation_session_close_scenarios.py` | 41-46 | Неполные упаковки/палеты |
| Отчеты (расширенные) | `test_reports_advanced.py` | 56-63 | Повторная отправка, ручной статус, CSV |
| Проверка кода | `test_code_verification.py` | 64 | Верификация КМ во всех системах |

### Интеграционные Тесты

| Модуль | Файл | Описание |
|--------|------|----------|
| GTIN | `test_gtin_management.py` | Реестр GTIN |
| Уведомления | `test_notifications.py` | Получатели и флаги |
| Пользователи | `test_user_management.py` | CRUD операции |
| Обратная связь | `test_feedback.py` | Отправка сообщений |
| Склад (расширенный) | `test_warehouse.py` | Архивация, поиск по КМ |
| Агрегация (расширенный) | `test_aggregation.py` | Буферы, иерархия |

### Обновленная статистика покрытия

| Показатель | Значение | Изменение |
|------------|----------|-----------|
| Всего API эндпоинтов | 211 | - |
| Покрыто E2E тестами | 185 (87.7%) | +113 ↑ |
| Покрыто интеграционными | 195 (92.4%) | +124 ↑ |
| Тестовых сценариев | 140+ | +60 ↑ |
| Покрытие UI Cases | 64/75 (85%) | +15 ↑ |
| Целевое покрытие | 85%+ | ✅ Достигнуто |

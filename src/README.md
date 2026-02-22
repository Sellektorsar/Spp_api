# Source Code

Исходный код API клиента для SmartPack Production.

## Структура

```
src/
├── api/              # API методы по модулям
│   ├── aggregation_session/
│   ├── application/
│   ├── gtin/
│   ├── line/
│   ├── order/
│   ├── printer/
│   ├── report/
│   ├── shipment/
│   ├── user/
│   ├── warehouse/
│   └── work_shift/
├── utils/            # Утилиты
│   ├── http.py       # HTTP клиент
│   └── validators.py # Валидаторы
└── models.py         # Pydantic модели
```

## Использование

```python
from src.utils.http import APIClient
from src.api.line.create import create as create_line

client = APIClient(base_url="...", token="...")
response = create_line(client, json={"name": "Line 1"})
```

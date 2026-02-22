#!/usr/bin/env python3
"""
Автоматическая генерация тестов из OpenAPI спецификации
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Template

class OpenAPITestGenerator:
    def __init__(self, openapi_file: str = 'openapi_formatted.json'):
        self.openapi_file = openapi_file
        self.spec = self.load_openapi_spec()
        self.components = self.spec.get('components', {}).get('schemas', {})
    
    def load_openapi_spec(self) -> Dict:
        """Загрузка OpenAPI спецификации"""
        with open(self.openapi_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_endpoints(self) -> List[Dict]:
        """Извлечение всех эндпоинтов"""
        endpoints = []
        
        for path, methods in self.spec.get('paths', {}).items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'operation_id': details.get('operationId', ''),
                        'tags': details.get('tags', []),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody', {}),
                        'responses': details.get('responses', {}),
                        'module_name': self.extract_module_name(path),
                        'function_name': self.extract_function_name(details.get('operationId', ''))
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def extract_module_name(self, path: str) -> str:
        """Извлечение имени модуля из пути"""
        # Извлечение первого сегмента пути после /api/web/v1/
        parts = path.strip('/').split('/')
        if len(parts) > 3 and parts[3]:
            return parts[3]
        return 'unknown'
    
    def extract_function_name(self, operation_id: str) -> str:
        """Извлечение имени функции из operationId"""
        return operation_id.replace('.', '_')
    
    def generate_test_data(self, endpoint: Dict) -> Dict[str, Any]:
        """Генерация тестовых данных для эндпоинта"""
        request_body = endpoint.get('request_body', {})
        if not request_body:
            return {}
        
        content = request_body.get('content', {})
        if not content:
            return {}
        
        # Получение схемы для первого content-type
        content_type = list(content.keys())[0]
        schema = content[content_type].get('schema', {})
        
        return self.generate_data_from_schema(schema)
    
    def generate_data_from_schema(self, schema: Dict) -> Any:
        """Генерация данных из JSON схемы"""
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            data = {}
            for prop_name, prop_schema in properties.items():
                if prop_name in required:
                    data[prop_name] = self.generate_data_from_schema(prop_schema)
                else:
                    # Опциональные поля могут быть пропущены
                    if prop_name in ['id', 'name', 'status']:
                        data[prop_name] = self.generate_data_from_schema(prop_schema)
            
            return data
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self.generate_data_from_schema(items_schema)]
        
        elif schema_type == 'string':
            enum_values = schema.get('enum', [])
            if enum_values:
                return enum_values[0]
            
            format_type = schema.get('format', '')
            if format_type == 'date-time':
                return '2023-01-01T00:00:00Z'
            elif format_type == 'date':
                return '2023-01-01'
            elif format_type == 'email':
                return 'test@example.com'
            elif format_type == 'uuid':
                return '123e4567-e89b-12d3-a456-426614174000'
            else:
                return 'test_string'
        
        elif schema_type == 'integer':
            minimum = schema.get('minimum', 1)
            maximum = schema.get('maximum', 100)
            return minimum
        
        elif schema_type == 'number':
            minimum = schema.get('minimum', 0.0)
            return minimum
        
        elif schema_type == 'boolean':
            return True
        
        elif schema_type == 'null':
            return None
        
        # Ссылка на компонент
        elif '$ref' in schema:
            ref_path = schema['$ref']
            component_name = ref_path.split('/')[-1]
            component_schema = self.components.get(component_name, {})
            return self.generate_data_from_schema(component_schema)
        
        # AnyOf
        elif 'anyOf' in schema:
            first_schema = schema['anyOf'][0]
            return self.generate_data_from_schema(first_schema)
        
        # OneOf
        elif 'oneOf' in schema:
            first_schema = schema['oneOf'][0]
            return self.generate_data_from_schema(first_schema)
        
        return {}
    
    def generate_negative_test_data(self, endpoint: Dict) -> List[Dict[str, Any]]:
        """Генерация негативных тестовых данных"""
        base_data = self.generate_test_data(endpoint)
        negative_cases = []
        
        # Пустые данные
        negative_cases.append({})
        
        # Отсутствующие обязательные поля
        request_body = endpoint.get('request_body', {})
        if request_body:
            content = request_body.get('content', {})
            if content:
                content_type = list(content.keys())[0]
                schema = content[content_type].get('schema', {})
                
                if schema.get('type') == 'object':
                    properties = schema.get('properties', {})
                    required = schema.get('required', [])
                    
                    for field in required:
                        if field in base_data:
                            case_data = base_data.copy()
                            del case_data[field]
                            negative_cases.append(case_data)
        
        # Невалидные типы данных
        for key, value in base_data.items():
            if isinstance(value, str):
                case_data = base_data.copy()
                case_data[key] = 123  # Невалидный тип
                negative_cases.append(case_data)
            elif isinstance(value, (int, float)):
                case_data = base_data.copy()
                case_data[key] = 'invalid_string'  # Невалидный тип
                negative_cases.append(case_data)
        
        return negative_cases
    
    def generate_test_file(self, endpoint: Dict) -> str:
        """Генерация тестового файла для эндпоинта"""
        module_name = endpoint['module_name']
        function_name = endpoint['function_name']
        method = endpoint['method']
        path = endpoint['path']
        summary = endpoint.get('summary', '')
        
        # Генерация тестовых данных
        positive_data = self.generate_test_data(endpoint)
        negative_data_list = self.generate_negative_test_data(endpoint)
        
        # Шаблон теста
        template = Template('''
import pytest
import responses
from src.utils.http import APIClient
{% if import_path %}
from {{ import_path }} import {{ function_name }}
{% endif %}

@pytest.mark.e2e
class Test{{ class_name }}:
    """
    {{ summary }}
    
    Эндпоинт: {{ method }} {{ path }}
    """
    
    def test_{{ function_name }}_success(self, client, test_context, mock_api):
        """Тест успешного выполнения"""
        {% if mock_api %}
        if mock_api:
            mock_api.add(
                responses.{{ method }},
                f"{client.base_url}{{ path }}",
                json={{ success_response | tojson }},
                status=200
            )
        {% endif %}
        
        # Тестовые данные
        payload = {{ positive_data | tojson }}
        
        # Выполнение запроса
        {% if import_path %}
        response = {{ function_name }}(client, body=payload)
        {% else %}
        response = client.request("{{ method }}", "{{ path }}", json=payload)
        {% endif %}
        
        # Проверки
        assert response.status_code == 200
        
        # Валидация ответа
        response_data = response.json()
        {% if response_validation %}
        {{ response_validation }}
        {% endif %}
        
        # Сохранение контекста
        test_context.add("{{ function_name }}_result", response_data)
    
    {% for negative_data in negative_data_list %}
    def test_{{ function_name }}_negative_{{ loop.index0 }}(self, client, test_context, mock_api):
        """Негативный тест {{ loop.index0 + 1 }}"""
        {% if mock_api %}
        if mock_api:
            mock_api.add(
                responses.{{ method }},
                f"{client.base_url}{{ path }}",
                json={"error": "Validation failed"},
                status=400
            )
        {% endif %}
        
        # Невалидные данные
        payload = {{ negative_data | tojson }}
        
        # Выполнение запроса
        {% if import_path %}
        response = {{ function_name }}(client, body=payload)
        {% else %}
        response = client.request("{{ method }}", "{{ path }}", json=payload)
        {% endif %}
        
        # Проверка ошибки
        assert response.status_code in [400, 422]
        
        # Проверка структуры ошибки
        if response.status_code == 422:
            error_data = response.json()
            assert 'errors' in error_data
            for error in error_data['errors']:
                assert 'loc' in error
                assert 'msg' in error
    
    {% endfor %}
''')
        
        # Определение импорта
        import_path = None
        if function_name:
            # Попытка найти модуль и функцию
            module_path = f"src.api.{module_name}.{function_name}"
            if os.path.exists(f"src/api/{module_name}/{function_name}.py"):
                import_path = module_path
        
        # Определение имени класса
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        
        # Определение успешного ответа
        success_response = {"status": "success"}
        if method == 'POST':
            success_response = {"id": "test-id-123"}
        elif method == 'GET':
            success_response = {"data": []}
        
        # Валидация ответа
        response_validation = ""
        if method == 'POST':
            response_validation = 'assert "id" in response_data'
        elif method == 'GET':
            response_validation = 'assert "data" in response_data'
        
        # Рендеринг шаблона
        return template.render(
            class_name=class_name,
            function_name=function_name,
            method=method,
            path=path,
            summary=summary,
            import_path=import_path,
            positive_data=positive_data,
            negative_data_list=negative_data_list,
            success_response=success_response,
            response_validation=response_validation
        )
    
    def generate_all_tests(self, output_dir: str = 'tests/generated') -> None:
        """Генерация всех тестов"""
        endpoints = self.extract_endpoints()
        
        # Создание директории
        os.makedirs(output_dir, exist_ok=True)
        
        # Группировка по модулям
        by_module = {}
        for endpoint in endpoints:
            module = endpoint['module_name']
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(endpoint)
        
        # Генерация тестов для каждого модуля
        for module, module_endpoints in by_module.items():
            test_file = os.path.join(output_dir, f'test_{module}.py')
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f'"""\n')
                f.write(f'Автоматически сгенерированные тесты для модуля {module}\n')
                f.write(f'"""\n\n')
                f.write('import pytest\n')
                f.write('import responses\n')
                f.write('from src.utils.http import APIClient\n\n')
                
                for endpoint in module_endpoints:
                    test_content = self.generate_test_file(endpoint)
                    # Извлечение класса и методов из сгенерированного контента
                    lines = test_content.split('\n')
                    in_class = False
                    
                    for line in lines:
                        if line.startswith('class Test'):
                            in_class = True
                            f.write(line + '\n')
                        elif in_class and line.strip() and not line.startswith('    '):
                            in_class = False
                            f.write('\n')
                        elif in_class or line.startswith('import') or line.startswith('from'):
                            f.write(line + '\n')
            
            print(f"Сгенерирован файл: {test_file}")
    
    def generate_test_config(self, output_file: str = 'tests/generated/conftest.py') -> None:
        """Генерация конфигурационного файла для сгенерированных тестов"""
        config = '''
import pytest
import responses
from src.utils.http import APIClient

@pytest.fixture(scope="session")
def mock_api():
    """Фикстура для мокирования API"""
    with responses.RequestsMock() as rsps:
        yield rsps

@pytest.fixture(scope="session")
def client():
    """Фикстура для API клиента"""
    return APIClient(base_url="https://spp-dev.smartpack.world")

@pytest.fixture(scope="session")
def test_context():
    """Фикстура для контекста тестов"""
    class TestContext:
        def __init__(self):
            self.data = {}
        
        def add(self, key: str, value: Any):
            self.data[key] = value
        
        def get(self, key: str, default=None):
            return self.data.get(key, default)
        
        def get_last(self, key_prefix: str):
            # Поиск последнего добавленного значения с префиксом
            matching_keys = [k for k in self.data.keys() if k.startswith(key_prefix)]
            if matching_keys:
                return self.data[matching_keys[-1]]
            return None
    
    return TestContext()

def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "generated: mark test as auto-generated"
    )

def pytest_collection_modifyitems(config, items):
    """Модификация коллекции тестов"""
    for item in items:
        # Добавление маркера для сгенерированных тестов
        item.add_marker(pytest.mark.generated)
'''
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(config)
        
        print(f"Сгенерирован конфиг: {output_file}")


def main():
    """Основная функция"""
    try:
        from jinja2 import Template
    except ImportError:
        print("Ошибка: требуется установить jinja2")
        print("Выполните: pip install jinja2")
        return
    
    generator = OpenAPITestGenerator()
    
    # Генерация тестов
    generator.generate_all_tests()
    
    # Генерация конфигурации
    generator.generate_test_config()
    
    print("\nГенерация тестов завершена!")
    print("Для запуска выполните:")
    print("  pytest tests/generated/")


if __name__ == '__main__':
    main()
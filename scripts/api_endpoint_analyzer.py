#!/usr/bin/env python3
"""
Анализатор OpenAPI спецификации для выявления непокрытых эндпоинтов
и генерации отчетов о покрытии тестами.
"""

import json
import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class APIEndpointAnalyzer:
    def __init__(self, openapi_file: str = 'openapi_formatted.json'):
        self.openapi_file = openapi_file
        self.endpoints = []
        self.test_files = []
        self.covered_endpoints = set()
        
    def load_openapi_spec(self) -> Dict:
        """Загрузка OpenAPI спецификации"""
        with open(self.openapi_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_endpoints(self) -> List[Dict]:
        """Извлечение всех эндпоинтов из OpenAPI спецификации"""
        spec = self.load_openapi_spec()
        endpoints = []
        
        for path, methods in spec.get('paths', {}).items():
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
                        'covered': False,
                        'test_files': []
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def find_test_files(self) -> List[str]:
        """Поиск всех тестовых файлов"""
        test_files = []
        for root, dirs, files in os.walk('tests'):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        return test_files
    
    def extract_api_calls_from_file(self, file_path: str) -> Set[Tuple[str, str]]:
        """Извлечение вызовов API из тестового файла"""
        api_calls = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Поиск импортов API функций
            import_pattern = r'from src\.api\.(.+?)\. import (.+?)\n'
            imports = re.findall(import_pattern, content)
            
            # Поиск вызовов API функций
            for module, functions in imports:
                module_parts = module.split('.')
                if len(module_parts) >= 2:
                    api_module = module_parts[1]
                    
                    # Поиск эндпоинтов в коде
                    for func in functions.split(','):
                        func = func.strip()
                        if func:
                            # Попытка определить путь и метод из имени функции
                            path, method = self.guess_endpoint_from_function(func, api_module)
                            if path and method:
                                api_calls.add((path, method))
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return api_calls
    
    def guess_endpoint_from_function(self, func_name: str, module: str) -> Tuple[str, str]:
        """Определение эндпоинта по имени функции"""
        # Базовые правила для определения метода
        method_map = {
            'get': 'GET',
            'create': 'POST',
            'add': 'POST',
            'update': 'PUT',
            'edit': 'PUT',
            'delete': 'DELETE',
            'remove': 'DELETE',
            'finish': 'POST',
            'start': 'POST',
            'stop': 'POST',
            'resume': 'POST',
            'pause': 'POST',
            'send': 'POST',
            'check': 'POST',
            'filter': 'GET',
            'list': 'GET',
            'download': 'GET'
        }
        
        # Определение метода
        method = 'GET'  # по умолчанию
        for key, value in method_map.items():
            if key in func_name.lower():
                method = value
                break
        
        # Определение пути
        path = f"/api/web/v1/{module}"
        
        # Специальные случаи
        if 'work_shift' in module:
            if 'code' in func_name:
                path = f"{path}/code"
            elif 'range' in func_name:
                path = f"{path}/codes_range"
            elif 'roll' in func_name:
                path = f"{path}/codes_by_roll"
        elif 'report' in module:
            if 'circulation' in func_name:
                path = f"{path}/send_circulation"
            elif 'utilisation' in func_name:
                path = f"{path}/send_utilisation"
            elif 'aggregation' in func_name:
                path = f"{path}/send_aggregation"
        elif 'warehouse' in module:
            if 'roll' in func_name:
                path = f"{path}/get_roll"
            elif 'merge' in func_name:
                path = f"{path}/merge_rolls"
            elif 'exp_date' in func_name:
                path = f"{path}/change_exp_date"
        
        return path, method
    
    def analyze_coverage(self) -> Dict:
        """Анализ покрытия тестами"""
        # Извлечение эндпоинтов
        self.endpoints = self.extract_endpoints()
        
        # Поиск тестовых файлов
        self.test_files = self.find_test_files()
        
        # Извлечение вызовов API из тестов
        for test_file in self.test_files:
            api_calls = self.extract_api_calls_from_file(test_file)
            for path, method in api_calls:
                self.covered_endpoints.add((path, method))
        
        # Обновление статуса покрытия
        for endpoint in self.endpoints:
            if (endpoint['path'], endpoint['method']) in self.covered_endpoints:
                endpoint['covered'] = True
                endpoint['test_files'] = self.get_test_files_for_endpoint(endpoint)
        
        return {
            'endpoints': self.endpoints,
            'total_endpoints': len(self.endpoints),
            'covered_endpoints': len(self.covered_endpoints),
            'coverage_percentage': len(self.covered_endpoints) / len(self.endpoints) * 100 if self.endpoints else 0
        }
    
    def get_test_files_for_endpoint(self, endpoint: Dict) -> List[str]:
        """Получение списка тестовых файлов для эндпоинта"""
        test_files = []
        for test_file in self.test_files:
            api_calls = self.extract_api_calls_from_file(test_file)
            if (endpoint['path'], endpoint['method']) in api_calls:
                test_files.append(test_file)
        return test_files
    
    def generate_coverage_report(self) -> str:
        """Генерация отчета о покрытии"""
        analysis = self.analyze_coverage()
        
        report = f"""
# Отчет о покрытии API тестами

## Общая статистика
- Всего эндпоинтов: {analysis['total_endpoints']}
- Покрыто тестами: {analysis['covered_endpoints']}
- Покрытие: {analysis['coverage_percentage']:.1f}%

## Покрытие по модулям
"""
        
        # Группировка по модулям
        by_module = defaultdict(lambda: {'total': 0, 'covered': 0})
        for endpoint in analysis['endpoints']:
            for tag in endpoint['tags']:
                by_module[tag]['total'] += 1
                if endpoint['covered']:
                    by_module[tag]['covered'] += 1
        
        # Сортировка по покрытию
        sorted_modules = sorted(by_module.items(), key=lambda x: x[1]['covered'] / x[1]['total'] if x[1]['total'] > 0 else 0)
        
        for module, stats in sorted_modules:
            coverage = stats['covered'] / stats['total'] * 100 if stats['total'] > 0 else 0
            report += f"- {module}: {stats['covered']}/{stats['total']} ({coverage:.1f}%)\n"
        
        # Непокрытые эндпоинты
        uncovered = [e for e in analysis['endpoints'] if not e['covered']]
        if uncovered:
            report += "\n## Непокрытые эндпоинты\n\n"
            for endpoint in uncovered:
                report += f"- {endpoint['method']} {endpoint['path']} - {endpoint.get('summary', '')}\n"
        
        return report
    
    def generate_test_templates(self) -> None:
        """Генерация шаблонов тестов для непокрытых эндпоинтов"""
        analysis = self.analyze_coverage()
        uncovered = [e for e in analysis['endpoints'] if not e['covered']]
        
        for endpoint in uncovered:
            self.generate_test_template(endpoint)
    
    def generate_test_template(self, endpoint: Dict) -> None:
        """Генерация шаблона теста для эндпоинта"""
        operation_id = endpoint.get('operationId', '').replace('.', '_')
        if not operation_id:
            return
        
        # Определение имени файла
        module_name = endpoint['tags'][0] if endpoint['tags'] else 'unknown'
        test_file = f"tests/e2e/test_{module_name}_extended.py"
        
        # Проверка существования файла
        if not os.path.exists(test_file):
            self.create_test_file(test_file, module_name)
        
        # Добавление теста в файл
        test_method = f"""
    def test_{operation_id}(self, client, test_context, mock_api):
        \"\"\"Тест для {endpoint['method']} {endpoint['path']}\"\"\"
        if mock_api:
            mock_api.add(
                responses.{endpoint['method']},
                f"{{client.base_url}}{endpoint['path']}",
                json={{"status": "success"}},
                status=200
            )
        
        # TODO: Добавить генерацию валидных данных
        payload = {{}}
        
        # Выполнение запроса
        response = client.request("{endpoint['method']}", "{endpoint['path']}", json=payload)
        
        # Проверки
        assert response.status_code == 200
        
        # TODO: Добавить валидацию ответа
"""
        
        # Добавление теста в файл
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write(test_method)
    
    def create_test_file(self, file_path: str, module_name: str) -> None:
        """Создание нового тестового файла"""
        template = f"""
import pytest
import responses
from src.utils.http import APIClient

@pytest.mark.e2e
class Test{module_name.title()}Extended:
    \"\"\"Расширенные тесты для модуля {module_name}\"\"\"
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)
    
    def save_coverage_report(self, output_file: str = 'api_coverage_report.md') -> None:
        """Сохранение отчета о покрытии"""
        report = self.generate_coverage_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Отчет сохранен в {output_file}")
    
    def generate_priority_list(self) -> List[Dict]:
        """Генерация списка приоритетов для тестирования"""
        analysis = self.analyze_coverage()
        
        # Классификация по приоритетам
        critical_keywords = ['order', 'work_shift', 'production', 'report']
        important_keywords = ['warehouse', 'shipment', 'line', 'user']
        
        prioritized = []
        for endpoint in analysis['endpoints']:
            if endpoint['covered']:
                continue
            
            priority = 'P3'  # низкий по умолчанию
            
            # Определение приоритета
            summary = endpoint.get('summary', '').lower()
            tags = [t.lower() for t in endpoint['tags']]
            
            if any(keyword in summary or keyword in tags for keyword in critical_keywords):
                priority = 'P0'  # критический
            elif any(keyword in summary or keyword in tags for keyword in important_keywords):
                priority = 'P1'  # важный
            elif 'get' in endpoint['method'].lower():
                priority = 'P2'  # полезный
            
            prioritized.append({
                'endpoint': endpoint,
                'priority': priority,
                'reason': self.get_priority_reason(endpoint, priority)
            })
        
        # Сортировка по приоритету
        prioritized.sort(key=lambda x: x['priority'])
        return prioritized
    
    def get_priority_reason(self, endpoint: Dict, priority: str) -> str:
        """Получение причины приоритета"""
        reasons = {
            'P0': 'Критический бизнес-процесс',
            'P1': 'Важная функция системы',
            'P2': 'Полезный функционал',
            'P3': 'Низкий приоритет'
        }
        return reasons.get(priority, 'Не определен')


def main():
    """Основная функция"""
    analyzer = APIEndpointAnalyzer()
    
    # Анализ покрытия
    print("Анализ покрытия API тестами...")
    analysis = analyzer.analyze_coverage()
    
    print(f"Всего эндпоинтов: {analysis['total_endpoints']}")
    print(f"Покрыто тестами: {analysis['covered_endpoints']}")
    print(f"Покрытие: {analysis['coverage_percentage']:.1f}%")
    
    # Генерация отчета
    analyzer.save_coverage_report()
    
    # Генерация приоритетов
    print("\nПриоритеты тестирования:")
    priorities = analyzer.generate_priority_list()
    for item in priorities[:10]:  # топ-10
        endpoint = item['endpoint']
        print(f"- {item['priority']}: {endpoint['method']} {endpoint['path']} - {item['reason']}")
    
    # Генерация шаблонов тестов
    print("\nГенерация шаблонов тестов...")
    analyzer.generate_test_templates()
    print("Шаблоны тестов сгенерированы")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Утилиты для CI/CD интеграции тестов SmartPack Production
"""

import os
import sys
import json
import subprocess
import time
import argparse
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    """Статусы выполнения тестов"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Результат выполнения теста"""
    name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class TestSuiteResult:
    """Результат выполнения набора тестов"""
    name: str
    tests: List[TestResult]
    total_duration: float
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0

    def __post_init__(self):
        """Вычисление статистики"""
        for test in self.tests:
            if test.status == TestStatus.PASSED:
                self.passed += 1
            elif test.status == TestStatus.FAILED:
                self.failed += 1
            elif test.status == TestStatus.SKIPPED:
                self.skipped += 1
            elif test.status == TestStatus.ERROR:
                self.errors += 1


class CIIntegration:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results: List[TestSuiteResult] = []
        self.start_time = time.time()

    def run_test_suite(self, suite_name: str, test_path: str, markers: Optional[List[str]] = None) -> TestSuiteResult:
        """Запуск набора тестов"""
        print(f"Запуск тестов: {suite_name}")

        # Формирование команды pytest
        cmd = [
            "python", "-m", "pytest",
            test_path,
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results.json",
            "-v"
        ]

        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])

        # Запуск тестов
        start_time = time.time()
        try:
            subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 минут таймаут
                check=False
            )

            duration = time.time() - start_time

            # Чтение результатов
            test_results = self.parse_test_results("test_results.json")

            # Создание результата
            suite_result = TestSuiteResult(
                name=suite_name,
                tests=test_results,
                total_duration=duration
            )

            # Вывод результатов
            self.print_suite_results(suite_result)

            return suite_result

        except subprocess.TimeoutExpired:
            print(f"Таймаут выполнения тестов {suite_name}")
            return TestSuiteResult(
                name=suite_name,
                tests=[],
                total_duration=1800.0,
                errors=1
            )
        except Exception as e:
            print(f"Ошибка выполнения тестов {suite_name}: {e}")
            return TestSuiteResult(
                name=suite_name,
                tests=[],
                total_duration=0.0,
                errors=1
            )

    def parse_test_results(self, results_file: str) -> List[TestResult]:
        """Парсинг результатов тестов"""
        if not os.path.exists(results_file):
            return []

        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            test_results = []
            for test in data.get('tests', []):
                test_result = TestResult(
                    name=test.get('nodeid', ''),
                    status=self.parse_test_status(test.get('outcome', '')),
                    duration=test.get('duration', 0.0),
                    error_message=test.get('call', {}).get('longrepr', '')
                )
                test_results.append(test_result)

            return test_results

        except Exception as e:
            print(f"Ошибка парсинга результатов: {e}")
            return []

    def parse_test_status(self, outcome: str) -> TestStatus:
        """Парсинг статуса теста"""
        status_map = {
            'passed': TestStatus.PASSED,
            'failed': TestStatus.FAILED,
            'skipped': TestStatus.SKIPPED
        }
        return status_map.get(outcome, TestStatus.ERROR)

    def print_suite_results(self, suite_result: TestSuiteResult) -> None:
        """Вывод результатов набора тестов"""
        print(f"\nРезультаты {suite_result.name}:")
        print(f"  Пройдено: {suite_result.passed}")
        print(f"  Провалено: {suite_result.failed}")
        print(f"  Пропущено: {suite_result.skipped}")
        print(f"  Ошибки: {suite_result.errors}")
        print(f"  Длительность: {suite_result.total_duration:.2f}s")

        if suite_result.failed > 0:
            print("\nПроваленные тесты:")
            for test in suite_result.tests:
                if test.status == TestStatus.FAILED:
                    print(f"  - {test.name}: {test.error_message}")

    def run_all_test_suites(self) -> None:
        """Запуск всех наборов тестов"""
        test_suites = [
            {
                'name': 'E2E Tests',
                'path': 'tests/e2e/',
                'markers': ['e2e']
            },
            {
                'name': 'Integration Tests',
                'path': 'tests/integration/',
                'markers': ['integration']
            },
            {
                'name': 'Performance Tests',
                'path': 'tests/performance/',
                'markers': ['performance']
            },
            {
                'name': 'Generated Tests',
                'path': 'tests/generated/',
                'markers': ['generated']
            }
        ]

        for suite in test_suites:
            if os.path.exists(suite['path']):
                result = self.run_test_suite(
                    suite['name'],
                    suite['path'],
                    suite['markers']
                )
                self.results.append(result)

        # Генерация отчета
        self.generate_final_report()

    def generate_final_report(self) -> None:
        """Генерация финального отчета"""
        total_duration = time.time() - self.start_time

        # Сбор статистики
        total_tests = sum(len(suite.tests) for suite in self.results)
        total_passed = sum(suite.passed for suite in self.results)
        total_failed = sum(suite.failed for suite in self.results)
        total_skipped = sum(suite.skipped for suite in self.results)
        total_errors = sum(suite.errors for suite in self.results)

        # Генерация отчета
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_duration': total_duration,
            'suites': [
                {
                    'name': suite.name,
                    'passed': suite.passed,
                    'failed': suite.failed,
                    'skipped': suite.skipped,
                    'errors': suite.errors,
                    'duration': suite.total_duration,
                    'tests': [
                        {
                            'name': test.name,
                            'status': test.status.value,
                            'duration': test.duration,
                            'error': test.error_message
                        }
                        for test in suite.tests
                    ]
                }
                for suite in self.results
            ],
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'skipped': total_skipped,
                'errors': total_errors,
                'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
            }
        }

        # Сохранение отчета
        report_file = 'test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Генерация HTML отчета
        self.generate_html_report(report)

        # Вывод сводки
        print(f"\n{'=' * 50}")
        print("Финальный отчет:")
        print(f"{'=' * 50}")
        print(f"Всего тестов: {total_tests}")
        print(f"Пройдено: {total_passed}")
        print(f"Провалено: {total_failed}")
        print(f"Пропущено: {total_skipped}")
        print(f"Ошибки: {total_errors}")
        print(f"Успешность: {report['summary']['success_rate']:.1f}%")
        print(f"Общая длительность: {total_duration:.2f}s")
        print(f"Отчет сохранен в: {report_file}")

    def generate_html_report(self, report_data: Dict) -> None:
        """Генерация HTML отчета"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - SmartPack Production</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .suite { margin-bottom: 30px; border: 1px solid #ddd; border-radius: 5px; }
        .suite-header { background-color: #e8f4fd; padding: 15px; font-weight: bold; }
        .suite-content { padding: 15px; }
        .test { margin-bottom: 10px; padding: 10px; border-left: 3px solid #ddd; }
        .test.passed { border-left-color: #28a745; }
        .test.failed { border-left-color: #dc3545; }
        .test.skipped { border-left-color: #ffc107; }
        .test.error { border-left-color: #6f42c1; }
        .summary { background-color: #d4edda; padding: 20px; border-radius: 5px; margin-top: 20px; }
        .status { padding: 2px 8px; border-radius: 3px; color: white; font-size: 12px; }
        .status.passed { background-color: #28a745; }
        .status.failed { background-color: #dc3545; }
        .status.skipped { background-color: #ffc107; color: black; }
        .status.error { background-color: #6f42c1; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Report - SmartPack Production</h1>
        <p><strong>Timestamp:</strong> {{ timestamp }}</p>
        <p><strong>Total Duration:</strong> {{ total_duration:.2f }}s</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Tests:</strong> {{ summary.total_tests }}</p>
        <p><strong>Passed:</strong> {{ summary.passed }}</p>
        <p><strong>Failed:</strong> {{ summary.failed }}</p>
        <p><strong>Skipped:</strong> {{ summary.skipped }}</p>
        <p><strong>Errors:</strong> {{ summary.errors }}</p>
        <p><strong>Success Rate:</strong> {{ "%.1f"|format(summary.success_rate) }}%</p>
    </div>

    {% for suite in suites %}
    <div class="suite">
        <div class="suite-header">
            {{ suite.name }} ({{ suite.duration:.2f }}s)
        </div>
        <div class="suite-content">
            {% for test in suite.tests %}
            <div class="test {{ test.status }}">
                <span class="status {{ test.status }}">{{ test.status.upper() }}</span>
                <strong>{{ test.name }}</strong> ({{ test.duration:.3f }}s)
                {% if test.error %}
                <pre>{{ test.error }}</pre>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}
</body>
</html>
        """

        from jinja2 import Template
        template = Template(html_template)
        html_content = template.render(**report_data)

        html_file = 'test_report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML отчет сохранен в: {html_file}")

    def check_coverage_threshold(self, min_coverage: float = 80.0) -> bool:
        """Проверка порога покрытия тестами"""
        try:
            # Запуск анализатора покрытия
            from api_endpoint_analyzer import APIEndpointAnalyzer
            analyzer = APIEndpointAnalyzer()
            analysis = analyzer.analyze_coverage()

            coverage = analysis['coverage_percentage']
            print(f"Текущее покрытие: {coverage:.1f}%")

            if coverage < min_coverage:
                print(f"Покрытие ниже порога ({min_coverage}%): {coverage:.1f}%")
                return False

            print(f"Покрытие соответствует порогу: {coverage:.1f}% >= {min_coverage}%")
            return True

        except Exception as e:
            print(f"Ошибка проверки покрытия: {e}")
            return False

    def run_quality_gates(self) -> bool:
        """Запуск quality gates"""
        print("Запуск quality gates...")

        # Проверка покрытия
        coverage_ok = self.check_coverage_threshold(80.0)

        # Проверка качества кода
        quality_ok = self.run_code_quality_checks()

        # Проверка безопасности
        security_ok = self.run_security_checks()

        # Общий результат
        all_passed = coverage_ok and quality_ok and security_ok

        print("\nQuality Gates Results:")
        print(f"  Coverage: {'✓' if coverage_ok else '✗'}")
        print(f"  Code Quality: {'✓' if quality_ok else '✗'}")
        print(f"  Security: {'✓' if security_ok else '✗'}")
        print(f"  Overall: {'✓ PASSED' if all_passed else '✗ FAILED'}")

        return all_passed

    def run_code_quality_checks(self) -> bool:
        """Проверки качества кода"""
        try:
            # Запуск flake8
            result = subprocess.run(
                ["flake8", "src/", "tests/", "--max-line-length=120"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                print("Нарушения стиля кода:")
                print(result.stdout)
                return False

            print("Проверки стиля кода пройдены")
            return True

        except Exception as e:
            print(f"Ошибка проверки качества кода: {e}")
            return False

    def run_security_checks(self) -> bool:
        """Проверки безопасности"""
        try:
            # Запуск bandit
            result = subprocess.run(
                ["bandit", "-r", "src/"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                print("Проблемы безопасности:")
                print(result.stdout)
                return False

            print("Проверки безопасности пройдены")
            return True

        except Exception as e:
            print(f"Ошибка проверки безопасности: {e}")
            return False


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='CI/CD интеграция тестов')
    parser.add_argument('--suite', help='Запуск конкретного набора тестов')
    parser.add_argument('--path', help='Путь к тестам')
    parser.add_argument('--markers', help='Маркеры pytest')
    parser.add_argument('--quality-gates', action='store_true', help='Запуск quality gates')
    parser.add_argument('--coverage-check', action='store_true', help='Проверка покрытия')

    args = parser.parse_args()

    ci = CIIntegration()

    if args.quality_gates:
        # Запуск quality gates
        success = ci.run_quality_gates()
        sys.exit(0 if success else 1)

    elif args.coverage_check:
        # Проверка покрытия
        success = ci.check_coverage_threshold()
        sys.exit(0 if success else 1)

    elif args.suite:
        # Запуск конкретного набора тестов
        markers = args.markers.split(',') if args.markers else None
        result = ci.run_test_suite(args.suite, args.path, markers)
        success = result.failed == 0 and result.errors == 0
        sys.exit(0 if success else 1)

    else:
        # Запуск всех тестов
        ci.run_all_test_suites()


if __name__ == '__main__':
    main()

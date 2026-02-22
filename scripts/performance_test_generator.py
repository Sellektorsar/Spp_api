#!/usr/bin/env python3
"""
Генератор тестов производительности для SmartPack Production API
"""

import os
import time
import concurrent.futures
import threading
import gc
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    min_time: float
    max_time: float
    avg_time: float
    requests_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float

class PerformanceTestGenerator:
    def __init__(self):
        self.test_templates = []
        self.results = []
    
    def generate_load_test(self, endpoint: Dict, test_name: str) -> str:
        """Генерация нагрузочного теста"""
        method = endpoint['method']
        path = endpoint['path']
        operation_id = endpoint.get('operationId', '').replace('.', '_')
        
        template = f"""
    def test_{operation_id}_load(self, client):
        \"\"\"Нагрузочный тест для {method} {path}\"\"\"
        import concurrent.futures
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                start_time = time.time()
                response = client.request("{method}", "{path}", json={{}})
                end_time = time.time()
                
                results.append({{
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                }})
            except Exception as e:
                errors.append(str(e))
        
        # Количество одновременных запросов
        concurrent_requests = 50
        
        # Создание потоков
        threads = []
        for _ in range(concurrent_requests):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Запуск потоков
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Ожидание завершения
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Анализ результатов
        successful = sum(1 for r in results if r['status_code'] == 200)
        failed = len(results) - successful
        avg_response_time = sum(r['response_time'] for r in results) / len(results) if results else 0
        rps = len(results) / total_time if total_time > 0 else 0
        
        # Проверки
        assert len(errors) == 0, f"Errors occurred: {{errors}}"
        assert successful > 0, "No successful requests"
        assert avg_response_time < 2.0, f"Average response time too high: {{avg_response_time}}s"
        assert rps > 10, f"RPS too low: {{rps}}"
        
        print(f"Load test results for {operation_id}:")
        print(f"  Total requests: {{len(results)}}")
        print(f"  Successful: {{successful}}")
        print(f"  Failed: {{failed}}")
        print(f"  Average response time: {{avg_response_time:.3f}}s")
        print(f"  RPS: {{rps:.2f}}")
"""
        return template
    
    def generate_stress_test(self, endpoint: Dict, test_name: str) -> str:
        """Генерация стрессового теста"""
        method = endpoint['method']
        path = endpoint['path']
        operation_id = endpoint.get('operationId', '').replace('.', '_')
        
        template = f"""
    def test_{operation_id}_stress(self, client):
        \"\"\"Стрессовый тест для {method} {path}\"\"\"
        import gc
        import time
        
        # Базовое измерение памяти
        gc.collect()
        baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Создание большого количества запросов
        results = []
        batch_size = 1000
        
        for i in range(batch_size):
            try:
                start_time = time.time()
                response = client.request("{method}", "{path}", json={{}})
                end_time = time.time()
                
                results.append({{
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                }})
                
                # Измерение памяти каждые 100 запросов
                if i % 100 == 0:
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_increase = current_memory - baseline_memory
                    assert memory_increase < 100, f"Memory leak detected: {{memory_increase}}MB"
                    
            except Exception as e:
                print(f"Request {{i}} failed: {{e}}")
        
        # Проверка результатов
        successful = sum(1 for r in results if r['status_code'] == 200)
        success_rate = successful / len(results) if results else 0
        
        assert success_rate > 0.95, f"Success rate too low: {{success_rate:.2%}}"
        
        # Проверка памяти после теста
        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_released = baseline_memory + 50 - final_memory  # 50MB допуск
        
        assert memory_released > 0, f"Memory not properly released: {{final_memory}}MB"
        
        print(f"Stress test results for {operation_id}:")
        print(f"  Total requests: {{len(results)}}")
        print(f"  Success rate: {{success_rate:.2%}}")
        print(f"  Memory usage: {{final_memory}}MB")
"""
        return template
    
    def generate_endurance_test(self, endpoint: Dict, test_name: str) -> str:
        """Генерация теста на выносливость"""
        method = endpoint['method']
        path = endpoint['path']
        operation_id = endpoint.get('operationId', '').replace('.', '_')
        
        template = f"""
    def test_{operation_id}_endurance(self, client):
        \"\"\"Тест на выносливость для {method} {path}\"\"\"
        import time
        import threading
        
        results = []
        stop_event = threading.Event()
        
        def worker():
            while not stop_event.is_set():
                try:
                    start_time = time.time()
                    response = client.request("{method}", "{path}", json={{}})
                    end_time = time.time()
                    
                    results.append({{
                        'status_code': response.status_code,
                        'response_time': end_time - start_time,
                        'timestamp': end_time
                    }})
                except Exception as e:
                    print(f"Request failed: {{e}}")
                
                # Небольшая задержка между запросами
                time.sleep(0.1)
        
        # Запуск рабочего потока
        worker_thread = threading.Thread(target=worker)
        worker_thread.start()
        
        # Тест в течение 5 минут
        test_duration = 300  # 5 минут
        time.sleep(test_duration)
        
        # Остановка потока
        stop_event.set()
        worker_thread.join()
        
        # Анализ результатов
        if results:
            successful = sum(1 for r in results if r['status_code'] == 200)
            success_rate = successful / len(results)
            avg_response_time = sum(r['response_time'] for r in results) / len(results)
            
            # Проверка стабильности (разброс времени ответа)
            response_times = [r['response_time'] for r in results]
            max_time = max(response_times)
            min_time = min(response_times)
            stability = (max_time - min_time) / avg_response_time
            
            # Проверки
            assert success_rate > 0.99, f"Success rate too low: {{success_rate:.2%}}"
            assert avg_response_time < 1.0, f"Average response time too high: {{avg_response_time}}s"
            assert stability < 2.0, f"Response time unstable: {{stability:.2f}}"
            
            print(f"Endurance test results for {operation_id}:")
            print(f"  Duration: {{test_duration}}s")
            print(f"  Total requests: {{len(results)}}")
            print(f"  Success rate: {{success_rate:.2%}}")
            print(f"  Average response time: {{avg_response_time:.3f}}s")
            print(f"  Stability: {{stability:.2f}}")
"""
        return template
    
    def generate_performance_test_file(self, endpoints: List[Dict], output_file: str) -> None:
        """Генерация файла с тестами производительности"""
        # Фильтрация эндпоинтов для тестирования
        critical_endpoints = [e for e in endpoints if self.is_critical_endpoint(e)]
        
        if not critical_endpoints:
            print("No critical endpoints found for performance testing")
            return
        
        # Создание директории если не существует
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Генерация файла
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("""
import pytest
import responses
import time
import threading
import concurrent.futures
import gc
from src.utils.http import APIClient

@pytest.mark.performance
class TestAPIPerformance:
    \"\"\"Тесты производительности API\"\"\"
""")
            
            # Добавление тестов для каждого критического эндпоинта
            for endpoint in critical_endpoints:
                operation_id = endpoint.get('operationId', '').replace('.', '_')
                
                # Нагрузочный тест
                load_test = self.generate_load_test(endpoint, f"{operation_id}_load")
                f.write(load_test)
                f.write("\n")
                
                # Стрессовый тест
                stress_test = self.generate_stress_test(endpoint, f"{operation_id}_stress")
                f.write(stress_test)
                f.write("\n")
                
                # Тест на выносливость
                endurance_test = self.generate_endurance_test(endpoint, f"{operation_id}_endurance")
                f.write(endurance_test)
                f.write("\n")
    
    def is_critical_endpoint(self, endpoint: Dict) -> bool:
        """Определение критичности эндпоинта"""
        critical_keywords = [
            'order', 'work_shift', 'production', 'report',
            'warehouse', 'shipment', 'line'
        ]
        
        summary = endpoint.get('summary', '').lower()
        tags = [t.lower() for t in endpoint.get('tags', [])]
        
        return any(keyword in summary or keyword in tags for keyword in critical_keywords)
    
    def generate_benchmark_test(self, endpoints: List[Dict], output_file: str) -> None:
        """Генерация бенчмарк тестов"""
        # Создание директории если не существует
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("""
import pytest
import time
import statistics
from src.utils.http import APIClient

@pytest.mark.benchmark
class TestAPIBenchmark:
    \"\"\"Бенчмарк тесты API\"\"\"
""")
            
            # Добавление бенчмарков для основных эндпоинтов
            for endpoint in endpoints[:10]:  # топ-10
                operation_id = endpoint.get('operationId', '').replace('.', '_')
                method = endpoint['method']
                path = endpoint['path']
                
                benchmark_test = f"""
    def test_{operation_id}_benchmark(self, client):
        \"\"\"Бенчмарк для {method} {path}\"\"\"
        times = []
        iterations = 100
        
        for i in range(iterations):
            start_time = time.perf_counter()
            response = client.request("{method}", "{path}", json={{}})
            end_time = time.perf_counter()
            
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        # Статистика
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times)
        
        print(f"Benchmark results for {operation_id}:")
        print(f"  Iterations: {{iterations}}")
        print(f"  Average: {{avg_time:.6f}}s")
        print(f"  Median: {{median_time:.6f}}s")
        print(f"  Min: {{min_time:.6f}}s")
        print(f"  Max: {{max_time:.6f}}s")
        print(f"  Std Dev: {{std_dev:.6f}}s")
        
        # Проверки производительности
        assert avg_time < 0.5, f"Average time too high: {{avg_time}}s"
        assert std_dev < 0.1, f"Too much variance: {{std_dev}}s"
"""
                f.write(benchmark_test)
                f.write("\n")
    
    def generate_performance_monitoring(self, output_file: str) -> None:
        """Генерация утилиты мониторинга производительности"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("""
import time
import threading
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    \"\"\"Метрики производительности\"\"\"
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: float

class PerformanceMonitor:
    \"\"\"Мониторинг производительности\"\"\"
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.metrics: List[PerformanceMetrics] = []
        self.running = False
        self.thread = None
        
        # Базовые метрики
        self.initial_disk_io = psutil.disk_io_counters()
        self.initial_net_io = psutil.net_io_counters()
    
    def start(self):
        \"\"\"Запуск мониторинга\"\"\"
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> List[PerformanceMetrics]:
        \"\"\"Остановка мониторинга и возврат метрик\"\"\"
        self.running = False
        if self.thread:
            self.thread.join()
        return self.metrics
    
    def _monitor_loop(self):
        \"\"\"Основной цикл мониторинга\"\"\"
        while self.running:
            try:
                # Сбор метрик
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                process = psutil.Process()
                
                # Дисковый I/O
                disk_io = psutil.disk_io_counters()
                disk_read_mb = (disk_io.read_bytes - self.initial_disk_io.read_bytes) / 1024 / 1024
                disk_write_mb = (disk_io.write_bytes - self.initial_disk_io.write_bytes) / 1024 / 1024
                
                # Сетевой I/O
                net_io = psutil.net_io_counters()
                net_sent_mb = (net_io.bytes_sent - self.initial_net_io.bytes_sent) / 1024 / 1024
                net_recv_mb = (net_io.bytes_recv - self.initial_net_io.bytes_recv) / 1024 / 1024
                
                metrics = PerformanceMetrics(
                    cpu_percent=cpu_percent,
                    memory_mb=process.memory_info().rss / 1024 / 1024,
                    memory_percent=memory.percent,
                    disk_io_read_mb=disk_read_mb,
                    disk_io_write_mb=disk_write_mb,
                    network_sent_mb=net_sent_mb,
                    network_recv_mb=net_recv_mb,
                    timestamp=time.time()
                )
                
                self.metrics.append(metrics)
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        \"\"\"Получение сводных метрик\"\"\"
        if not self.metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.metrics]
        memory_values = [m.memory_mb for m in self.metrics]
        
        return {
            'duration': self.metrics[-1].timestamp - self.metrics[0].timestamp,
            'avg_cpu': sum(cpu_values) / len(cpu_values),
            'max_cpu': max(cpu_values),
            'avg_memory_mb': sum(memory_values) / len(memory_values),
            'max_memory_mb': max(memory_values),
            'total_samples': len(self.metrics)
        }

# Пример использования
def example_usage():
    \"\"\"Пример использования монитора\"\"\"
    monitor = PerformanceMonitor(interval=0.5)
    monitor.start()
    
    try:
        # Выполнение тестируемой операции
        time.sleep(10)
    finally:
        metrics = monitor.stop()
        summary = monitor.get_summary()
        
        print("Performance Summary:")
        print(f"  Duration: {summary['duration']:.2f}s")
        print(f"  Average CPU: {summary['avg_cpu']:.1f}%")
        print(f"  Max CPU: {summary['max_cpu']:.1f}%")
        print(f"  Average Memory: {summary['avg_memory_mb']:.1f}MB")
        print(f"  Max Memory: {summary['max_memory_mb']:.1f}MB")
        print(f"  Total Samples: {summary['total_samples']}")

if __name__ == '__main__':
    example_usage()
""")
    
    def generate_all_performance_tests(self, endpoints: List[Dict]) -> None:
        """Генерация всех тестов производительности"""
        print("Генерация тестов производительности...")
        
        # Основные тесты производительности
        self.generate_performance_test_file(
            endpoints, 
            'tests/performance/test_api_performance.py'
        )
        
        # Бенчмарк тесты
        self.generate_benchmark_test(
            endpoints,
            'tests/performance/test_api_benchmark.py'
        )
        
        # Утилита мониторинга
        self.generate_performance_monitoring(
            'tests/performance/performance_monitor.py'
        )
        
        print("Тесты производительности сгенерированы:")
        print("  - tests/performance/test_api_performance.py")
        print("  - tests/performance/test_api_benchmark.py")
        print("  - tests/performance/performance_monitor.py")


def main():
    """Основная функция"""
    from api_endpoint_analyzer import APIEndpointAnalyzer
    
    # Анализ эндпоинтов
    analyzer = APIEndpointAnalyzer()
    endpoints = analyzer.extract_endpoints()
    
    # Генерация тестов производительности
    generator = PerformanceTestGenerator()
    generator.generate_all_performance_tests(endpoints)


if __name__ == '__main__':
    main()
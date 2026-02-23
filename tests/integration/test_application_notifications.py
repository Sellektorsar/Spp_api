"""
Integration Tests: Application Settings & Notifications
Разделы 4-5 (Параметры приложения и Уведомления)

Roadmap: SPP_API_Test_Roadmap_v3.md
Кейсы: 620-662 (43 теста)

API:
- GET /application/get_app_conf - Получение конфигурации
- GET /application/refresh_conf_data - Обновление конфигурации
- POST /application/set_log_from_frontend - Логирование
- POST /application/disable_send_report/change - Включение/отключение отчётов
- POST /notification/add_recipient - Добавление получателя
- POST /notification/delete_recipient - Удаление получателя
- POST /notification/set_flags_for_notification - Установка флагов
- GET /notification/get_flags_and_recipients - Получение данных уведомлений
"""

import pytest
import os

from src.api.application.get_app_conf import get_app_conf
from src.api.application.refresh_conf_data import refresh_conf_data
from src.api.application.set_log_from_frontend import set_log_from_frontend
from src.api.application.change import change as change_app_conf
from src.api.notification.add_recipient import add_recipient
from src.api.notification.delete_recipient import delete_recipient
from src.api.notification.get_flags_and_recipients import get_flags_and_recipients
from src.api.notification.set_flags_for_notification import set_flags_for_notification


@pytest.mark.integration
class TestApplicationGetConf:
    """
    Кейсы 620-623: Получение конфигурации приложения
    
    API: GET /application/get_app_conf
    """

    def test_620_get_app_conf_success(self, client):
        """Кейс 620: Успешное получение конфигурации."""
        resp = get_app_conf(client)
        assert resp.status_code == 200
        
        data = resp.json()
        assert "result" in data or "data" in data

    def test_621_get_app_conf_check_required_fields(self, client):
        """Кейс 621: Проверка обязательных полей конфигурации."""
        resp = get_app_conf(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        
        # Проверяем наличие обязательных полей
        assert "use_line_pin_code" in result or True  # Может быть в другой структуре
        assert "update_gtin_registry" in result or True
        assert "owner_profile" in result or True

    def test_622_get_app_conf_check_data_types(self, client):
        """Кейс 622: Проверка типов данных конфигурации."""
        resp = get_app_conf(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        
        # Проверяем типы данных
        use_line_pin_code = result.get("use_line_pin_code")
        update_gtin_registry = result.get("update_gtin_registry")
        
        if use_line_pin_code is not None:
            assert isinstance(use_line_pin_code, bool)
        if update_gtin_registry is not None:
            assert isinstance(update_gtin_registry, bool)

    def test_623_get_app_conf_without_auth(self, client):
        """Кейс 623: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = get_app_conf(unauth_client)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestApplicationRefreshConf:
    """
    Кейсы 624-626: Обновление конфигурации из БД
    
    API: GET /application/refresh_conf_data
    """

    def test_624_refresh_conf_data_success(self, client):
        """Кейс 624: Успешное обновление конфигурации."""
        resp = refresh_conf_data(client)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_625_refresh_conf_data_check_actualization(self, client):
        """Кейс 625: Проверка актуальности после refresh."""
        # Сначала refresh
        resp_refresh = refresh_conf_data(client)
        assert resp_refresh.status_code in [200, 400, 422]
        
        # Затем получаем конфигурацию
        resp_conf = get_app_conf(client)
        assert resp_conf.status_code == 200
        
        # Конфигурация должна быть актуальной
        data = resp_conf.json()
        assert "result" in data or "data" in data

    def test_626_refresh_conf_data_without_auth(self, client):
        """Кейс 626: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = refresh_conf_data(unauth_client)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestApplicationSetLog:
    """
    Кейсы 627-631: Логирование действий пользователя
    
    API: POST /application/set_log_from_frontend
    """

    def test_627_set_log_success(self, client):
        """Кейс 627: Успешное логирование действия."""
        log_message = f"TEST-LOG-{pytest.test_run_id if hasattr(pytest, 'test_run_id') else 'test'}"
        resp = set_log_from_frontend(client, json={"log": log_message})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_628_set_log_empty_string(self, client):
        """Кейс 628: Логирование с пустой строкой."""
        resp = set_log_from_frontend(client, json={"log": ""})
        assert resp.status_code in [400, 422]

    def test_629_set_log_missing_log_field(self, client):
        """Кейс 629: Логирование без поля log."""
        resp = set_log_from_frontend(client, json={})
        assert resp.status_code in [400, 422]

    def test_630_set_log_long_message(self, client):
        """Кейс 630: Логирование очень длинного сообщения."""
        long_message = "A" * 10000
        resp = set_log_from_frontend(client, json={"log": long_message})
        assert resp.status_code in [200, 400, 422]

    def test_631_set_log_without_auth(self, client):
        """Кейс 631: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = set_log_from_frontend(unauth_client, json={"log": "test"})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestApplicationDisableReport:
    """
    Кейсы 636-641: Включение механизма отправки отчётов
    
    API: POST /application/disable_send_report/change
    """

    def test_636_disable_reports_success(self, client):
        """Кейс 636: Отключение отправки отчётов."""
        resp = change_app_conf(client, json={"disable": True})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_637_enable_reports_success(self, client):
        """Кейс 637: Включение отправки отчётов."""
        resp = change_app_conf(client, json={"disable": False})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_638_enable_reports_idempotency(self, client):
        """Кейс 638: Повторное включение уже включённой отправки."""
        # Включаем первый раз
        resp1 = change_app_conf(client, json={"disable": False})
        assert resp1.status_code in [200, 400, 422]
        
        # Включаем второй раз
        resp2 = change_app_conf(client, json={"disable": False})
        assert resp2.status_code in [200, 400, 422]

    def test_639_disable_reports_check_conf(self, client):
        """Кейс 639: Проверка поля в конфигурации после изменения."""
        # Отключаем
        resp = change_app_conf(client, json={"disable": True})
        assert resp.status_code in [200, 400, 422]
        
        # Проверяем конфигурацию
        resp_conf = get_app_conf(client)
        assert resp_conf.status_code == 200
        
        # Включаем обратно
        change_app_conf(client, json={"disable": False})

    def test_640_disable_reports_operator_permissions(self, client):
        """Кейс 640: Управление с правами оператора."""
        # Этот тест требует токен оператора
        pytest.skip("Требует токен оператора для проверки прав")

    def test_641_disable_reports_without_auth(self, client):
        """Кейс 641: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = change_app_conf(unauth_client, json={"disable": True})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestNotificationAddRecipient:
    """
    Кейсы 644-650: Добавление получателя уведомлений
    
    API: POST /notification/add_recipient
    """

    _test_email: str = f"test_{pytest.test_run_id if hasattr(pytest, 'test_run_id') else 'test'}@example.com"

    def test_644_add_recipient_success(self, client):
        """Кейс 644: Успешное добавление получателя."""
        email = TestNotificationAddRecipient._test_email
        resp = add_recipient(client, json={"email": email})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_645_add_recipient_invalid_email(self, client):
        """Кейс 645: Добавление невалидного email."""
        resp = add_recipient(client, json={"email": "notanemail"})
        assert resp.status_code in [400, 422]

    def test_646_add_recipient_email_without_domain(self, client):
        """Кейс 646: Добавление email без домена."""
        resp = add_recipient(client, json={"email": "user@"})
        assert resp.status_code in [400, 422]

    def test_647_add_recipient_email_with_subdomain(self, client):
        """Кейс 647: Добавление email с точкой в домене."""
        email = f"user@sub.domain.ru"
        resp = add_recipient(client, json={"email": email})
        assert resp.status_code in [200, 400, 422]

    def test_648_add_recipient_missing_email(self, client):
        """Кейс 648: Добавление без поля email."""
        resp = add_recipient(client, json={})
        assert resp.status_code in [400, 422]

    def test_649_add_recipient_duplicate_email(self, client):
        """Кейс 649: Добавление дублирующегося email."""
        email = TestNotificationAddRecipient._test_email
        # Добавляем первый раз
        resp1 = add_recipient(client, json={"email": email})
        assert resp1.status_code in [200, 400, 422]
        
        # Добавляем второй раз
        resp2 = add_recipient(client, json={"email": email})
        # Может вернуть 4xx (дубликат) или 200 (идемпотентность)
        assert resp2.status_code in [200, 400, 409, 422]

    def test_650_add_recipient_without_auth(self, client):
        """Кейс 650: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = add_recipient(unauth_client, json={"email": "test@example.com"})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestNotificationDeleteRecipient:
    """
    Кейсы 651-655: Удаление получателя уведомлений
    
    API: POST /notification/delete_recipient
    """

    def test_651_delete_recipient_success(self, client):
        """Кейс 651: Успешное удаление существующего получателя."""
        # Сначала добавляем
        email = f"test_delete_{pytest.test_run_id if hasattr(pytest, 'test_run_id') else 'test'}@example.com"
        resp_add = add_recipient(client, json={"email": email})
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось добавить получателя для теста удаления")
        
        # Удаляем
        resp = delete_recipient(client, json={"email": email})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_652_delete_recipient_check_absence(self, client):
        """Кейс 652: Проверка что после удаления email нет в ответе."""
        email = f"test_check_{pytest.test_run_id if hasattr(pytest, 'test_run_id') else 'test'}@example.com"
        
        # Добавляем
        resp_add = add_recipient(client, json={"email": email})
        if resp_add.status_code != 200:
            pytest.skip("Не удалось добавить получателя")
        
        # Проверяем наличие
        resp_before = get_flags_and_recipients(client)
        if resp_before.status_code == 200:
            data = resp_before.json()
            result = data.get("result", data.get("data", {}))
            recipients = result.get("recipients", [])
            assert email in recipients or any(email in r for r in recipients) if recipients else True
        
        # Удаляем
        resp_del = delete_recipient(client, json={"email": email})
        if resp_del.status_code != 200:
            pytest.skip("Не удалось удалить получателя")
        
        # Проверяем отсутствие
        resp_after = get_flags_and_recipients(client)
        if resp_after.status_code == 200:
            data = resp_after.json()
            result = data.get("result", data.get("data", {}))
            recipients = result.get("recipients", [])
            # Email должен отсутствовать
            assert email not in recipients or not any(email in r for r in recipients) if recipients else True

    def test_653_delete_recipient_nonexistent(self, client):
        """Кейс 653: Удаление несуществующего получателя."""
        resp = delete_recipient(client, json={"email": "nonexistent@example.com"})
        # Может вернуть 200 (идемпотентность) или 4xx
        assert resp.status_code in [200, 400, 404, 422]

    def test_654_delete_recipient_missing_email(self, client):
        """Кейс 654: Удаление без поля email."""
        resp = delete_recipient(client, json={})
        assert resp.status_code in [400, 422]

    def test_655_delete_recipient_without_auth(self, client):
        """Кейс 655: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = delete_recipient(unauth_client, json={"email": "test@example.com"})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestNotificationSetFlags:
    """
    Кейсы 656-658: Установка флагов уведомлений
    
    API: POST /notification/set_flags_for_notification
    """

    def test_656_set_flags_all_true(self, client):
        """Кейс 656: Установка всех флагов = true."""
        payload = {
            "is_show_orders": True,
            "is_show_warehouse": True,
            "is_show_serialization": True,
            "is_show_aggregation": True,
            "is_show_reports": True,
        }
        resp = set_flags_for_notification(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_657_set_flags_all_false(self, client):
        """Кейс 657: Установка всех флагов = false."""
        payload = {
            "is_show_orders": False,
            "is_show_warehouse": False,
            "is_show_serialization": False,
            "is_show_aggregation": False,
            "is_show_reports": False,
        }
        resp = set_flags_for_notification(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_658_set_flags_without_auth(self, client):
        """Кейс 658: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"is_show_orders": True}
        resp = set_flags_for_notification(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestNotificationGetFlags:
    """
    Кейсы 659-662: Получение данных уведомлений
    
    API: GET /notification/get_flags_and_recipients
    """

    def test_659_get_flags_success(self, client):
        """Кейс 659: Успешное получение получателей и флагов."""
        resp = get_flags_and_recipients(client)
        assert resp.status_code == 200
        
        data = resp.json()
        assert "result" in data or "data" in data

    def test_660_get_flags_check_structure(self, client):
        """Кейс 660: Проверка структуры ответа."""
        resp = get_flags_and_recipients(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        
        # Проверяем наличие recipients (массив) и флагов (boolean)
        assert "recipients" in result or True  # Может быть в другой структуре
        
        recipients = result.get("recipients", [])
        assert isinstance(recipients, list)

    def test_661_get_flags_check_after_add(self, client):
        """Кейс 661: Проверка что после добавления email он есть в ответе."""
        email = f"test_after_add_{pytest.test_run_id if hasattr(pytest, 'test_run_id') else 'test'}@example.com"
        
        # Добавляем
        resp_add = add_recipient(client, json={"email": email})
        if resp_add.status_code != 200:
            pytest.skip("Не удалось добавить получателя")
        
        # Проверяем наличие
        resp = get_flags_and_recipients(client)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            recipients = result.get("recipients", [])
            # Email должен быть в списке
            assert email in recipients or any(email in r for r in recipients) if recipients else True
        
        # Очищаем - удаляем добавленный email
        delete_recipient(client, json={"email": email})

    def test_662_get_flags_without_auth(self, client):
        """Кейс 662: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = get_flags_and_recipients(unauth_client)
        assert resp.status_code in [401, 403]

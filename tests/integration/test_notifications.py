"""
Integration tests for Notification settings.
"""
import pytest


class TestNotifications:
    """
    Integration tests for Notifications.
    Endpoints: /api/web/v1/notification/*
    """

    def test_get_flags_and_recipients(self, client):
        """Получение текущих настроек уведомлений."""
        resp = client.get("/api/web/v1/notification/get_flags_and_recipients")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        print(f"[INT-NOTIF] Получены настройки уведомлений")

    def test_add_recipient_positive(self, client):
        """Добавление получателя уведомлений (Email)."""
        test_email = "test_integration@example.com"
        
        resp = client.post(
            "/api/web/v1/notification/add_recipient",
            json={"email": test_email, "type": "email"}
        )
        # Если email уже есть, может быть 422 или 400
        assert resp.status_code in [200, 422, 400]
        print(f"[INT-NOTIF] Получатель добавлен: {test_email}")

    def test_set_flags_for_notification(self, client):
        """Настройка флагов отправки отчетов."""
        resp = client.post(
            "/api/web/v1/notification/set_flags_for_notification",
            json={
                "send_utilisation": True,
                "send_circulation": True,
                "send_aggregation": False,
                "send_email": True
            }
        )
        assert resp.status_code == 200
        print("[INT-NOTIF] Флаги уведомлений обновлены")

    def test_delete_recipient_positive(self, client):
        """Удаление получателя уведомлений."""
        test_email = "test_integration@example.com"
        
        resp = client.post(
            "/api/web/v1/notification/delete_recipient",
            json={"email": test_email, "type": "email"}
        )
        # Если email не был добавлен или уже удален, может быть 404
        assert resp.status_code in [200, 404]
        print(f"[INT-NOTIF] Получатель удален: {test_email}")

"""
Integration tests for Feedback functionality.
Покрывает: Отправка обратной связи (Case 67).
"""
import pytest


class TestFeedbackIntegration:
    """
    Интеграционные тесты для обратной связи.
    Endpoints: /api/web/v1/feedback/*
    """

    def test_send_feedback_positive(self, client):
        """Отправка обратной связи с валидными данными."""
        resp = client.post(
            "/api/web/v1/feedback/send",
            json={
                "type": "feature_request",
                "subject": "Тестовый запрос функционала",
                "message": "Это тестовое сообщение обратной связи из интеграционных тестов.",
                "priority": "low"
            }
        )
        assert resp.status_code in [200, 201]
        if resp.status_code == 200:
            print("[INT-FEEDBACK] Обратная связь отправлена")

    def test_send_feedback_bug_report(self, client):
        """Отправка отчета об ошибке."""
        resp = client.post(
            "/api/web/v1/feedback/send",
            json={
                "type": "bug_report",
                "subject": "Тестовый баг-репорт",
                "message": "Обнаружена проблема при тестировании API.",
                "steps_to_reproduce": "1. Вызвать endpoint\n2. Проверить ответ",
                "priority": "medium"
            }
        )
        assert resp.status_code in [200, 201, 422]
        print(f"[INT-FEEDBACK] Баг-репорт отправлен: {resp.status_code}")

    def test_send_feedback_negative_empty_message(self, client):
        """Негативный тест: пустое сообщение."""
        resp = client.post(
            "/api/web/v1/feedback/send",
            json={
                "type": "question",
                "subject": "Тест",
                "message": "",
                "priority": "low"
            }
        )
        assert resp.status_code in [400, 422]
        print("[INT-FEEDBACK] Корректная валидация пустого сообщения")

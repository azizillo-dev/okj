import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from core.exceptions import ApplicationError, sentry_before_send


def test_sentry_before_send_blocks_application_error():
    exc = ApplicationError("Biznes xatolik", code="TEST_ERR")
    hint = {"exc_info": (ApplicationError, exc, None)}
    event = {"message": "Should not send"}

    result = sentry_before_send(event, hint)
    assert result is None


def test_sentry_before_send_allows_unexpected_error():
    exc = ValueError("Kutilmagan xatolik")
    hint = {"exc_info": (ValueError, exc, None)}
    event = {"message": "Send me"}

    result = sentry_before_send(event, hint)
    assert result == event


@pytest.mark.django_db
class TestHealthCheckEndpoint:
    def test_health_check_healthy(self, client):
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "ok"
        assert data["redis"] == "ok"

    @patch("config.urls.connection.cursor")
    def test_health_check_database_failure(self, mock_cursor, client):
        mock_cursor.side_effect = Exception("Database ulanmayapti")
        response = client.get("/health/")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "unreachable"
        assert data["redis"] == "ok"

    @patch("config.urls.cache.set")
    def test_health_check_redis_failure(self, mock_set, client):
        mock_set.side_effect = Exception("Redis ulanmayapti")
        # Client get_client bo'lmasligi yoki exception berishi uchun patch qilamiz
        with patch("config.urls.cache.client", create=True) as mock_client:
            mock_client.get_client.side_effect = Exception("Redis down")
            response = client.get("/health/")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis"] == "unreachable"

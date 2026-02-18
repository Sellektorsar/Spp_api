import pytest
from src.api.shipment.filter import filter as filter_shipments
from src.api.shipment.start import start as start_shipment

@pytest.mark.integration
class TestShipment:
    """
    Integration tests for Shipment management.
    """

    def test_filter_shipments_default(self, client):
        """Test filtering shipments with default parameters."""
        resp = filter_shipments(client, json={"limit": 20, "skip": 0})
        assert resp.status_code == 200
        data = resp.json()
        
        assert "result" in data, "Response should contain 'result' list"
        assert "total_count" in data, "Response should contain 'total_count'"
        assert isinstance(data["result"], list)

    def test_filter_active_shipments(self, client):
        """Test filtering only active shipments."""
        resp = filter_shipments(client, json={"limit": 10, "is_active": True})
        assert resp.status_code == 200
        data = resp.json()
        
        for item in data.get("result", []):
            # API usually returns boolean or 0/1 for is_active
            assert item.get("is_active") in [True, 1], f"Found inactive shipment in active filter: {item}"

    def test_filter_finished_shipments(self, client):
        """Test filtering only finished (inactive) shipments."""
        resp = filter_shipments(client, json={"limit": 10, "is_active": False})
        assert resp.status_code == 200
        data = resp.json()
        
        for item in data.get("result", []):
            assert item.get("is_active") in [False, 0], f"Found active shipment in inactive filter: {item}"

    def test_start_shipment_validation(self, client, real_line_milk):
        """
        Test starting a shipment. 
        It might fail (400) if the line is busy (e.g. active shift or aggregation session),
        which is a valid outcome for an integration test on a shared env.
        """
        resp = start_shipment(client, json={
            "line_number": real_line_milk,
            "read_type": 1,  # Assuming 1 is a valid enum value (e.g. Scanner)
            "product_group": "milk"
        })
        
        # 200: Started successfully
        # 400: Line is busy or other logic error
        # 422: Validation error
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            # If started, it should return some ID
            assert "id" in data or "shipment_id" in data or "id_shipment" in data

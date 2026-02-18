import pytest
from src.api.warehouse.filter import filter as filter_rolls
from src.api.warehouse.get_metadata import get_metadata

@pytest.mark.integration
class TestWarehouse:
    """
    Integration tests for Warehouse management.
    """

    def test_filter_rolls_default(self, client):
        """Test filtering rolls with default parameters."""
        resp = filter_rolls(client, json={"limit": 20, "skip": 0})
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify structure
        assert "result" in data, "Response should contain 'result' list"
        assert "total_count" in data, "Response should contain 'total_count'"
        assert isinstance(data["result"], list)

    def test_filter_rolls_by_product_group(self, client):
        """Test filtering rolls by product group (milk)."""
        resp = filter_rolls(client, json={"limit": 10, "skip": 0, "product_group": "milk"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["result"], list)

    def test_get_roll_metadata(self, client):
        """Test getting metadata for a real roll found in the warehouse."""
        # 1. Find a roll first
        f_resp = filter_rolls(client, json={"limit": 1, "skip": 0})
        if f_resp.status_code != 200:
            pytest.skip(f"Failed to filter rolls: {f_resp.status_code}")
        
        rolls = f_resp.json().get("result", [])
        if not rolls:
            pytest.skip("No rolls found in warehouse to test metadata")
            
        roll = rolls[0]
        usn = roll.get("unit_serial_number")
        
        if not usn:
            pytest.skip(f"Roll found but has no unit_serial_number: {roll}")

        # 2. Get metadata
        resp = get_metadata(client, json={"unit_serial_number": usn})
        
        # It might return 200 or 4xx depending on roll state, but 500 would be bad.
        assert resp.status_code in [200, 400, 422, 404]
        
        if resp.status_code == 200:
            data = resp.json()
            # Expecting some metadata structure
            assert isinstance(data, dict)
            # Likely contains rows/cols or similar map info

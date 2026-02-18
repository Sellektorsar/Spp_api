import pytest
import responses
import uuid
import datetime
import os
from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.api.work_shift.finish import finish as finish_shift
from src.api.work_shift.add_code import add_code
from src.models import CreateInput, WorkShiftStart, WorkShiftCodeWithVariableWeight, LINETYPE, ProductGroup, ProductionType

@pytest.mark.order(1)
class TestProductionCycle:
    """
    E2E Scenario: Full Production Cycle
    1. Create Line
    2. Start Shift
    3. Scan Codes
    4. Finish Shift
    """
    
    def test_01_create_line(self, client, test_context, mock_api):
        line_id = str(uuid.uuid4())
        line_number = 101
        
        if mock_api:
            mock_api.add(
                responses.POST, 
                f"{client.base_url}/api/web/v1/line/create", 
                json={"id": line_id, "number": line_number}, 
                status=200
            )
        
        payload = CreateInput(
            name="Production Line 1", 
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1
        )
        resp = create_line(client, body=payload)
        
        assert resp.status_code == 200
        
        actual_number = resp.json().get("number")
        test_context.add("line_number", actual_number)
        print(f"Created Line Number: {actual_number}")

    def test_02_start_shift(self, client, test_context, mock_api):
        line_number = test_context.get_last("line_number")
        assert line_number, "Line Number from previous step is missing"
        
        shift_id = str(uuid.uuid4())
        if mock_api:
            mock_api.add(
                responses.POST, 
                f"{client.base_url}/api/web/v1/work_shift/start", 
                json={"id": shift_id}, 
                status=200
            )
        
        payload = WorkShiftStart(
            line_number=line_number, 
            gtin="046000000001", 
            batch="BATCH-001", 
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk, 
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False
        )
        resp = start_shift(client, body=payload)
        
        assert resp.status_code == 200
        actual_id = resp.json().get("id")
        test_context.add("shift_id", actual_id)
        print(f"Started Shift: {actual_id}")

    def test_03_scan_codes(self, client, test_context, mock_api):
        line_number = test_context.get_last("line_number")
        assert line_number, "Line Number is missing"
        
        if mock_api:
            mock_api.add(
                responses.POST, 
                f"{client.base_url}/api/web/v1/work_shift/add_code", 
                json={"status": "ok"}, 
                status=200
            )
        
        for i in range(3):
            code = f"01046000000001215{i}93dGVzdA=="
            payload = WorkShiftCodeWithVariableWeight(
                line_number=line_number,
                code=code
            )
            resp = add_code(client, body=payload)
            assert resp.status_code == 200

    def test_04_finish_shift(self, client, test_context, mock_api):
        shift_id = test_context.get_last("shift_id")
        assert shift_id, "Shift ID from previous step is missing"
        
        if mock_api:
            mock_api.add(
                responses.POST, 
                f"{client.base_url}/api/web/v1/work_shift/finish", 
                json={"status": "finished"}, 
                status=200
            )
        
        resp = finish_shift(client, json={"id": shift_id})
        assert resp.status_code == 200

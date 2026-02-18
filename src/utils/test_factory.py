import uuid
import random
import string
from datetime import datetime

class TestDataFactory:
    @staticmethod
    def random_string(length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def create_line_payload():
        return {
            "name": f"Line_{TestDataFactory.random_string(5)}",
            "description": "Auto-generated test line",
            "number": random.randint(1, 100)
        }

    @staticmethod
    def create_shift_payload(line_id):
        return {
            "line_id": line_id,
            "gtin": f"046{random.randint(1000000000, 9999999999)}",
            "batch": f"BATCH-{TestDataFactory.random_string(4)}",
            "exp_date": datetime.now().strftime("%Y-%m-%d")
        }

    @staticmethod
    def create_user_payload():
        return {
            "login": f"user_{TestDataFactory.random_string(5)}",
            "password": "Password123!",
            "role": "operator"
        }

from typing import Dict, Any, List, Optional
import random

class TestContext:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TestContext, cls).__new__(cls)
            cls._instance.reset()
        return cls._instance

    def reset(self):
        self.store: Dict[str, List[Any]] = {
            "lines": [],
            "shifts": [],
            "users": [],
            "products": [],
            "aggregations": [],
            "tokens": []
        }

    def add(self, entity_type: str, data: Any):
        if entity_type not in self.store:
            self.store[entity_type] = []
        self.store[entity_type].append(data)

    def get(self, entity_type: str) -> Optional[Any]:
        """Get a random entity of the given type, or None."""
        items = self.store.get(entity_type, [])
        if not items:
            return None
        return random.choice(items)

    def get_last(self, entity_type: str) -> Optional[Any]:
        """Get the most recently created entity."""
        items = self.store.get(entity_type, [])
        if not items:
            return None
        return items[-1]

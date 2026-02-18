import json
import re

class OpenAPIParsingError(Exception):
    pass

class OpenAPIHelper:
    def __init__(self, path="openapi.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.spec = json.load(f)
        except FileNotFoundError:
            raise OpenAPIParsingError(f"File {path} not found")

    def get_operation(self, path, method):
        """Finds operation details by path and method."""
        if path.startswith("<server>"):
            path = path.replace("<server>", "")
        
        if path in self.spec["paths"]:
            return self.spec["paths"][path].get(method.lower())
        return None

    def resolve_ref(self, ref):
        """Resolves a $ref string to the actual schema object."""
        if not ref or not ref.startswith("#/"):
            return {}
        parts = ref.split("/")
        current = self.spec
        for part in parts[1:]:
            current = current.get(part, {})
        return current

    def get_request_model_name(self, operation):
        """Returns the model class name for the request body if available."""
        if "requestBody" in operation:
            content = operation["requestBody"].get("content", {})
            json_media = content.get("application/json", {})
            schema = json_media.get("schema", {})
            if "$ref" in schema:
                return schema["$ref"].split("/")[-1]
            # Handle cases where schema is defined inline but might have a generated name
            # For now, we return None to avoid guessing wrong names
        return None

    def get_parameters(self, operation):
        """Extracts parameters and body arguments."""
        params = []
        
        # 1. Path/Query Parameters
        if "parameters" in operation:
            for p in operation["parameters"]:
                if "$ref" in p:
                    p = self.resolve_ref(p["$ref"])
                
                params.append({
                    "name": p["name"],
                    "in": p["in"],
                    "required": p.get("required", False),
                    "type": p.get("schema", {}).get("type", "any"),
                    "description": p.get("description", "")
                })

        # 2. Request Body
        if "requestBody" in operation:
            content = operation["requestBody"].get("content", {})
            json_media = content.get("application/json", {})
            schema = json_media.get("schema", {})
            
            if "$ref" in schema:
                schema = self.resolve_ref(schema["$ref"])
            
            # If it's an object with properties
            if schema.get("type") == "object" and "properties" in schema:
                required_fields = schema.get("required", [])
                for name, prop in schema["properties"].items():
                    if "$ref" in prop:
                        # Resolve ref to get type name or details
                        ref_name = prop["$ref"].split("/")[-1]
                        prop_type = ref_name # Use class name as type hint
                    else:
                        prop_type = prop.get("type", "any")
                        
                    params.append({
                        "name": name,
                        "in": "body",
                        "required": name in required_fields,
                        "type": prop_type,
                        "description": prop.get("description", "")
                    })
        
        return params

    def generate_docstring(self, operation, path, method):
        summary = operation.get("summary", "No summary")
        desc = operation.get("description", "")
        params = self.get_parameters(operation)
        
        doc = f'"""\n    {summary}\n\n    {desc}\n\n    Endpoint: {path}\n    Method: {method.upper()}\n\n    Parameters:\n'
        
        for p in params:
            req = " (required)" if p["required"] else ""
            doc += f'    - {p["name"]} ({p["type"]}){req}: {p["description"]}\n'
            
        doc += '    """'
        return doc

    def generate_payload_template(self, operation):
        """Generates a sample payload dictionary for tests."""
        params = self.get_parameters(operation)
        payload = {}
        for p in params:
            if p["in"] == "body":
                # Generate dummy data based on type
                if p["type"] == "string":
                    payload[p["name"]] = "test_string"
                elif p["type"] == "integer":
                    payload[p["name"]] = 1
                elif p["type"] == "boolean":
                    payload[p["name"]] = True
                elif p["type"] == "array":
                    payload[p["name"]] = []
                else:
                    payload[p["name"]] = {} # object or unknown
        return payload

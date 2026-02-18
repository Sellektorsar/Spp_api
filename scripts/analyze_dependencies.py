import re
import json
from pathlib import Path
from src.utils.openapi_helper import OpenAPIHelper

def analyze_dependencies():
    try:
        helper = OpenAPIHelper()
    except Exception as e:
        print(f"Failed to load OpenAPI: {e}")
        return

    # Map: Parameter Name -> List of Methods that require it
    requires = {}
    # Map: Field Name -> List of Methods that produce it
    produces = {}
    
    # Analyze all operations
    for path, path_item in helper.spec.get("paths", {}).items():
        for method, op in path_item.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue
                
            op_id = f"{method.upper()} {path}"
            op_summary = op.get("summary", op_id)
            
            # --- Consumer Analysis ---
            params = helper.get_parameters(op)
            for p in params:
                name = p["name"]
                if name not in requires:
                    requires[name] = []
                requires[name].append(op_id)
            
            # --- Producer Analysis ---
            responses = op.get("responses", {})
            success = responses.get("200") or responses.get("201")
            if success:
                content = success.get("content", {}).get("application/json", {})
                schema = content.get("schema", {})
                
                if "$ref" in schema:
                    schema = helper.resolve_ref(schema["$ref"])
                
                if schema.get("type") == "object" and "properties" in schema:
                    for prop_name in schema["properties"]:
                        if prop_name not in produces:
                            produces[prop_name] = []
                        produces[prop_name].append(op_id)
                        
                        # Heuristic: if method is "create_line" and returns "id", treat as "line_id"
                        if prop_name == "id":
                            if "line" in path or "line" in op_summary.lower():
                                produces.setdefault("line_id", []).append(op_id)
                            if "shift" in path or "shift" in op_summary.lower():
                                produces.setdefault("shift_id", []).append(op_id)
                            if "user" in path or "user" in op_summary.lower():
                                produces.setdefault("user_id", []).append(op_id)
                            if "aggregation" in path:
                                produces.setdefault("aggregation_id", []).append(op_id)

    # --- Match ---
    chains = []
    
    # 1. Exact Match
    for param in requires:
        if param in produces:
            for producer in produces[param]:
                # Filter self-loops (update method producing same id)
                # Filter trivial matches (get_X using id produced by get_X)
                chains.append({
                    "param": param,
                    "producer": producer,
                    "consumers": requires[param],
                    "type": "Exact"
                })
                
    # 2. ID Heuristics (already handled by populating "line_id" etc in produces)
    
    # --- Report ---
    report = []
    report.append("# Dependency Analysis Report")
    report.append("Automated analysis of API dependencies and potential reuse chains.")
    
    report.append("\n## Reusable Parameters (Producers)")
    for param, prods in sorted(produces.items()):
        if len(prods) > 0 and param.endswith("id"):
            report.append(f"- **{param}**")
            for p in prods[:3]: # Limit list
                report.append(f"  - Produced by: `{p}`")
    
    report.append("\n## Consumption Chains")
    for chain in sorted(chains, key=lambda x: x['param']):
        if not chain['param'].endswith("id") and not chain['param'].endswith("token"):
            continue # Focus on IDs and Tokens
            
        report.append(f"### Parameter: `{chain['param']}`")
        report.append(f"- **Source**: `{chain['producer']}`")
        report.append(f"- **Used in {len(chain['consumers'])} methods**, examples:")
        for c in chain['consumers'][:5]:
             report.append(f"  - `{c}`")
        report.append("")

    Path("DEPENDENCY_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Analysis complete. Found {len(chains)} potential dependency chains.")

if __name__ == "__main__":
    analyze_dependencies()

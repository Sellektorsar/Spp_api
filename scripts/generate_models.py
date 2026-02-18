import subprocess
import sys
from pathlib import Path

def main():
    openapi_path = Path("openapi.json")
    output_dir = Path("src/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "generated.py"
    
    if not openapi_path.exists():
        print("openapi.json not found!")
        return

    cmd = [
        sys.executable, "-m", "datamodel_code_generator",
        "--input", str(openapi_path),
        "--output", str(output_file),
        "--input-file-type", "openapi",
        "--output-model-type", "pydantic_v2.BaseModel",
        "--target-python-version", "3.13",
        "--use-schema-description",
        "--use-field-description",
        "--collapse-root-models",
        "--disable-timestamp"
    ]
    
    print(f"Generating models from {openapi_path}...")
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully generated models in {output_file}")
        
        # Create __init__.py
        init_file = output_dir / "__init__.py"
        init_file.write_text("from .generated import *", encoding="utf-8")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating models: {e}")

if __name__ == "__main__":
    main()

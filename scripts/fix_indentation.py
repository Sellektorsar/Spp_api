from pathlib import Path

def fix_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    
    # Define the wrong block (double indented)
    # Note: Using explicit spaces to match what was likely written
    wrong_block = """        if body:
            if hasattr(body, "model_dump"):
                kwargs["json"] = body.model_dump(by_alias=True, exclude_none=True)
            else:
                kwargs["json"] = body"""
    
    # Define the correct block (single indented)
    correct_block = """    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body"""
            
    if wrong_block in content:
        print(f"Fixing {file_path}")
        new_content = content.replace(wrong_block, correct_block)
        file_path.write_text(new_content, encoding="utf-8")
        return True
    return False

def main():
    src_dir = Path("src/api")
    count = 0
    for file_path in src_dir.rglob("*.py"):
        if fix_file(file_path):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()

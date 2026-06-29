import ast
import os
import sys

def check_syntax(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, e
    except Exception as e:
        return False, e

def main():
    root = r"D:\Quant"
    errors = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                success, error = check_syntax(filepath)
                if not success:
                    errors.append((filepath, error))
    if errors:
        print("Syntax errors found:")
        for filepath, error in errors:
            print(f"{filepath}: {error}")
        sys.exit(1)
    else:
        print("All Python files have valid syntax.")
        sys.exit(0)

if __name__ == "__main__":
    main()

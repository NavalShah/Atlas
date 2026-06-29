import os
import sys

def remove_bom(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    root = r"D:\Quant"
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip .git directory
        if ".git" in dirpath.split(os.sep):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    remove_bom(filepath)
                    print(f"Fixed BOM in {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()

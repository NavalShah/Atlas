import os
import sys

def remove_bom(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    root = r"D:\Quant"
    extensions = [".py", ".yaml", ".yml", ".txt", ".md", ".toml", ".gitignore"]
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip .git directory
        if ".git" in dirpath.split(os.sep):
            continue
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                filepath = os.path.join(dirpath, filename)
                remove_bom(filepath)

if __name__ == "__main__":
    main()

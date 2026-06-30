import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    in_class = False
    class_indent = 0
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not in_class and stripped.startswith('class ') and '(BaseFeature)' in line:
            in_class = True
            class_indent = len(line) - len(line.lstrip())
            new_lines.append(line)
            i += 1
            continue
        
        if in_class:
            # Check if we've left the class: a line that is not indented more than class_indent (and not empty or comment)
            if stripped and (len(line) - len(line.lstrip()) <= class_indent):
                # We've left the class
                in_class = False
                # We'll just fall through and add the line normally
                pass
            # Check for the category property pattern
            if stripped.startswith('@property') and i+2 < len(lines):
                next_line = lines[i+1]
                next_next_line = lines[i+2]
                if next_line.strip().startswith('def category(self) -> str:') and \
                   next_next_line.strip().startswith('return '):
                    ret_line = next_next_line.strip()
                    match = re.search(r"return\s+['\"]([^'\"]+)['\"]", ret_line)
                    if match:
                        cat_string = match.group(1)
                        indent = line[:len(line) - len(line.lstrip())]
                        new_lines.append(indent + f'_category = \'{cat_string}\'')
                        new_lines.append(indent + '@property')
                        new_lines.append(indent + 'def category(self) -> str:')
                        new_lines.append(indent + '    return self._category')
                        i += 3
                        continue
        # If we didn't match, just add the line
        new_lines.append(line)
        i += 1
    
    new_content = '\n'.join(new_lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Processed {filepath}')

# Process each feature file
feature_dir = os.path.join('.', 'atlas_quant', 'features')
for filename in os.listdir(feature_dir):
    if filename.endswith('.py') and filename != '__init__.py' and filename != 'base.py':
        process_file(os.path.join(feature_dir, filename))

import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith('@property') and i+2 < len(lines):
            next_line = lines[i+1]
            next_next_line = lines[i+2]
            if next_line.lstrip().startswith('def category(self) -> str:') and \
               next_next_line.lstrip().startswith('return '):
                # Found the pattern
                indent = line[:len(line) - len(line.lstrip())]
                # Extract the return string
                ret_line = next_next_line.strip()
                match = re.search(r"return\s+['\"]([^'\"]+)['\"]", ret_line)
                if match:
                    cat_string = match.group(1)
                    # Replace the three lines with new three lines
                    lines[i] = indent + f'_category = \'{cat_string}\'\n'
                    lines[i+1] = indent + '@property\n'
                    lines[i+2] = indent + 'def category(self) -> str:\n'
                    # We need to add the return line with proper indentation
                    lines.insert(i+3, indent + '    return self._category\n')
                    # We have added an extra line, so we need to skip the original three lines and the newly added line?
                    # We replaced three lines with four lines? Actually we replaced three lines with four lines? Let's see:
                    # Original lines at i, i+1, i+2: three lines.
                    # We set line i to new string (with newline), line i+1 to new string, line i+2 to new string.
                    # Then we insert a new line at i+3.
                    # So we have effectively replaced three lines with four lines.
                    # We need to increment i by 4 to skip the original three and the new one? Actually we want to move past the original three and the new line
                    # then continue after the new line we inserted? But we have already modified the list; we should just increment i by 3 (to skip the original three)
                    # and then the loop will increment i by 1 again? We are not incrementing i automatically; we are controlling i.
                    # We'll set i to i+3 (to skip the original three lines) and then the loop will continue, but we have inserted a line at i+3, so we need to skip that too?
                    # Let's think: we want to process the next line after the inserted line. So we should set i = i+4 (because we have consumed three original lines and we want to skip the inserted line as well? Actually we want to move past the entire block we replaced, which is now four lines long.
                    # So we set i = i+4
                    i += 4
                    continue
        i += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f'Processed {filepath}')

# Process each feature file
feature_dir = os.path.join('.', 'atlas_quant', 'features')
for filename in os.listdir(feature_dir):
    if filename.endswith('.py') and filename != '__init__.py' and filename != 'base.py':
        process_file(os.path.join(feature_dir, filename))

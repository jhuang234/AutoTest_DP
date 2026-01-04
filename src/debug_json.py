import re
import json

file_path = "src/full_config.json"
try:
    with open(file_path, 'r') as f:
        content = f.read()

    print("--- Original Content (First 200 chars) ---")
    print(content[:200])

    content_no_comments = re.sub(r'#.*', '', content)
    content_no_comments = re.sub(r'//.*', '', content_no_comments)

    print("\n--- Stripped Content (First 200 chars) ---")
    print(content_no_comments[:200])

    config = json.loads(content_no_comments)
    print("\nSUCCESS: JSON loaded.")
    print("Keys:", list(config.keys())[:5])
except Exception as e:
    print(f"\nFAIL: {e}")
    # Print the line where it failed if possible
    if hasattr(e, 'lineno'):
         start = max(0, e.lineno - 2)
         lines = content_no_comments.splitlines()
         print(f"Error at line {e.lineno}, col {e.colno}")
         for i in range(start, min(len(lines), e.lineno + 1)):
             print(f"{i+1}: {lines[i]}")

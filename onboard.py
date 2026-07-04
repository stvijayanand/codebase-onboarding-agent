import os
import sys

# Ensure src directory is in the import path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from cli import main

if __name__ == "__main__":
    main()

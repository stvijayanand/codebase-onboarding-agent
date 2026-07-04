import os
import sys
import unittest
import tempfile
import shutil

# Ensure src directory is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import utils

class TestCodebaseOnboardingConcierge(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for sandboxing tests
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.test_dir)

    def test_is_safe_path(self):
        # Valid path
        valid_path = os.path.join(self.test_dir, "src", "main.py")
        self.assertTrue(utils.is_safe_path(self.test_dir, valid_path))
        
        # Relative valid path
        self.assertTrue(utils.is_safe_path(self.test_dir, "src/main.py"))

        # Directory traversal path escaping sandbox
        invalid_path = os.path.join(self.test_dir, "..", "secret.txt")
        self.assertFalse(utils.is_safe_path(self.test_dir, invalid_path))
        
        # Absolute path outside sandbox
        self.assertFalse(utils.is_safe_path(self.test_dir, "C:\\Windows\\System32"))

    def test_list_files_in_sandbox(self):
        # Create dummy file tree
        os.makedirs(os.path.join(self.test_dir, "src"))
        os.makedirs(os.path.join(self.test_dir, "node_modules")) # should be ignored
        
        # Files to include
        with open(os.path.join(self.test_dir, "src", "main.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(self.test_dir, "README.md"), "w") as f:
            f.write("# Hello")
            
        # Files to ignore
        with open(os.path.join(self.test_dir, "node_modules", "package.json"), "w") as f:
            f.write("{}")
        with open(os.path.join(self.test_dir, "src", "image.png"), "w") as f:
            f.write("binary data")
            
        files = utils.list_files_in_sandbox(self.test_dir)
        paths = [f["path"] for f in files]
        
        self.assertIn("src/main.py", paths)
        self.assertIn("README.md", paths)
        self.assertNotIn("node_modules/package.json", paths)
        self.assertNotIn("src/image.png", paths)

    def test_read_file_safe(self):
        test_file = os.path.join(self.test_dir, "hello.py")
        with open(test_file, "w") as f:
            f.write("content")
            
        # Read valid path
        content = utils.read_file_safe(self.test_dir, "hello.py")
        self.assertEqual(content, "content")
        
        # Deny invalid path
        with self.assertRaises(PermissionError):
            utils.read_file_safe(self.test_dir, "../escaping_file.py")

    def test_search_symbols_regex(self):
        # Create dummy file with declarations
        test_file = os.path.join(self.test_dir, "app.js")
        with open(test_file, "w") as f:
            f.write("""
class DatabaseConnection {
    constructor() {}
}
function connectDB() {
    return new DatabaseConnection();
}
""")
            
        # Search for Class definition
        results = utils.search_symbols_regex(self.test_dir, "DatabaseConnection")
        self.assertTrue(len(results) >= 2) # matches class decl and function body
        
        # Verify it highlights class declaration
        class_decls = [r for r in results if r["is_declaration"]]
        self.assertTrue(len(class_decls) >= 1)
        self.assertIn("class DatabaseConnection", class_decls[0]["content"])

    def test_run_ast_query_python(self):
        test_file = os.path.join(self.test_dir, "math_utils.py")
        with open(test_file, "w") as f:
            f.write("""
import os
import sys
from math import sqrt

class Calculator:
    \"\"\"Docstring for Calculator class.\"\"\"
    def add(self, a, b):
        return a + b
        
def root_func(x):
    \"\"\"Docstring for root function.\"\"\"
    return sqrt(x)
""")
            
        res = utils.run_ast_query(self.test_dir, "math_utils.py")
        self.assertEqual(res["language"], "python")
        self.assertIn("os", res["imports"])
        self.assertIn("math.sqrt", res["imports"])
        
        self.assertEqual(len(res["classes"]), 1)
        self.assertEqual(res["classes"][0]["name"], "Calculator")
        self.assertEqual(res["classes"][0]["methods"][0]["name"], "add")
        
        self.assertEqual(len(res["functions"]), 1)
        self.assertEqual(res["functions"][0]["name"], "root_func")

    def test_imports_and_modules(self):
        # Verify all code modules can be imported without errors
        try:
            import cli
            import mcp_server
            import agents.base
            import agents.explorer
            import agents.mapper
            import agents.doc_writer
            import agents.qa
            import agents.orchestrator
        except Exception as e:
            self.fail(f"Importing code modules failed: {str(e)}")

if __name__ == "__main__":
    unittest.main()

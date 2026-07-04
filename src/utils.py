import os
import re
import ast
import subprocess
from typing import List, Dict, Any, Optional

def is_safe_path(base_dir: str, target_path: str) -> bool:
    """
    Validates that target_path resolves to a location within base_dir.
    Prevents directory traversal attacks.
    """
    abs_base = os.path.abspath(base_dir)
    # If target_path is relative, resolve it against abs_base
    if not os.path.isabs(target_path):
        abs_target = os.path.abspath(os.path.join(abs_base, target_path))
    else:
        abs_target = os.path.abspath(target_path)
    
    # Commonpath returns the longest common sub-path
    common = os.path.commonpath([abs_base, abs_target])
    return common == abs_base

def list_files_in_sandbox(sandbox_dir: str, max_files: int = 400) -> List[Dict[str, Any]]:
    """
    Recursively lists all files in the sandbox directory.
    Excludes binary files and typical dependency/meta/test/doc directories.
    """
    if not os.path.exists(sandbox_dir):
        return []
        
    abs_base = os.path.abspath(sandbox_dir)
    file_list = []
    
    # Exclude directories
    exclude_dirs = {
        '.git', 'node_modules', '.venv', 'venv', '__pycache__', 
        'dist', 'build', '.idea', '.vscode', 'env', '.gemini',
        '.agents', 'obj', 'bin', 'docs', 'tests', 'test', 'spec',
        'htmlcov', 'docs_src', '.github', 'site-packages'
    }
    
    # Exclude file extensions (binaries, lock files, images, etc.)
    exclude_exts = {
        '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', 
        '.tar', '.gz', '.db', '.sqlite', '.exe', '.dll', '.so',
        '.dylib', '.bin', '.woff', '.woff2', '.eot', '.ttf',
        '.lock', '-lock.json', '.pyc', '.class'
    }

    for root, dirs, files in os.walk(abs_base):
        # Modify dirs in-place to prune excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in exclude_exts or file.startswith('.'):
                continue
                
            full_path = os.path.join(root, file)
            if not is_safe_path(abs_base, full_path):
                continue
                
            rel_path = os.path.relpath(full_path, abs_base)
            try:
                size = os.path.getsize(full_path)
            except OSError:
                size = 0
                
            file_list.append({
                "path": rel_path.replace("\\", "/"),
                "size": size,
                "extension": ext
            })
            
    if len(file_list) > max_files:
        truncated_list = file_list[:max_files]
        truncated_list.append({
            "path": f"... (truncated, showing {max_files} of {len(file_list)} files. Use search_symbols to locate other files)",
            "size": 0,
            "extension": ""
        })
        return truncated_list
        
    return file_list

def read_file_safe(sandbox_dir: str, rel_path: str) -> str:
    """
    Safely reads file contents within the sandboxed directory.
    """
    abs_base = os.path.abspath(sandbox_dir)
    full_path = os.path.join(abs_base, rel_path)
    
    if not is_safe_path(abs_base, full_path):
        raise PermissionError(f"Access denied: path '{rel_path}' is outside the sandbox.")
        
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: '{rel_path}'")
        
    if os.path.isdir(full_path):
        raise IsADirectoryError(f"Path '{rel_path}' is a directory.")
        
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def search_symbols_regex(sandbox_dir: str, query: str) -> List[Dict[str, Any]]:
    """
    Searches for symbols matching query (regex/substring) across files.
    Identifies typical class/function declarations in multiple languages.
    """
    files = list_files_in_sandbox(sandbox_dir)
    abs_base = os.path.abspath(sandbox_dir)
    results = []
    
    # Common function/class patterns in various languages
    # e.g., class Foo, function bar, def baz, func qux, type Struct
    pattern = re.compile(query, re.IGNORECASE)
    
    for f_info in files:
        rel_path = f_info["path"]
        full_path = os.path.join(abs_base, rel_path)
        
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_idx, line in enumerate(f, 1):
                    # Check if line matches query and looks like a definition
                    if pattern.search(line):
                        # Attempt to see if it is a declaration line
                        is_declaration = any(kw in line for kw in [
                            "class ", "def ", "function ", "func ", "fn ", "interface ", "struct ", "type "
                        ]) or "=>" in line
                        
                        results.append({
                            "file": rel_path,
                            "line": line_idx,
                            "content": line.strip(),
                            "is_declaration": is_declaration
                        })
        except Exception:
            continue
            
    return results[:100]  # Cap results at 100

def get_git_history(sandbox_dir: str, limit: int = 20) -> Dict[str, Any]:
    """
    Gets recent git commits and details about top contributors.
    """
    abs_base = os.path.abspath(sandbox_dir)
    if not os.path.exists(os.path.join(abs_base, ".git")):
        return {"status": "No git repository found", "commits": []}
        
    try:
        # Run git log
        log_cmd = ["git", "--no-pager", "log", f"-n", str(limit), "--pretty=format:%h|%an|%ae|%ad|%s", "--date=short"]
        result = subprocess.run(
            log_cmd, 
            cwd=abs_base, 
            capture_output=True, 
            text=True, 
            check=True,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
        lines = result.stdout.strip().split("\n")
        
        commits = []
        author_counts = {}
        for line in lines:
            if not line:
                continue
            parts = line.split("|")
            if len(parts) == 5:
                h, name, email, date, subject = parts
                commits.append({
                    "hash": h,
                    "author": name,
                    "email": email,
                    "date": date,
                    "subject": subject
                })
                author_counts[name] = author_counts.get(name, 0) + 1
                
        # Sorted authors
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "status": "success",
            "commits": commits,
            "top_contributors": [{"name": name, "commits": count} for name, count in top_authors]
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "commits": []}

def run_ast_query(sandbox_dir: str, rel_path: str) -> Dict[str, Any]:
    """
    Parses file imports, classes, methods, and functions.
    Uses AST for Python, regex for other languages.
    """
    abs_base = os.path.abspath(sandbox_dir)
    full_path = os.path.join(abs_base, rel_path)
    
    if not is_safe_path(abs_base, full_path):
        raise PermissionError(f"Access denied: path '{rel_path}' is outside the sandbox.")
        
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: '{rel_path}'")
        
    _, ext = os.path.splitext(rel_path)
    ext = ext.lower()
    
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    if ext == ".py":
        return _parse_python_ast(content)
    elif ext in [".js", ".ts", ".jsx", ".tsx"]:
        return _parse_js_ts_regex(content)
    elif ext == ".go":
        return _parse_go_regex(content)
    else:
        return _parse_generic_regex(content)

def _parse_python_ast(content: str) -> Dict[str, Any]:
    """
    Uses Python's built-in AST module to extract code structure.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}", "imports": [], "classes": [], "functions": []}
        
    imports = []
    classes = []
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for name in node.names:
                imports.append(f"{module}.{name.name}" if module else name.name)
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append({
                        "name": item.name,
                        "line": item.lineno,
                        "docstring": ast.get_docstring(item) or ""
                    })
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "methods": methods,
                "docstring": ast.get_docstring(node) or ""
            })
        elif isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
            # Top level functions
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "docstring": ast.get_docstring(node) or ""
            })
            
    # De-duplicate top level functions that are actually inside classes (the walk above gets everything)
    # We filter out functions that belong to classes
    class_method_names = set()
    for c in classes:
        for m in c["methods"]:
            class_method_names.add((m["name"], m["line"]))
            
    functions = [f for f in functions if (f["name"], f["line"]) not in class_method_names]
            
    return {
        "language": "python",
        "imports": list(set(imports)),
        "classes": classes,
        "functions": functions
    }

def _parse_js_ts_regex(content: str) -> Dict[str, Any]:
    """
    Lightweight, fast regex parser for JS/TS codebases.
    """
    imports = []
    classes = []
    functions = []
    
    lines = content.split("\n")
    
    # Simple regexes
    import_pat = re.compile(r'(?:import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"])|(?:require\([\'"]([^\'"]+)[\'"]\))')
    class_pat = re.compile(r'\bclass\s+(\w+)')
    func_pat = re.compile(r'\b(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]+)\s*=>)')
    
    for idx, line in enumerate(lines, 1):
        # Imports
        imp_match = import_pat.search(line)
        if imp_match:
            val = imp_match.group(1) or imp_match.group(2)
            if val:
                imports.append(val)
                
        # Classes
        cls_match = class_pat.search(line)
        if cls_match:
            classes.append({
                "name": cls_match.group(1),
                "line": idx,
                "methods": []  # Regex class methods parsing is simplified
            })
            
        # Functions
        fn_match = func_pat.search(line)
        if fn_match:
            name = fn_match.group(1) or fn_match.group(2)
            if name and name not in ["if", "for", "while", "switch"]:
                functions.append({
                    "name": name,
                    "line": idx
                })
                
    return {
        "language": "javascript/typescript",
        "imports": list(set(imports)),
        "classes": classes,
        "functions": functions
    }

def _parse_go_regex(content: str) -> Dict[str, Any]:
    """
    Lightweight, fast regex parser for Go.
    """
    imports = []
    classes = []  # In Go we map Structs to classes
    functions = []
    
    lines = content.split("\n")
    
    # Matches imports
    import_single = re.compile(r'import\s+[\'"]([^\'"]+)[\'"]')
    # Matches struct definitions
    struct_pat = re.compile(r'type\s+(\w+)\s+struct')
    # Matches functions: func Foo(...) or func (r *Rec) Foo(...)
    func_pat = re.compile(r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(')
    
    in_import_block = False
    for idx, line in enumerate(lines, 1):
        line_strip = line.strip()
        
        # Multiline imports
        if line_strip == "import (":
            in_import_block = True
            continue
        if in_import_block and line_strip == ")":
            in_import_block = False
            continue
        if in_import_block:
            m = re.search(r'[\'"]([^\'"]+)[\'"]', line_strip)
            if m:
                imports.append(m.group(1))
            continue
            
        # Single line import
        m = import_single.search(line_strip)
        if m:
            imports.append(m.group(1))
            
        # Struct definitions (mapped to classes)
        m = struct_pat.search(line_strip)
        if m:
            classes.append({
                "name": m.group(1),
                "line": idx,
                "methods": []
            })
            
        # Functions
        m = func_pat.search(line_strip)
        if m:
            name = m.group(1)
            functions.append({
                "name": name,
                "line": idx
            })
            
    return {
        "language": "go",
        "imports": list(set(imports)),
        "classes": classes,  # structs
        "functions": functions
    }

def _parse_generic_regex(content: str) -> Dict[str, Any]:
    """
    Fallback parser for other languages.
    """
    classes = []
    functions = []
    lines = content.split("\n")
    
    class_pat = re.compile(r'\b(?:class|interface|struct)\s+(\w+)')
    func_pat = re.compile(r'\b(?:def|func|fn|function)\s+(\w+)')
    
    for idx, line in enumerate(lines, 1):
        m = class_pat.search(line)
        if m:
            classes.append({"name": m.group(1), "line": idx, "methods": []})
        m = func_pat.search(line)
        if m:
            functions.append({"name": m.group(1), "line": idx})
            
    return {
        "language": "generic",
        "imports": [],
        "classes": classes,
        "functions": functions
    }

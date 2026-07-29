import ast
import io
import os
import re
import tokenize
from pathlib import Path

# --------------------------------------------------
# Configuration
# --------------------------------------------------

BACKEND_ROOT = Path("./backend")
FRONTEND_ROOT = Path("./frontend")

BACKEND_OUTPUT = Path("backend_code.txt")
FRONTEND_OUTPUT = Path("frontend_code.txt")

SKIP_DIRS = {
    ".git",
    ".idea",
    ".venv",
    "__pycache__",
    "pycache",
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    ".cache",
    "alembic",
    "tests",
    "package-lock.json"
}

FRONTEND_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".css",
    ".scss",
    ".html",
    ".json",
}


# --------------------------------------------------
# Shared utilities
# --------------------------------------------------

def remove_blank_lines(text: str) -> str:
    return "\n".join(
        line.rstrip()
        for line in text.splitlines()
        if line.strip()
    )


def read_file(path: Path) -> str:
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


# --------------------------------------------------
# Python cleaner
# --------------------------------------------------

def remove_python_docstrings(source: str) -> str:
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.Module,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body.pop(0)

    return ast.unparse(tree)


def remove_python_comments(source: str) -> str:
    output = []

    tokens = tokenize.generate_tokens(io.StringIO(source).readline)

    for token in tokens:
        if token.type == tokenize.COMMENT:
            continue
        output.append(token)

    return tokenize.untokenize(output)


def clean_python(source: str) -> str:
    source = remove_python_docstrings(source)
    source = remove_python_comments(source)
    return remove_blank_lines(source)


# --------------------------------------------------
# JavaScript / TypeScript
# --------------------------------------------------

JS_COMMENT_RE = re.compile(
    r"""
    //.*?$           |   # single line
    /\*.*?\*/            # block
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


def clean_javascript(source: str) -> str:
    source = JS_COMMENT_RE.sub("", source)
    return remove_blank_lines(source)


# --------------------------------------------------
# CSS / SCSS
# --------------------------------------------------

CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def clean_css(source: str) -> str:
    source = CSS_COMMENT_RE.sub("", source)
    return remove_blank_lines(source)


# --------------------------------------------------
# HTML
# --------------------------------------------------

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def clean_html(source: str) -> str:
    source = HTML_COMMENT_RE.sub("", source)
    return remove_blank_lines(source)


# --------------------------------------------------
# JSON
# --------------------------------------------------

def clean_json(source: str) -> str:
    # Standard JSON has no comments.
    return remove_blank_lines(source)


# --------------------------------------------------
# Dispatcher
# --------------------------------------------------

def clean_file(path: Path, source: str) -> str:
    suffix = path.suffix.lower()

    if suffix == ".py":
        return clean_python(source)

    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return clean_javascript(source)

    if suffix in {".css", ".scss"}:
        return clean_css(source)

    if suffix == ".html":
        return clean_html(source)

    if suffix == ".json":
        return clean_json(source)

    return source


# --------------------------------------------------
# Processing
# --------------------------------------------------

def collect_files(root: Path, extensions: set[str]):
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if should_skip(path):
            continue

        if path.suffix.lower() in extensions:
            yield path


def write_project(root: Path, extensions: set[str], output_file: Path):
    with open(output_file, "w", encoding="utf-8") as out:

        for path in sorted(collect_files(root, extensions)):

            try:
                source = read_file(path)
                cleaned = clean_file(path, source)

            except Exception as e:
                print(f"Skipping {path}: {e}")
                continue

            out.write(f"# File: {path}\n")
            out.write(cleaned)
            out.write("\n\n")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    write_project(
        BACKEND_ROOT,
        {".py"},
        BACKEND_OUTPUT,
    )

    write_project(
        FRONTEND_ROOT,
        FRONTEND_EXTENSIONS,
        FRONTEND_OUTPUT,
    )


if __name__ == "__main__":
    main()
import ast
import io
import os
import tokenize


def remove_comments(source: str) -> str:
    """
    Removes:
    - module/class/function docstrings
    - # comments (including inline comments)
    """

    # ---------- Remove docstrings ----------
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body.pop(0)

    source = ast.unparse(tree)

    # ---------- Remove # comments ----------
    output = []
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)

    for token in tokens:
        if token.type == tokenize.COMMENT:
            continue
        output.append(token)

    cleaned = tokenize.untokenize(output)

    # Remove empty lines
    cleaned = "\n".join(
        line.rstrip()
        for line in cleaned.splitlines()
        if line.strip()
    )

    return cleaned


if __name__ == "__main__":
    open("backend_code.txt", "w").close()

    for dirpath, dirnames, filenames in os.walk("./backend/app"):
        # Skip unwanted directories
        parts = dirpath.split(os.sep)
        if "alembic" in parts or ".venv" in parts or "tests" in parts:
            continue

        for filename in filenames:
            if filename.startswith("."):
                continue

            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)

                with open(filepath, "r", encoding="utf-8") as f:
                    content = remove_comments(f.read())

                with open("backend_code.txt", "a", encoding="utf-8") as f:
                    f.write(f"# File: {filepath}\n")
                    f.write(content)
                    f.write("\n\n")
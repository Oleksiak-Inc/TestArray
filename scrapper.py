import os

if __name__ == "__main__":
    open("backend_code.txt", "w").close()
    for dirpath, dirnames, filenames in os.walk("./backend"):
        # Skip unwanted directories
        parts = dirpath.split(os.sep)
        if "alembic" in parts or ".venv" in parts:
            continue
        
        for filename in filenames:
            if filename.startswith("."):
                continue
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, "r") as file:
                    content = file.read()
                with open("backend_code.txt", "a") as file:
                    file.write(f"# File: {filepath}\n")
                    file.write(content)
                    file.write("\n\n")
                #print(f"-- File: {filepath} --")
                #print(content)
                #print()


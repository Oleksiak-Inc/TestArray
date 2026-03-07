import os

for root, _, files in os.walk("."):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, encoding="utf-8") as file:
                    file.read()
            except UnicodeDecodeError:
                print("Bad encoding in:", path)

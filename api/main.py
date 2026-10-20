# api/main.py

from config import PROJECT_ROOT, SQL_DIR, load_yaml

# --------------------------------------------------------------------------------

config = load_yaml(PROJECT_ROOT / "config/config.yaml")

DATABASE = config["database"]["file"]

# --------------------------------------------------------------------------------

def main():
    return


if __name__ == "__main__":
    main()



from pathlib import Path


SCHEMA_DIRS = {
    "FMI2": "3rdParty/FMI2/schema",
    "FMI3": "3rdParty/FMI3/schema",
    "SSP1": "3rdParty/FMI2/schema",
    "SSP2": "3rdParty/FMI2/schema",
}

LIB_SCHEMA_PATH = Path("pyssp_standard/schema")

def main():
    for name, path in SCHEMA_DIRS.items():
        target_dir = LIB_SCHEMA_PATH / name
        target_dir.mkdir(parents=True, exist_ok=True)

        



if __name__ == "__main__":
    main()

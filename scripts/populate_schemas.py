


from pathlib import Path
import shutil
import os


SCHEMA_DIRS = {
    "FMI2": "3rdParty/FMI2/schema",
    "FMI3": "3rdParty/FMI3/schema",
    "SSP1": "3rdParty/FMI2/schema",
    "SSP2": "3rdParty/FMI2/schema",
    "SSP-LS-Traceability": "3rdParty/ssp-ls-traceability",
}

LIB_SCHEMA_PATH = Path("pyssp_standard/schema")

def main():
    for name, source_dir in SCHEMA_DIRS.items():
        source_dir = Path(source_dir)
        target_dir = LIB_SCHEMA_PATH / name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for filename in os.listdir(source_dir):
            if filename.endswith('.xsd'):
                print(source_dir / filename, target_dir /filename)
                shutil.copy( source_dir / filename, target_dir /filename)

if __name__ == "__main__":
    main()

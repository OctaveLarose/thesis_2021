import os
import subprocess
import sys


CODEBASES_DIR = "../data/java_codebases"
OUTPUT_DATA_DIR = "../data/ck_data"
CK_JAR_PATH = "./ck-0.6.3-with-deps.jar"
OUTPUT_CSV_FILE_NAMES = ["class", "method", "field", "variable"]


def main():
    codebases_names = os.listdir(CODEBASES_DIR)

    for idx, codebase_name in enumerate(codebases_names):
        codebase_path = os.path.join(CODEBASES_DIR, codebase_name)

        if os.path.exists(os.path.join(OUTPUT_DATA_DIR, OUTPUT_CSV_FILE_NAMES[0], f"{OUTPUT_CSV_FILE_NAMES[0]}_{codebase_name}.csv")):
            print(f"{OUTPUT_CSV_FILE_NAMES[0]}_{codebase_name}.csv exists, skipping. ({idx + 1}/{len(codebases_names)})")
            continue

        if run_ck(codebase_path):
            move_output_csv_files(codebase_path)
        else:
            print("Error while running CK. Deleting CSV files.")
            for csv_fn in OUTPUT_CSV_FILE_NAMES:
                if os.path.exists(csv_fn + ".csv"):
                    os.remove(csv_fn + ".csv")

        print(f"Done with {codebase_name}. ({idx + 1}/{len(codebases_names)})")


def run_ck(codebase_path: str) -> bool:
    # FLAGS REF: <use jars:true|false> <max files per partition,0=auto selection> <variables + fields metrics?
    # true|false>
    def get_ck_command_arr(flags: [str] = "true 0 true") -> [str]:
        return ["java", "-jar", os.path.abspath(CK_JAR_PATH), ".", *flags.split()]

    TIMEOUT_AFTER_X_SEC = 60
    ck_command_arr = get_ck_command_arr(codebase_path)

    try:
        subprocess.run(ck_command_arr, check=True, cwd=codebase_path, timeout=TIMEOUT_AFTER_X_SEC)
    except subprocess.TimeoutExpired:
        print(f'Error: command {" ".join(ck_command_arr)} timed out after {TIMEOUT_AFTER_X_SEC} seconds.', file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        print(f'Error: command {" ".join(ck_command_arr)} returned {e.returncode}.', file=sys.stderr)
        return False

    return True


def move_output_csv_files(codebase_path: str):
    if not os.path.isdir(OUTPUT_DATA_DIR):
        os.mkdir(OUTPUT_DATA_DIR)

    codebase_name = codebase_path.split("/")[-1]

    for csv_fn in OUTPUT_CSV_FILE_NAMES:
        if not os.path.isdir(os.path.join(OUTPUT_DATA_DIR, csv_fn)):
            os.mkdir(os.path.join(OUTPUT_DATA_DIR, csv_fn))
        os.rename(os.path.join(codebase_path, csv_fn + ".csv"),
                  os.path.join(OUTPUT_DATA_DIR, csv_fn, f"{csv_fn}_{codebase_name}.csv"))


if __name__ == "__main__":
    main()

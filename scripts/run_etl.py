#!/usr/bin/env python3
import sys
import subprocess


def main():
    # Run the ETL module as if using `python -m scripts.run_etl_pipeline`
    subprocess.run([sys.executable, "-m", "scripts.run_etl_pipeline"] + sys.argv[1:])


if __name__ == "__main__":
    main()

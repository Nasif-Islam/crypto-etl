import subprocess


def main():
    """
    Simple CLI entry point to run pytest with -v
    """
    subprocess.run(["pytest", "-v"], check=False)

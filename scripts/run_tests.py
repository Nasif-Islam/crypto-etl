import subprocess


def main():
    """
    Runs the test suite using Coverage + Pytest
    Generates a terminal report and an HTML report
    """
    subprocess.run(["coverage", "erase"], check=False)
    subprocess.run(["coverage", "run", "-m", "pytest", "-v"], check=False)
    subprocess.run(["coverage", "report", "-m"], check=False)
    subprocess.run(["coverage", "html"], check=False)

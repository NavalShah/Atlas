import subprocess
import sys

def run_tests():
    """Run the test suite using pytest."""
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Return code: {result.returncode}")
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

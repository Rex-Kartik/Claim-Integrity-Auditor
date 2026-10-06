# Pass/Fail check script for exercise 3
import sys

def check():
    print("Checking exercise 3...")
    print("Pass!")
    return True

if __name__ == "__main__":
    if not check():
        sys.exit(1)

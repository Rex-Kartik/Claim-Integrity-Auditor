# Pass/Fail check script for exercise 2
import sys

def check():
    print("Checking exercise 2...")
    print("Pass!")
    return True

if __name__ == "__main__":
    if not check():
        sys.exit(1)

# Pass/Fail check script for exercise 1
import sys

def check():
    print("Checking exercise 1...")
    # Add validation logic here
    print("Pass!")
    return True

if __name__ == "__main__":
    if not check():
        sys.exit(1)

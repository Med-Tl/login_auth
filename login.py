#!/usr/bin/env python3
import json
import sys
from pathlib import Path

USERS = Path("users.json")

def main():
    if len(sys.argv) != 3:
        print("usage: login.py USERNAME PASSWORD")
        return 2

    username, password = sys.argv[1], sys.argv[2]
    users = json.loads(USERS.read_text())
    if users.get(username, {}).get("password") == password:
        print("login ok")
        return 0

    print("login failed")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import hmac
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

BASE = Path("/home/labex/project")
LOGIN = BASE / "login.py"
GEN = BASE / "generate-code.py"
SECRET = BASE / "mfa_secret.txt"

def run(args):
    return subprocess.run(args, cwd=BASE, text=True, capture_output=True)

def expected_code(username):
    secret = SECRET.read_text().strip().encode()
    digest = hmac.new(secret, username.encode(), hashlib.sha256).hexdigest()
    return digest[:6]

def check_password_only():
    ok = run([sys.executable, str(LOGIN), "alice", "wonderland"])
    bad = run([sys.executable, str(LOGIN), "alice", "wrong"])
    if ok.returncode != 0 or "login ok" not in ok.stdout:
        print("password-only: correct password did not work")
        return 1
    if bad.returncode == 0:
        print("password-only: wrong password should fail")
        return 1
    print("password-only: complete")
    return 0

def check_secret(report=True):
    if not SECRET.exists():
        print("secret: mfa_secret.txt is missing")
        return 1
    if len(SECRET.read_text().strip()) < 16:
        print("secret: mfa_secret.txt is too short")
        return 1
    mode = stat.S_IMODE(SECRET.stat().st_mode)
    if mode != 0o600:
        print(f"secret: expected permissions 600, got {oct(mode)[2:]}")
        return 1
    if report:
        print("secret: complete")
    return 0

def check_generator(report=True, check_dependency=True):
    if check_dependency and check_secret(report=False):
        return 1
    if not GEN.exists():
        print("generator: generate-code.py is missing")
        return 1
    result = run([sys.executable, str(GEN), "alice"])
    if result.returncode != 0:
        print("generator: generate-code.py failed")
        return 1
    code = result.stdout.strip()
    if code != expected_code("alice"):
        print("generator: code does not match expected HMAC value")
        return 1
    if len(code) != 6:
        print("generator: code must be six hex characters")
        return 1
    if report:
        print("generator: complete")
    return 0

def check_enforced(report=True, check_dependency=True):
    if check_dependency and check_generator(report=False):
        return 1
    code = expected_code("alice")
    no_code = run([sys.executable, str(LOGIN), "alice", "wonderland"])
    bad_code = run([sys.executable, str(LOGIN), "alice", "wonderland", "000000"])
    good = run([sys.executable, str(LOGIN), "alice", "wonderland", code])
    if no_code.returncode == 0:
        print("enforced: password-only login should not work after MFA is enabled")
        return 1
    if bad_code.returncode == 0:
        print("enforced: wrong MFA code should fail")
        return 1
    if good.returncode != 0 or "login ok" not in good.stdout:
        print("enforced: correct password and code should succeed")
        return 1
    if SECRET.read_text().strip() in good.stdout:
        print("enforced: login output must not print the MFA secret")
        return 1
    if report:
        print("enforced: complete")
    return 0

def main():
    checks = {
        "password-only": check_password_only,
        "secret": check_secret,
        "generator": check_generator,
        "enforced": check_enforced,
    }
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        return max(
            check_secret(report=True),
            check_generator(report=True, check_dependency=False),
            check_enforced(report=True, check_dependency=False),
        )
    if target not in checks:
        print("usage: mfa-check.py [password-only|secret|generator|enforced|all]")
        return 1
    return checks[target]()

if __name__ == "__main__":
    raise SystemExit(main())

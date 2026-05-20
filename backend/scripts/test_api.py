"""Test auth endpoints (API must be running). Usage: python scripts/test_api.py"""

import sys

import httpx

BASE = "http://127.0.0.1:8000"


def main() -> int:
    print("Testing EduSpark API at", BASE)

    try:
        r = httpx.get(f"{BASE}/health", timeout=10)
        r.raise_for_status()
        print("[health]", r.json())
    except Exception as exc:
        print("[health] FAILED — is uvicorn running?", exc)
        return 1

    for email, password, role in [
        ("teacher@eduspark.sy", "teacher123", "teacher"),
        ("student@eduspark.sy", "student123", "student"),
    ]:
        r = httpx.post(
            f"{BASE}/api/auth/login",
            json={"email": email, "password": password},
            timeout=15,
        )
        if r.status_code != 200:
            print(f"[login {role}] FAILED", r.status_code, r.text)
            return 1
        data = r.json()
        print(f"[login {role}] OK — token received for", data["user"]["name"])

    print("\nAll auth checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

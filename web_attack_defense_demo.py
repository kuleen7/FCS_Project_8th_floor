"""
Demonstration script for common web attack defenses.
"""

import requests

BASE_URL = "http://localhost:8000"


def check_security_headers():
    res = requests.get(f"{BASE_URL}/api/health", timeout=10)
    print("Health status:", res.status_code)
    for header in [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "X-XSS-Protection",
        "Content-Security-Policy",
    ]:
        print(f"{header}: {res.headers.get(header)}")


def test_attack_pattern_block():
    res = requests.get(f"{BASE_URL}/api/jobs/search?q=' OR 1=1 --", timeout=10)
    print("SQLi-like query blocked:", res.status_code, res.text[:120])


def test_rate_limit():
    endpoint = f"{BASE_URL}/api/health"
    code = None
    for _ in range(130):
        r = requests.get(endpoint, timeout=10)
        code = r.status_code
        if code == 429:
            break
    print("Rate limit response code:", code)


if __name__ == "__main__":
    print("=== Security Headers ===")
    check_security_headers()
    print("\n=== Attack Pattern Block ===")
    test_attack_pattern_block()
    print("\n=== Rate Limit Test ===")
    test_rate_limit()

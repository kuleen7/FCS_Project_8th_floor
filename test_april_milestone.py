"""
Quick smoke test for April milestone APIs.
Run after logging in and replacing TOKEN.
"""

import requests

BASE_URL = "http://localhost:8000"
TOKEN = "REPLACE_WITH_VALID_JWT"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def run():
    r = requests.post(f"{BASE_URL}/api/april/otp/keyboard-challenge", headers=HEADERS, timeout=10)
    print("keyboard challenge:", r.status_code, r.text[:120])

    r = requests.post(f"{BASE_URL}/api/april/pki/keys/rotate", headers=HEADERS, timeout=10)
    print("rotate keys:", r.status_code, r.text[:120])

    payload = {"data": {"action": "demo", "resource": "application"}}
    r = requests.post(f"{BASE_URL}/api/april/pki/sign", headers=HEADERS, json=payload, timeout=10)
    print("sign:", r.status_code, r.text[:120])
    if r.status_code == 200:
        signature = r.json().get("signature_b64")
        verify_payload = {
            "data": payload["data"],
            "signature_b64": signature,
        }
        r2 = requests.post(f"{BASE_URL}/api/april/pki/verify", headers=HEADERS, json=verify_payload, timeout=10)
        print("verify:", r2.status_code, r2.text[:120])

    block_payload = {"event_type": "milestone_test", "payload": {"module": "april"}}
    r = requests.post(f"{BASE_URL}/api/april/audit/block", headers=HEADERS, json=block_payload, timeout=10)
    print("append block:", r.status_code, r.text[:120])


if __name__ == "__main__":
    run()

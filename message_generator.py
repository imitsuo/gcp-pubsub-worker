from base64 import b64encode
import json


def generate_message(message: dict) -> dict:
    contentb64 = b64encode(json.dumps(
        message).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": {
            "data": contentb64
        }
    }

    return payload


if __name__ == "__main__":
    message = {
        "type": "new-order",
        "data": {
            "id": "",
            "status": "created"
        }
    }

    payload = generate_message(message)
    print(json.dumps(payload))

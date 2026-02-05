import base64
import hashlib

from ecdsa import VerifyingKey, NIST256p, ellipticcurve
from ecdsa.util import string_to_number, sigdecode_string
from fastapi import APIRouter, status, HTTPException

from core import SonolusRequest
from helpers.models.sonolus.account import ServerAuthenticateExternalRequest

from datetime import timedelta
import time

router = APIRouter()

# https://wiki.sonolus.com/custom-server-specs/headers/sonolus-signature
JWK = {
    "key_ops": ["verify"],
    "ext": True,
    "kty": "EC",
    "x": "d2B14ZAn-zDsqY42rHofst8rw3XB90-a5lT80NFdXo0",
    "y": "Hxzi9DHrlJ4CVSJVRnydxFWBZAgkFxZXbyxPSa8SJQw",
    "crv": "P-256",
}
del JWK["ext"]
del JWK["key_ops"]


def load_public_key(jwk_dict):
    x = base64.urlsafe_b64decode(jwk_dict["x"] + "==")
    y = base64.urlsafe_b64decode(jwk_dict["y"] + "==")

    x_int = string_to_number(x)
    y_int = string_to_number(y)

    curve = NIST256p
    point = ellipticcurve.Point(curve.curve, x_int, y_int)

    pub_key = VerifyingKey.from_public_point(point, curve=curve)
    return pub_key


@router.post("")
async def main(request: SonolusRequest, data: ServerAuthenticateExternalRequest):
    """
    We support a maximum of 6 sessions:
    - 3 external (eg. website)
    - 3 in-game

    This route will replace any expired or nonexistent session.

    If all sessions are not expired, we replace the OLDEST session.
    """
    id = request.query_params.get("id")
    if not id:
        raise HTTPException(status_code=400, detail="Missing id.")

    signature = request.headers.get("Sonolus-Signature")
    if signature is None:
        raise HTTPException(status_code=400, detail="Missing Sonolus-Signature header")
    public_key = (
        request.app.sono_pub_key if hasattr(request.app, "sono_pub_key") else None
    )
    if not public_key:
        request.app.sono_pub_key = load_public_key(JWK)
        public_key = request.app.sono_pub_key

    # Verify the signature
    decoded_signature = base64.urlsafe_b64decode(signature)
    body = await request.body()
    try:
        public_key.verify(
            decoded_signature,
            body,
            hashfunc=hashlib.sha256,
            sigdecode=sigdecode_string,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )

    TIME_WINDOW = timedelta(minutes=5)
    if data.type != "authenticateExternal":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if (
        data.url != request.app.base_url + f"/sonolus/authenticate_external?id={id}"
        and not request.app.debug
    ):
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Are you using the right website?",
        )
    current_time = round(time.time() * 1000)  # Current time in milliseconds (epoch)
    if (
        abs(current_time - data.time) > TIME_WINDOW.total_seconds() * 1000
        and not request.app.debug
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time. Please click 'Cancel' and try again.",
        )

    response = await request.app.api.authenticate_external(data.userProfile, id).send()

    if response.status != 200:
        raise HTTPException(
            status_code=response.status, detail="We're not sure what went wrong!"
        )

    return {"message": "Success. Return to the browser."}

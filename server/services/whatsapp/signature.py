"""YCloud webhook signature verification."""

import hmac
import hashlib
from typing import Optional

from ...logging_config import logger


def verify_ycloud_signature(
    payload: str,
    signature_header: str,
    secret: str,
) -> bool:
    """Verify YCloud webhook signature.

    Args:
        payload: Raw request body as string
        signature_header: Value of YCloud-Signature header (format: t={timestamp},s={signature})
        secret: Webhook secret from YCloud

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature_header:
        logger.warning("Missing YCloud-Signature header")
        return False

    try:
        parts = signature_header.split(",")
        timestamp = None
        signature = None

        for part in parts:
            if part.startswith("t="):
                timestamp = part[2:]
            elif part.startswith("s="):
                signature = part[2:]

        if not timestamp or not signature:
            logger.warning("Invalid YCloud-Signature format")
            return False

        signed_payload = f"{timestamp}.{payload}"

        expected_signature = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        is_valid = hmac.compare_digest(signature, expected_signature)

        if not is_valid:
            # Try without the whsec_ prefix
            if secret.startswith("whsec_"):
                secret_no_prefix = secret[6:]
                expected_signature_no_prefix = hmac.new(
                    secret_no_prefix.encode("utf-8"),
                    signed_payload.encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest()
                is_valid = hmac.compare_digest(signature, expected_signature_no_prefix)

        if not is_valid:
            logger.warning("YCloud signature verification failed")

        return is_valid

    except Exception as exc:
        logger.error("Error verifying YCloud signature", extra={"error": str(exc)})
        return False

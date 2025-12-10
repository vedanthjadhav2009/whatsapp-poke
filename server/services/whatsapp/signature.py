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
        logger.info(f"Verifying signature with header: {signature_header}")

        parts = signature_header.split(",")
        timestamp = None
        signature = None

        for part in parts:
            if part.startswith("t="):
                timestamp = part[2:]
            elif part.startswith("s="):
                signature = part[2:]

        if not timestamp or not signature:
            logger.warning(f"Invalid YCloud-Signature format. timestamp={timestamp}, signature={signature}")
            return False

        logger.info(f"Extracted timestamp: {timestamp}, signature: {signature[:20] if signature else 'None'}...")

        signed_payload = f"{timestamp}.{payload}"
        logger.info(f"Signed payload (first 100 chars): {signed_payload[:100]}...")

        expected_signature = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        logger.info(f"Expected signature: {expected_signature[:20]}...")
        logger.info(f"Received signature: {signature[:20] if signature else 'None'}...")

        is_valid = hmac.compare_digest(signature, expected_signature)

        if not is_valid:
            logger.warning("YCloud signature verification failed")
            # Try without the whsec_ prefix
            if secret.startswith("whsec_"):
                secret_no_prefix = secret[6:]
                expected_signature_no_prefix = hmac.new(
                    secret_no_prefix.encode("utf-8"),
                    signed_payload.encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest()
                logger.info(f"Trying without whsec_ prefix, signature: {expected_signature_no_prefix[:20]}...")
                is_valid = hmac.compare_digest(signature, expected_signature_no_prefix)
                if is_valid:
                    logger.info("Signature valid without whsec_ prefix!")

        return is_valid

    except Exception as exc:
        logger.error("Error verifying YCloud signature", extra={"error": str(exc)})
        return False

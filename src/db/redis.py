import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY = 3600
token_blocklist = redis.from_url(Config.REDIS_URL)
verify_client = redis.from_url(Config.REDIS_URL)

async def add_token_to_blocklist(jti: str) -> None:
    
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    
    jti = await token_blocklist.get(jti)

    return jti is not None

# --- Email verification methods ---
async def save_email_verification_token(email: str, token: str, expiry: int = 86400) -> None:
    """Saves the email verification token with a given expiry (default 24h)."""
    redis_key = f"verify:{email}"
    await verify_client.set(redis_key, token, ex=expiry)

async def get_email_verification_token(email: str) -> str | None:
    """Retrieves the verification token for an email, if it exists."""
    redis_key = f"verify:{email}"
    return await verify_client.get(redis_key)

async def delete_email_verification_token(email: str) -> None:
    """Deletes the verification token after successful verification."""
    redis_key = f"verify:{email}"
    await verify_client.delete(redis_key)
"""
安全模块：Token 认证。
"""
from fastapi import Header, HTTPException
from backend.core.config import settings

async def verify_token(authorization: str = Header(None)):
    """
    管理员接口 Token 认证。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    # 简单 Bearer Token 校验
    token = authorization.replace("Bearer ", "")
    if token != settings.APP_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid token")
    return True
import os
from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Optional



SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def raise_unauthoraized():
    return HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Token expired",
            headers= {"WWW-Authenticate": "Bearer"}
        )

def raise_expired_token():
    return HTTPException (
       status_code= status.HTTP_401_UNAUTHORIZED,
       detail="Token Expired",
       headers= {"WWW-Authenticate": "Bearer"}
   )
    
def raise_forbidden():
    return HTTPException (
       status_code= status.HTTP_403_UNAUTHORIZED,
       detail="Permission denied"
   )    

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(tz = timezone.utc) + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key= SECRET_KEY, algorithms=[ALGORITHM])
    return payload

async def get_current_user(token: str = Depends(oauth2_scheme)):
    
    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")
        username: Optional[str] = payload.get("username")
        if not sub or not username:
            raise raise_unauthoraized
        return {"email": sub, "username": username}
    
    except ExpiredSignatureError:
        raise raise_unauthoraized
    
    except InvalidTokenError:
        raise raise_expired_token
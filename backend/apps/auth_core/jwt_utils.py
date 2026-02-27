from __future__ import annotations

import datetime as dt
import uuid
from typing import Any, Dict, Tuple

import jwt
from django.conf import settings


ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME_MINUTES = 30


def create_access_token(user_id: int) -> Tuple[str, str, dt.datetime]:
    """Создать access JWT-токен с полями user_id, exp и jti.

    Возвращает кортеж (token, jti, exp).
    """
    now = dt.datetime.now(dt.timezone.utc)
    exp = now + dt.timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    jti = uuid.uuid4().hex
    payload: Dict[str, Any] = {
        "user_id": user_id,
        "jti": jti,
        "exp": exp,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, exp


def decode_token(token: str) -> Dict[str, Any]:
    """Декодировать и провалидировать JWT-токен.

    Выбрасывает jwt.InvalidTokenError при невалидной подписи или истёкшем сроке.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])

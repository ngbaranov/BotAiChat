from __future__ import annotations
from typing import Optional

from _curses import raw

from app.service.file_extension import CANDIDATE_ENCODINGS, TEXT_EXTS

# Минимум зависимостей: без chardet. Пытаемся несколькими кодировками.
def is_text_filename(name: str) -> bool:
    """
    Проверяем, есть ли расширения для работы файла
    :param name:
    :return:
    """
    if not name:
            return False
    name = name.lower()
    return any(name.endswith(ext) for ext in TEXT_EXTS)

def _safe_decode(raw: bytes) -> str:
    for enc in CANDIDATE_ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")

def read_text_file(path: str, max_chars: Optional[int] = None, prefer_tail: bool = False) -> str:
    """
    Читает текстовый файл (код/логи/конфиги и т.п.).
    prefer_tail=True — полезно для .log (берём хвост).
    """
    with open(path, "rb") as f:
        raw = f.read()

    text = _safe_decode(raw).strip()

    if max_chars and max_chars > 0 and len(text) > max_chars:
        if prefer_tail:
            text = text[-max_chars:]
        else:
            text = text[:max_chars]
    return text

def should_prefer_tail_by_ext(filename: str | None) -> bool:
    name = (filename or "").lower()
    return name.endswith((".log", ".out", ".err"))

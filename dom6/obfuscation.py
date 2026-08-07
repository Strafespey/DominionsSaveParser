"""Dominions 6 string obfuscation.

Every text string in a Dominions 6 savegame is stored XOR'd byte-by-byte with
the constant 0x4F, and NUL-terminated (the terminator itself is stored as 0x4F,
i.e. 0x00 ^ 0x4F).

Numeric fields are NOT obfuscated -- they are plain little-endian integers.
So you must never XOR a whole save file; XOR only while reading a string field.
"""

XOR_KEY = 0x4F

# Handy constants when eyeballing hexdumps.
RAW_NUL_IN_STRING = 0x4F  # a 0x4F byte inside a string region is a terminator
RAW_SPACE = 0x6F  # 0x20 ^ 0x4F


def deobfuscate(data: bytes) -> bytes:
    """XOR a buffer with the string key. Involutive: f(f(x)) == x."""
    return bytes(b ^ XOR_KEY for b in data)


obfuscate = deobfuscate  # the operation is its own inverse


def read_cstring(data: bytes, offset: int, max_len: int = 4096) -> tuple[str, int]:
    """Read one obfuscated NUL-terminated string.

    Returns (text, offset_just_past_terminator).
    """
    end = data.find(bytes([XOR_KEY]), offset, offset + max_len)
    if end < 0:
        raise ValueError(
            f"unterminated obfuscated string at 0x{offset:x} "
            f"(no 0x{XOR_KEY:02x} within {max_len} bytes)"
        )
    text = deobfuscate(data[offset:end]).decode("utf-8", errors="replace")
    return text, end + 1


def looks_like_text(data: bytes, offset: int, min_len: int = 3) -> bool:
    """Cheap probe: does an obfuscated, printable run start here?

    Note the trap this guards against: a run of 0x00 padding bytes decodes to
    'OOOO...' and a run of 0xFF decodes to a printable char too, so a naive
    printability test reports text almost everywhere in a Dominions save.
    A window made up *entirely* of padding bytes is rejected.
    """
    window = data[offset : offset + min_len]
    if len(window) < min_len:
        return False
    if all(not (0x20 <= (b ^ XOR_KEY) < 0x7F) for b in window[:1]):
        return False
    for b in window:
        if not (0x20 <= (b ^ XOR_KEY) < 0x7F):
            return False
    # Reject pure padding (all 0x00, or all 0xFF).
    if all(b == window[0] for b in window) and window[0] in (0x00, 0xFF):
        return False
    return True

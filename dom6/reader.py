"""Little-endian binary cursor for Dominions 6 save files."""

from __future__ import annotations

import struct

from .obfuscation import read_cstring


class Cursor:
    """A seekable little-endian reader with Dominions string support."""

    def __init__(self, data: bytes, pos: int = 0):
        self.data = data
        self.pos = pos

    # -- primitives ---------------------------------------------------
    def _unpack(self, fmt: str, size: int):
        if self.pos + size > len(self.data):
            raise EOFError(
                f"read of {size} bytes at 0x{self.pos:x} runs past "
                f"end of buffer (0x{len(self.data):x})"
            )
        (value,) = struct.unpack_from(fmt, self.data, self.pos)
        self.pos += size
        return value

    def u8(self) -> int:
        return self._unpack("<B", 1)

    def i8(self) -> int:
        return self._unpack("<b", 1)

    def u16(self) -> int:
        return self._unpack("<H", 2)

    def i16(self) -> int:
        return self._unpack("<h", 2)

    def u32(self) -> int:
        return self._unpack("<I", 4)

    def i32(self) -> int:
        return self._unpack("<i", 4)

    def i64(self) -> int:
        return self._unpack("<q", 8)

    def raw(self, n: int) -> bytes:
        if self.pos + n > len(self.data):
            raise EOFError(f"read of {n} bytes at 0x{self.pos:x} runs past end")
        out = self.data[self.pos : self.pos + n]
        self.pos += n
        return out

    def string(self) -> str:
        """Read one XOR-0x4F obfuscated, NUL-terminated string."""
        text, self.pos = read_cstring(self.data, self.pos)
        return text

    def float_dom(self) -> float:
        """Illwinter's split float: unsigned short fraction, then int integer part.

        Documented for the .d6m format in dom6fileformats.pdf.
        """
        frac = self.u16()
        whole = self.i32()
        return whole + frac / 65536.0

    # -- navigation ---------------------------------------------------
    def seek(self, pos: int) -> "Cursor":
        self.pos = pos
        return self

    def skip(self, n: int) -> "Cursor":
        self.pos += n
        return self

    def tell(self) -> int:
        return self.pos

    @property
    def remaining(self) -> int:
        return len(self.data) - self.pos

    def peek(self, n: int = 16) -> bytes:
        return self.data[self.pos : self.pos + n]

    def peek_i32s(self, count: int = 8) -> list[int]:
        """Non-advancing look at the next `count` int32s -- for exploration."""
        n = min(count, max(0, (len(self.data) - self.pos) // 4))
        return list(struct.unpack_from(f"<{n}i", self.data, self.pos))

    def hexdump(self, length: int = 64, base: int | None = None) -> str:
        base = self.pos if base is None else base
        lines = []
        for off in range(0, length, 16):
            chunk = self.data[base + off : base + off + 16]
            if not chunk:
                break
            hexs = " ".join(f"{b:02x}" for b in chunk)
            asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            dec = "".join(
                chr(b ^ 0x4F) if 32 <= (b ^ 0x4F) < 127 else "." for b in chunk
            )
            lines.append(f"{base + off:08x}  {hexs:<47}  |{asc}|  x4F:|{dec}|")
        return "\n".join(lines)

def to_bytes_ascii(msg: str) -> bytes:
    return msg.encode("ascii", errors="strict")

def bytes_to_hex(b: bytes) -> str:
    return b.hex()

def bytes_to_bitstring(b: bytes) -> str:
    return "".join(f"{byte:08b}" for byte in b)

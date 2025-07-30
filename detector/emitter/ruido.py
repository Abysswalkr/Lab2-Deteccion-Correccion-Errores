import random

def apply_ber(frame: bytes, p: float) -> tuple[bytes, list[int]]:
    if p <= 0.0:
        return frame, []
    out = bytearray(frame)
    flipped = []
    total_bits = len(frame) * 8
    for bit_idx in range(total_bits):
        if random.random() < p:
            byte_idx = bit_idx // 8
            bit_in_byte = bit_idx % 8
            out[byte_idx] ^= (1 << bit_in_byte)
            flipped.append(bit_idx)
    return bytes(out), flipped

def apply_manual_flips(frame: bytes, bit_indices: list[int]) -> tuple[bytes, list[int]]:
    if not bit_indices:
        return frame, []
    out = bytearray(frame)
    total_bits = len(frame) * 8
    flips_done = []
    for idx in bit_indices:
        if 0 <= idx < total_bits:
            out[idx // 8] ^= (1 << (idx % 8))
            flips_done.append(idx)
    return bytes(out), flips_done

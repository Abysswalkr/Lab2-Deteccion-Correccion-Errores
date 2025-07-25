# detector/emitter/ruido.py
import random

def apply_ber(frame: bytes, p: float) -> tuple[bytes, list[int]]:
    """
    Aplica ruido bit a bit con probabilidad p.
    Retorna (frame_mutado, indices_de_bits_volteados).
    """
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

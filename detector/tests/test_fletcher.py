import pytest
import random
from detector.fletcher.emisor import emisor_fletcher
from detector.fletcher.receptor import verificar_fletcher

# Mensajes con longitudes distintas
MESSAGES = [b"A", b"ABCDE", b"Lorem ipsum"]    # 1, 5 y 11 bytes
BLOCK_SIZES = [8, 16, 32]


def flip_bits(data: bytes, bit_indices: list[int]) -> bytes:
    """Invierte los bits indicados (índices absolutos) y devuelve una copia mutada."""
    out = bytearray(data)
    for idx in bit_indices:
        byte_idx = idx // 8
        bit_idx = idx % 8
        out[byte_idx] ^= 1 << bit_idx
    return bytes(out)


# ----------------------------- SIN ERRORES -----------------------------
@pytest.mark.parametrize("msg", MESSAGES)
@pytest.mark.parametrize("block", BLOCK_SIZES)
def test_no_error(msg: bytes, block: int):
    frame = emisor_fletcher(msg, block)
    ok, original = verificar_fletcher(frame, block)
    assert ok is True
    assert original == msg


# ---------------------------- 1 BIT DE ERROR ---------------------------
@pytest.mark.parametrize("msg", MESSAGES)
@pytest.mark.parametrize("block", BLOCK_SIZES)
def test_one_bit_error(msg: bytes, block: int):
    frame = emisor_fletcher(msg, block)
    bit_to_flip = random.randrange(len(frame) * 8)
    corrupted = flip_bits(frame, [bit_to_flip])
    ok, _ = verificar_fletcher(corrupted, block)
    assert ok is False


# --------------------------- ≥2 ERRORES -------------------------------
@pytest.mark.parametrize("msg", MESSAGES)
@pytest.mark.parametrize("block", BLOCK_SIZES)
def test_two_bits_error(msg: bytes, block: int):
    frame = emisor_fletcher(msg, block)
    bits = random.sample(range(len(frame) * 8), k=2)
    corrupted = flip_bits(frame, bits)
    ok, _ = verificar_fletcher(corrupted, block)
    assert ok is False

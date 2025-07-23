# detector/tests/test_fletcher_cross.py

import pytest, random, subprocess, json
from detector.fletcher import emisor_fletcher

MESSAGES = [b"A", b"ABCDE", b"Lorem ipsum"]
BLOCK_SIZES = [8, 16, 32]

def flip_bits(data: bytes, bit_indices: list[int]) -> bytes:
    """Invierte los bits indicados (índices absolutos) y devuelve la copia mutada."""
    out = bytearray(data)
    for idx in bit_indices:
        byte_idx = idx // 8
        bit_idx = idx % 8
        out[byte_idx] ^= 1 << bit_idx
    return bytes(out)

def call_js_receiver(frame: bytes, block: int):
    hex_frame = frame.hex()
    proc = subprocess.run(
        ["node", "detector/fletcher/receptor.js", str(block), hex_frame],
        capture_output=True, text=True, check=True
    )
    return json.loads(proc.stdout)

@pytest.mark.parametrize("msg", MESSAGES)
@pytest.mark.parametrize("block", BLOCK_SIZES)
def test_cross_no_error(msg, block):
    frame = emisor_fletcher(msg, block)
    out = call_js_receiver(frame, block)
    assert out["ok"] is True
    assert bytes.fromhex(out["original"]) == msg

@pytest.mark.parametrize("msg", MESSAGES)
@pytest.mark.parametrize("block", BLOCK_SIZES)
def test_cross_one_bit_error(msg, block):
    frame = emisor_fletcher(msg, block)
    bit_to_flip = random.randrange(len(frame) * 8)
    corrupted = flip_bits(frame, [bit_to_flip])
    out = call_js_receiver(corrupted, block)
    assert out["ok"] is False

@pytest.mark.parametrize("msg", MESSAGES)
@pytest.mark.parametrize("block", BLOCK_SIZES)
def test_cross_two_bits_error(msg, block):
    frame = emisor_fletcher(msg, block)
    bits = random.sample(range(len(frame) * 8), k=2)
    corrupted = flip_bits(frame, bits)
    out = call_js_receiver(corrupted, block)
    assert out["ok"] is False

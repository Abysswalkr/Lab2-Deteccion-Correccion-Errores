# Emisor para Fletcher Checksum. Soporta bloques de 8, 16 y 32 bits (configurable).

from .constants import ALLOWED_BLOCK_SIZES, DEFAULT_BLOCK_SIZE


def pad_data(data: bytes, block_size: int) -> bytes:
    """
    Añade bytes 0x00 al final hasta que len(data) sea múltiplo de block_size/8.
    """
    byte_block = block_size // 8
    rem = len(data) % byte_block
    if rem:
        padding = byte_block - rem
        data += bytes(padding)
    return data


def calcular_fletcher(
    data: bytes,
    block_size: int = DEFAULT_BLOCK_SIZE,
) -> tuple[int, int]:
    """
    Calcula las sumas de Fletcher (sum1, sum2) para el bloque dado.
    """
    if block_size not in ALLOWED_BLOCK_SIZES:
        raise ValueError(f"block_size debe ser uno de {ALLOWED_BLOCK_SIZES}")

    # 1. Padding para alinear al tamaño de bloque
    data = pad_data(data, block_size)

    modulo = (1 << block_size) - 1
    byte_block = block_size // 8
    sum1 = 0
    sum2 = 0

    # 2. Procesar bloque por bloque
    for i in range(0, len(data), byte_block):
        block = int.from_bytes(data[i : i + byte_block], "big")
        sum1 = (sum1 + block) % modulo
        sum2 = (sum2 + sum1) % modulo

    return sum1, sum2


def emisor_fletcher(
    data: bytes,
    block_size: int = DEFAULT_BLOCK_SIZE,
) -> bytes:
    """
    Construye la trama para transmitir:
        data_original ‖ sum1 ‖ sum2 y se codifican en block_size/8 bytes cada uno (big‑endian).
    """
    # 1. Calcular las dos sumas
    sum1, sum2 = calcular_fletcher(data, block_size)

    # 2. Convertirlas a bytes del tamaño adecuado
    byte_block = block_size // 8
    checksum_bytes = sum1.to_bytes(byte_block, "big") + sum2.to_bytes(
        byte_block, "big"
    )

    # 3. Concatenar datos + checksum y devolver
    return data + checksum_bytes

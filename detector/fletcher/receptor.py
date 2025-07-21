#Receptor para el algoritmo Fletcher Checksum con bloques configurables de 8, 16 o 32 bits.

from .constants import ALLOWED_BLOCK_SIZES, DEFAULT_BLOCK_SIZE
from .emisor import pad_data, calcular_fletcher


def verificar_fletcher(
    frame: bytes,
    block_size: int = DEFAULT_BLOCK_SIZE,
) -> tuple[bool, bytes]:

    # 1. Validación de tamaño de bloque
    if block_size not in ALLOWED_BLOCK_SIZES:
        raise ValueError(f"block_size debe ser uno de {ALLOWED_BLOCK_SIZES}")

    byte_block = block_size // 8
    checksum_len = 2 * byte_block

    # 2. Verificar que la trama traiga al menos los checksum
    if len(frame) < checksum_len:
        return False, b""

    # 3. Separar data y checksum
    data_part = frame[:-checksum_len]
    checksum_part = frame[-checksum_len:]

    # 4. Recalcular sumas sobre la data (con padding idéntico al emisor)
    sum1, sum2 = calcular_fletcher(data_part, block_size)
    expected_checksum = sum1.to_bytes(byte_block, "big") + sum2.to_bytes(
        byte_block, "big"
    )

    # 5. Comparar y devolver resultado
    if checksum_part == expected_checksum:
        original = data_part.rstrip(b"\x00")
        return True, original

    return False, b""

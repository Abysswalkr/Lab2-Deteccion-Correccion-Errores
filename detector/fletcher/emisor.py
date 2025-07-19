from .constants import MODULO

def calcular_fletcher(data: bytes) -> tuple[int, int]:
    """
    Calcula las dos sumas de Fletcher-16 sobre `data`.
    """
    sum1 = 0
    sum2 = 0
    for byte in data:
        sum1 = (sum1 + byte) % MODULO
        sum2 = (sum2 + sum1) % MODULO
    return sum1, sum2


def emisor_fletcher(data: bytes) -> bytes:
    """
    Emisor: construye la trama final agregando al final
    los dos bytes de checksum.
    """
    s1, s2 = calcular_fletcher(data)

    return data + bytes([s1, s2])
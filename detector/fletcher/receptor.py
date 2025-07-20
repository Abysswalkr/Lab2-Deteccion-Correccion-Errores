from .constants import MODULO
from .emisor import calcular_fletcher

def verificar_fletcher(frame: bytes) -> bool:
    """
    Receptor: recibe la trama completa (datos + 2 bytes checksum).
    """

    if len(frame) < 2:
        return False
    data, checksum = frame[:-2], frame[-2:]
    s1, s2 = calcular_fletcher(data)
    return checksum[0] == s1 and checksum[1] == s2
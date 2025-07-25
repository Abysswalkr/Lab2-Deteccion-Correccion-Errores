# detector/emitter/enlace.py
from detector.fletcher import emisor_fletcher

def build_frame_fletcher(data: bytes, block_size: int) -> bytes:
    """
    Devuelve la trama data ‖ sum1 ‖ sum2
    """
    return emisor_fletcher(data, block_size)

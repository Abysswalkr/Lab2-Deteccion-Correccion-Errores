import socket
import json
from typing import Optional

def send_over_tcp(host: str, port: int, alg: str, block_size: int, frame: bytes) -> Optional[dict]:
    """
    Envía un JSON por TCP (terminado en '\n') y espera una única línea de respuesta en JSON.
    """
    payload = {
        "alg": alg,
        "block_size": block_size,
        "frame_hex": frame.hex(),
    }
    data = (json.dumps(payload) + "\n").encode("utf-8")

    with socket.create_connection((host, port), timeout=10) as s:
        s.sendall(data)
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk

    if not buf:
        return None
    return json.loads(buf.decode("utf-8").rstrip("\n"))

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

class JsonlClient:
    """
    Cliente TCP persistente (JSON por línea).
    Uso:
        with JsonlClient(host, port) as cli:
            resp = cli.send({"alg": "fletcher", ...})
    """
    def __init__(self, host: str, port: int, timeout: float = 10.0):
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._buf = b""

    def _recv_line(self) -> str:
        while b"\n" not in self._buf:
            chunk = self._sock.recv(4096)
            if not chunk:
                break
            self._buf += chunk
        line, _, rest = self._buf.partition(b"\n")
        self._buf = rest
        return line.decode("utf-8")

    def send(self, obj: dict) -> dict:
        data = (json.dumps(obj) + "\n").encode("utf-8")
        self._sock.sendall(data)
        line = self._recv_line()
        if not line:
            return {}
        return json.loads(line)

    def close(self):
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        finally:
            self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

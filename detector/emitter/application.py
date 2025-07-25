# detector/emitter/application.py
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Emisor por capas (Aplicación, Presentación, Enlace, Ruido)"
    )
    parser.add_argument("--msg", required=True, help="Mensaje a enviar (texto)")
    parser.add_argument("--alg", default="fletcher", choices=["fletcher"],
                        help="Algoritmo de integridad (por ahora: fletcher)")
    parser.add_argument("--block-size", type=int, default=8, choices=[8, 16, 32],
                        help="Tamaño de bloque en bits para Fletcher")
    parser.add_argument("--ber", type=float, default=0.0,
                        help="Probabilidad de error por bit (ruido)")
    return parser.parse_args()

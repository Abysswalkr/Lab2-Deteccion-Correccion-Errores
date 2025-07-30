from .application import parse_args
from .presentation import to_bytes_ascii, bytes_to_hex, bytes_to_bitstring
from .enlace import build_frame_fletcher
from .ruido import apply_ber, apply_manual_flips
from .transmision import send_over_tcp

def main():
    args = parse_args()

    print("=== CAPA APLICACIÓN ===")
    print(f"Mensaje: {args.msg}")
    print(f"Algoritmo: {args.alg}")
    print(f"Block size: {args.block_size} bits")
    print(f"BER (ruido): {args.ber}\n")

    print("=== CAPA PRESENTACIÓN ===")
    data_bytes = to_bytes_ascii(args.msg)
    print(f"ASCII bytes (hex): {bytes_to_hex(data_bytes)}")
    print(f"ASCII bits: {bytes_to_bitstring(data_bytes)}\n")

    print("=== CAPA ENLACE ===")
    if args.alg == "fletcher":
        frame = build_frame_fletcher(data_bytes, args.block_size)
    else:
        raise NotImplementedError("Solo fletcher está implementado en esta entrega.")
    print(f"Trama emitida (hex): {bytes_to_hex(frame)}")
    print(f"Trama emitida (bits): {bytes_to_bitstring(frame)}\n")

    print("=== CAPA RUIDO (EMISOR) ===")
    flip_bits_list = [int(x) for x in args.flip_bits.split(",") if x.strip().isdigit()]
    if flip_bits_list:
        noisy_frame, flipped = apply_manual_flips(frame, flip_bits_list)
        print(f"(Modo manual) Bits a voltear (entrada): {flip_bits_list}")
    else:
        noisy_frame, flipped = apply_ber(frame, args.ber)

    print(f"Trama con ruido (hex): {bytes_to_hex(noisy_frame)}")
    print(f"Bits volteados: {flipped if flipped else 'Ninguno'}")
    print(f"Total bits volteados: {len(flipped)}\n")

    print("=== CAPA TRANSMISIÓN (TCP) ===")
    print(f"Destino: {args.send_host}:{args.send_port}")
    try:
        if args.send_host and args.send_port:
            response = send_over_tcp(args.send_host, args.send_port, args.alg, args.block_size, noisy_frame)
            print("Respuesta receptor (JSON):", response)
        else:
            print("Flags --send-host/--send-port no proporcionados; no se envía.")
    except Exception as e:
        import traceback
        print("Error de transmisión:", e)
        traceback.print_exc()

    print("=== RESUMEN ===")
    print("Original (hex):", bytes_to_hex(frame))
    print("Con ruido (hex):", bytes_to_hex(noisy_frame))

if __name__ == "__main__":
    main()

import socket
import json
import sys
import argparse

def obtener_posiciones_paridad(longitud_trama):
    posiciones = []
    potencia = 1
    while potencia <= longitud_trama:
        posiciones.append(potencia)
        potencia *= 2
    return posiciones

def calcular_bit_paridad(trama_lista, posicion_paridad, longitud_trama):
    paridad = 0
    
    for pos in range(1, longitud_trama + 1):
        if pos & posicion_paridad:
            paridad ^= trama_lista[pos - 1]
    
    return paridad

def extraer_datos_originales(trama_lista, posiciones_paridad):
    datos = []
    for i in range(len(trama_lista)):
        pos_actual = i + 1
        if pos_actual not in posiciones_paridad:
            datos.append(str(trama_lista[i]))
    
    return ''.join(datos)

def procesar_bloque_hamming_74(bloque_7bits):
    """
    Procesa un bloque individual de Hamming(7,4).
    Estructura: p1 p2 d0 p3 d1 d2 d3 (posiciones 1,2,3,4,5,6,7)
    Retorna: {ok, error_detected, corrected, syndrome, position, data_bits}
    """
    if len(bloque_7bits) != 7:
        return {
            'ok': False, 'error_detected': False, 'corrected': False,
            'syndrome': 0, 'position': None, 'data_bits': ''
        }
    
    bits = [int(b) for b in bloque_7bits]
    p1, p2, d0, p3, d1, d2, d3 = bits
    
    # Calcular síndrome según Hamming(7,4)
    s1 = p1 ^ d0 ^ d1 ^ d3  # paridad de posiciones 1,3,5,7
    s2 = p2 ^ d0 ^ d2 ^ d3  # paridad de posiciones 2,3,6,7  
    s3 = p3 ^ d1 ^ d2 ^ d3  # paridad de posiciones 4,5,6,7
    
    syndrome = s1 * 1 + s2 * 2 + s3 * 4
    
    resultado = {
        'ok': False,
        'error_detected': syndrome != 0,
        'corrected': False,
        'syndrome': syndrome,
        'position': syndrome if syndrome > 0 else None,
        'data_bits': ''
    }
    
    if syndrome == 0:
        # Sin errores
        resultado['ok'] = True
        resultado['data_bits'] = f"{d0}{d1}{d2}{d3}"
    else:
        # Error detectado - intentar corregir
        if 1 <= syndrome <= 7:
            # Corregir el bit en la posición indicada por el síndrome
            bits_corregidos = bits.copy()
            bits_corregidos[syndrome - 1] = 1 - bits_corregidos[syndrome - 1]
            
            # Extraer datos corregidos
            _, _, d0_c, _, d1_c, d2_c, d3_c = bits_corregidos
            resultado['data_bits'] = f"{d0_c}{d1_c}{d2_c}{d3_c}"
            resultado['corrected'] = True
            resultado['ok'] = True
        else:
            # Síndrome inválido
            resultado['data_bits'] = "0000"  # datos por defecto
    
    return resultado

def receptor_hamming_multiple_blocks(trama_recibida):
    """
    Procesa múltiples bloques Hamming(7,4) como hace el emisor.
    """
    if not all(bit in '01' for bit in trama_recibida):
        raise ValueError("La entrada debe ser una cadena binaria (solo 0s y 1s)")
    
    # Dividir en bloques de 7 bits
    bloques_7 = []
    for i in range(0, len(trama_recibida), 7):
        bloque = trama_recibida[i:i+7]
        if len(bloque) == 7:  # Solo procesar bloques completos
            bloques_7.append(bloque)
        # Si el último bloque es incompleto, lo ignoramos (puede ser padding)
    
    if not bloques_7:
        return {
            'ok': False, 'error_detected': False, 'corrected': False,
            'total_errors': 0, 'blocks_processed': 0, 'syndrome': 0,
            'datos_originales': '', 'blocks_detail': []
        }
    
    # Procesar cada bloque
    total_errors = 0
    total_corrected = 0
    datos_recuperados = ''
    blocks_detail = []
    overall_ok = True
    
    for i, bloque in enumerate(bloques_7):
        resultado_bloque = procesar_bloque_hamming_74(bloque)
        
        blocks_detail.append({
            'block_num': i + 1,
            'original': bloque,
            'syndrome': resultado_bloque['syndrome'],
            'error_detected': resultado_bloque['error_detected'],
            'corrected': resultado_bloque['corrected'],
            'data_bits': resultado_bloque['data_bits']
        })
        
        if resultado_bloque['error_detected']:
            total_errors += 1
            if resultado_bloque['corrected']:
                total_corrected += 1
            else:
                overall_ok = False
        
        if resultado_bloque['ok']:
            datos_recuperados += resultado_bloque['data_bits']
        else:
            overall_ok = False
    
    return {
        'ok': overall_ok,
        'error_detected': total_errors > 0,
        'corrected': total_corrected > 0,
        'total_errors': total_errors,
        'total_corrected': total_corrected,
        'blocks_processed': len(bloques_7),
        'syndrome': sum(d['syndrome'] for d in blocks_detail),  # suma de todos los síndromes
        'datos_originales': datos_recuperados,
        'blocks_detail': blocks_detail
    }

def receptor_hamming(trama_recibida):
    """
    Función principal actualizada que usa múltiples bloques Hamming(7,4).
    """
    return receptor_hamming_multiple_blocks(trama_recibida)

def process_tcp_request(payload):
    """
    Procesa una request TCP y devuelve la respuesta en formato JSON.
    Input esperado: {"frame_hex": "1010101"}
    Output: {"ok": bool, "corrected": bool, "error_detected": bool, "syndrome": int, 
             "original_hex": "", "original_ascii": "", "total_errors": int, "blocks_processed": int}
    """
    try:
        frame_hex = payload.get("frame_hex", "")
        if not frame_hex:
            return {"ok": False, "error": "frame_hex requerido"}
        
        # Convertir hex a binario
        try:
            frame_bytes = bytes.fromhex(frame_hex)
            # Convertir bytes a string binario
            frame_binary = ''.join(format(byte, '08b') for byte in frame_bytes)
        except ValueError as e:
            return {"ok": False, "error": f"frame_hex inválido: {e}"}
        
        # Procesar con Hamming múltiples bloques
        resultado = receptor_hamming(frame_binary)
        
        # Preparar respuesta TCP
        response = {
            "ok": resultado["ok"],
            "error_detected": resultado["error_detected"],
            "corrected": resultado["corrected"],
            "syndrome": resultado["syndrome"],
            "total_errors": resultado["total_errors"],
            "total_corrected": resultado.get("total_corrected", 0),
            "blocks_processed": resultado["blocks_processed"],
            "original_hex": "",
            "original_ascii": ""
        }
        
        # Si se recuperaron datos, convertirlos de vuelta
        if resultado["ok"] and resultado["datos_originales"]:
            try:
                # Convertir datos binarios de vuelta a bytes
                datos_bin = resultado["datos_originales"]
                
                # Asegurar que sea múltiplo de 8 bits para formar bytes válidos
                if len(datos_bin) % 8 != 0:
                    # Pad con ceros a la derecha hasta completar el byte
                    datos_bin = datos_bin.ljust((len(datos_bin) + 7) // 8 * 8, '0')
                
                # Convertir a bytes
                original_bytes = bytes(int(datos_bin[i:i+8], 2) for i in range(0, len(datos_bin), 8))
                
                # Quitar bytes de padding (ceros al final)
                while original_bytes and original_bytes[-1] == 0:
                    original_bytes = original_bytes[:-1]
                
                response["original_hex"] = original_bytes.hex()
                response["original_ascii"] = original_bytes.decode('ascii', errors='ignore')
                
            except Exception as e:
                response["original_hex"] = ""
                response["original_ascii"] = ""
                response["decode_error"] = str(e)
        
        # Agregar detalles de bloques para debug (opcional)
        if "blocks_detail" in resultado:
            response["debug_blocks"] = resultado["blocks_detail"]
        
        return response
        
    except Exception as e:
        return {"ok": False, "error": str(e)}

def start_tcp_server(port):
    """
    Inicia el servidor TCP que recibe JSON por línea (JSONL).
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('0.0.0.0', port))
        server.listen(5)
        print(f"Receptor Hamming escuchando en tcp://0.0.0.0:{port}")
        
        while True:
            client, addr = server.accept()
            print(f"Conexión desde {addr}")
            
            try:
                handle_client(client)
            except Exception as e:
                print(f"Error manejando cliente {addr}: {e}")
            finally:
                client.close()
                
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
    finally:
        server.close()

def handle_client(client_socket):
    """
    Maneja un cliente TCP individual.
    Procesa líneas JSON hasta que se cierre la conexión.
    """
    buffer = ""
    
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
                
            buffer += data.decode('utf-8')
            
            # Procesar líneas completas
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if not line:
                    continue
                
                try:
                    payload = json.loads(line)
                    response = process_tcp_request(payload)
                    
                    # Log simple del resultado
                    if response.get('ok'):
                        status = "✓"
                        if response.get('error_detected'):
                            status += f" ({response.get('total_errors', 0)} errores corregidos)"
                    else:
                        status = f"✗ {response.get('error', 'error')}"
                    
                    print(f"📤 {status}")
                    
                    response_json = json.dumps(response) + '\n'
                    client_socket.send(response_json.encode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"❌ JSON inválido")
                    error_response = json.dumps({"ok": False, "error": "JSON inválido"}) + '\n'
                    client_socket.send(error_response.encode('utf-8'))
                    
        except Exception as e:
            print(f"Error: {e}")
            break

def probar_receptor():
    """Pruebas por defecto del receptor (modo standalone)"""
    tramas_prueba = [
        ("1010101", "Bloque Hamming(7,4) simple - sin errores"),  
        ("0010101", "Bloque Hamming(7,4) simple - con error en posición 2"),
        ("1001100111000011001100011001", "Múltiples bloques - sin errores"),
    ]
    
    print("=" * 60)
    print("PRUEBAS DEL RECEPTOR HAMMING (MÚLTIPLES BLOQUES)")
    print("=" * 60)
    
    for i, (trama, descripcion) in enumerate(tramas_prueba):
        try:
            print(f"\n--- PRUEBA {i + 1}: {descripcion} ---")
            resultado = receptor_hamming(trama)
            
            print(f"Trama recibida: {trama}")
            print(f"Bloques procesados: {resultado['blocks_processed']}")
            print(f"Errores detectados: {resultado['total_errors']}")
            print(f"Errores corregidos: {resultado.get('total_corrected', 0)}")
            print(f"Síndrome total: {resultado['syndrome']}")
            
            if resultado['ok']:
                print(f"✓ Procesamiento exitoso")
                print(f"✓ Datos recuperados: {resultado['datos_originales']}")
                
                # Mostrar detalles de bloques
                if 'blocks_detail' in resultado:
                    print("\n--- Detalle por bloque ---")
                    for block in resultado['blocks_detail']:
                        status = "✓" if not block['error_detected'] else ("⚠" if block['corrected'] else "✗")
                        print(f"  Bloque {block['block_num']}: {block['original']} → {block['data_bits']} {status}")
            else:
                print(f"✗ Error en el procesamiento")
                
        except Exception as error:
            print(f"Error en prueba {i + 1}: {error}")

def parse_args():
    parser = argparse.ArgumentParser(description="Receptor Hamming con soporte TCP")
    parser.add_argument("trama", nargs="?", help="Trama codificada en binario (modo standalone)")
    parser.add_argument("--tcp-port", type=int, default=None, help="Puerto TCP para modo servidor")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Modo servidor TCP
    if args.tcp_port:
        start_tcp_server(args.tcp_port)
        return
    
    # Modo standalone (como antes)
    if not args.trama:
        print("Uso: python receptor-hamming.py <trama_codificada>")
        print("     python receptor-hamming.py --tcp-port 5001")
        print("Ejemplo: python receptor-hamming.py 1010101")
        print("\nEjecutando pruebas por defecto...")
        probar_receptor()
        return
    
    try:
        resultado = receptor_hamming(args.trama)
        
        print(f"\n=== RECEPTOR HAMMING (MÚLTIPLES BLOQUES) ===")
        print(f"Trama recibida: {args.trama}")
        print(f"Bloques procesados: {resultado['blocks_processed']}")
        print(f"Errores detectados: {resultado['total_errors']}")
        print(f"Errores corregidos: {resultado.get('total_corrected', 0)}")
        print(f"Síndrome total: {resultado['syndrome']}")
        
        print(f"\n{'='*40}")
        print("RESUMEN:")
        if resultado['ok']:
            if resultado['error_detected']:
                print(f"✓ {resultado['total_errors']} error(es) detectado(s)")
                if resultado['corrected']:
                    print(f"✓ {resultado.get('total_corrected', 0)} error(es) corregido(s)")
                print(f"✓ Datos recuperados: {resultado['datos_originales']}")
            else:
                print(f"✓ Trama recibida sin errores")
                print(f"✓ Datos: {resultado['datos_originales']}")
        else:
            print(f"✗ Error en el procesamiento")
            
        # Mostrar detalles de bloques
        if 'blocks_detail' in resultado and resultado['blocks_detail']:
            print(f"\n--- Detalle por bloque ---")
            for block in resultado['blocks_detail']:
                status = "✓" if not block['error_detected'] else ("⚠" if block['corrected'] else "✗")
                print(f"  Bloque {block['block_num']}: {block['original']} → {block['data_bits']} {status}")
            
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
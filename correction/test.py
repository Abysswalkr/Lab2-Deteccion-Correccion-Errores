#!/usr/bin/env python3
"""
Test para validar el sistema Hamming cross-language.
"""

import subprocess
import json
import time
import sys
import os
import socket

def detect_working_directory():
    """Detectar si estamos en el directorio correcto"""
    current_dir = os.getcwd()
    
    # Verificar si estamos en el directorio correction o en el directorio padre
    if os.path.basename(current_dir) == "correction":
        print(f"✅ Directorio de trabajo: {current_dir}")
        return True
    elif os.path.exists("correction"):
        print(f"✅ Directorio de trabajo: {current_dir} (con subdirectorio correction)")
        return True
    else:
        print(f"❌ Directorio incorrecto: {current_dir}")
        print("   Debe ejecutarse desde el directorio correction/ o desde el directorio padre")
        return False

def find_file(filename):
    """Buscar un archivo en el directorio actual y subdirectorios"""
    current_dir = os.getcwd()
    
    # Buscar en el directorio actual
    if os.path.exists(filename):
        return os.path.abspath(filename)
    
    # Buscar en el subdirectorio correction
    correction_path = os.path.join("correction", filename)
    if os.path.exists(correction_path):
        return os.path.abspath(correction_path)
    
    # Buscar en el directorio padre si estamos en correction
    if os.path.basename(current_dir) == "correction":
        parent_path = os.path.join("..", filename)
        if os.path.exists(parent_path):
            return os.path.abspath(parent_path)
    
    return None

def test_emitter_available():
    """Verificar que el emisor Node.js está disponible"""
    try:
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            check=True,
            timeout=5
        )
        print(f"✅ Node.js disponible: {result.stdout.decode().strip()}")
        
        # Verificar que el emisor existe
        emitter_path = find_file("emitter-hamming.js")
        if emitter_path:
            print(f"✅ Emisor encontrado en: {emitter_path}")
            return True
        else:
            print("❌ Archivo emitter-hamming.js no encontrado")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ Node.js no está disponible")
        return False

def test_receptor_available():
    """Verificar que el receptor Python está disponible"""
    try:
        result = subprocess.run([
            "python3", "-c", "print('Receptor disponible')"
        ], capture_output=True, timeout=5, check=True)
        
        receptor_path = find_file("receptor-hamming.py")
        if receptor_path:
            print(f"✅ Receptor encontrado en: {receptor_path}")
            return True
        else:
            print("❌ Archivo receptor-hamming.py no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando receptor: {e}")
        return False

def wait_for_server(host, port, timeout=10):
    """Esperar hasta que el servidor esté disponible"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def start_receptor_server(port=5003):
    """Iniciar el servidor receptor en background"""
    try:
        receptor_path = find_file("receptor-hamming.py")
        if not receptor_path:
            print("❌ No se encontró receptor-hamming.py")
            return None
            
        process = subprocess.Popen([
            "python3", receptor_path, 
            "--tcp-port", str(port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar hasta que el servidor esté listo para aceptar conexiones
        print(f"⏳ Esperando que el servidor esté listo en puerto {port}...")
        if not wait_for_server("127.0.0.1", port, timeout=10):
            # Verificar si el proceso terminó
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ Servidor falló al iniciar: {stderr.decode()}")
            else:
                print(f"❌ Servidor no responde en puerto {port}")
                process.terminate()
            return None
            
        print(f"✅ Servidor iniciado y listo en puerto {port}")
        return process
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return None

def call_emitter(message, port=5003, **kwargs):
    """Llamar al emisor y obtener resultado"""
    emitter_path = find_file("emitter-hamming.js")
    if not emitter_path:
        print("❌ No se encontró emitter-hamming.js")
        return None
        
    cmd = [
        "node", emitter_path,
        message,
        "--tcp-host", "127.0.0.1",
        "--tcp-port", str(port)
    ]
    
    # Agregar parámetros opcionales
    if "ber" in kwargs:
        cmd.extend(["--ber", str(kwargs["ber"])])
    if "flip_bits" in kwargs:
        cmd.extend(["--flip-bits", ",".join(map(str, kwargs["flip_bits"]))])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        
        # Buscar el JSON de respuesta en el output
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if "Respuesta completa:" in line:
                # Verificar si el JSON empieza en la misma línea
                if line.strip().endswith('{'):
                    # El JSON empieza en esta línea, después del ':'
                    json_lines = ['{']  # Empezar con la llave de apertura
                    brace_count = 1
                    
                    # Continuar con las líneas siguientes
                    for j in range(i+1, len(lines)):
                        json_lines.append(lines[j])
                        brace_count += lines[j].count('{') - lines[j].count('}')
                        if brace_count == 0:
                            break
                    
                    if json_lines:
                        json_str = '\n'.join(json_lines)
                        return json.loads(json_str)
                else:
                    # El JSON está en las líneas siguientes
                    json_lines = []
                    brace_count = 0
                    started = False
                    
                    for j in range(i+1, len(lines)):
                        # Buscar la primera línea que contiene solo { (inicio del JSON principal)
                        if lines[j].strip() == '{' and not started:
                            started = True
                        if started:
                            json_lines.append(lines[j])
                            brace_count += lines[j].count('{') - lines[j].count('}')
                            if brace_count == 0:
                                break
                    
                    if json_lines:
                        json_str = '\n'.join(json_lines)
                        return json.loads(json_str)
        
        print("⚠️  No se encontró JSON en respuesta")
        return None
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout del emisor")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error del emisor: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        return None

def run_test_suite():
    """Ejecutar suite de tests"""
    print("=" * 50)
    print("🧪 SUITE DE TESTS - HAMMING CROSS-LANGUAGE")
    print("=" * 50)
    
    # Detectar directorio de trabajo
    print("\n📋 Detectando entorno...")
    if not detect_working_directory():
        print("❌ No se puede ejecutar desde este directorio")
        return False
    
    # Verificar dependencias
    print("\n📋 Verificando dependencias...")
    if not test_emitter_available() or not test_receptor_available():
        return False
    
    # Iniciar servidor
    print("\n🚀 Iniciando servidor receptor...")
    server = start_receptor_server()
    if not server:
        return False
    
    try:
        # Tests
        print("\n🧪 Ejecutando tests...")
        all_passed = True
        
        # Test 1: Sin errores
        print("\n--- Test 1: Sin errores ---")
        response = call_emitter("A", ber=0.0)
        if response and response.get("ok") and response.get("original_ascii") == "A":
            print("✅ PASÓ: Mensaje sin errores")
        else:
            print("❌ FALLÓ: Mensaje sin errores")
            print(f"📤 Respuesta: {response}")
            all_passed = False
        
        # Test 2: Con error corregible
        print("\n--- Test 2: Error corregible ---")
        response = call_emitter("A", flip_bits=[3])
        if response and response.get("ok") and response.get("error_detected") and response.get("corrected"):
            print("✅ PASÓ: Error detectado y corregido")
        else:
            print("❌ FALLÓ: Error no corregido correctamente")
            print(f"📤 Respuesta: {response}")
            all_passed = False
        
        # Test 3: Mensaje más largo
        print("\n--- Test 3: Mensaje largo ---")
        response = call_emitter("Hi", ber=0.0)
        if response and response.get("ok") and response.get("original_ascii") == "Hi":
            print("✅ PASÓ: Mensaje largo sin errores")
        else:
            print("❌ FALLÓ: Mensaje largo")
            print(f"📤 Respuesta: {response}")
            all_passed = False
        
        # Test 4: Múltiples bloques con error
        print("\n--- Test 4: Múltiples bloques ---")
        response = call_emitter("Test", flip_bits=[5])
        if response and response.get("blocks_processed", 0) > 1:
            print("✅ PASÓ: Múltiples bloques procesados")
        else:
            print("❌ FALLÓ: Múltiples bloques")
            print(f"📤 Respuesta: {response}")
            all_passed = False
        
        # Test 5: BER aleatorio
        print("\n--- Test 5: BER aleatorio ---")
        response = call_emitter("Code", ber=0.03)
        if response and "ok" in response:
            print("✅ PASÓ: BER aleatorio manejado")
        else:
            print("❌ FALLÓ: BER aleatorio")
            print(f"📤 Respuesta: {response}")
            all_passed = False
        
        return all_passed
        
    finally:
        # Cerrar servidor
        print("\n🛑 Cerrando servidor...")
        server.terminate()
        server.wait(timeout=5)

def main():
    """Función principal"""
    success = run_test_suite()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ Sistema Hamming cross-language funcionando correctamente")
        sys.exit(0)
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔍 Revisar logs arriba para detalles")
        sys.exit(1)

if __name__ == "__main__":
    main()
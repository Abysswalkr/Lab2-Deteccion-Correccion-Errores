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

def receptor_hamming(trama_recibida):
    print(f"\n=== RECEPTOR HAMMING ===")
    print(f"Trama recibida: {trama_recibida}")
    
    if not all(bit in '01' for bit in trama_recibida):
        raise ValueError("La entrada debe ser una cadena binaria (solo 0s y 1s)")
    
    longitud_trama = len(trama_recibida)
    trama_lista = [int(bit) for bit in trama_recibida]
    
    posiciones_paridad = obtener_posiciones_paridad(longitud_trama)
    print(f"Posiciones de paridad detectadas: {posiciones_paridad}")
    
    sindrome = 0
    verificaciones_paridad = []
    
    print(f"\n--- VERIFICACIÓN DE PARIDADES ---")
    for pos_paridad in posiciones_paridad:
        paridad_calculada = calcular_bit_paridad(trama_lista, pos_paridad, longitud_trama)
        
        posiciones_incluidas = []
        for pos in range(1, longitud_trama + 1):
            if pos & pos_paridad:
                posiciones_incluidas.append(pos)
        
        print(f"P{pos_paridad}: XOR de posiciones {posiciones_incluidas} = {paridad_calculada}")
        verificaciones_paridad.append(paridad_calculada)
        
        if paridad_calculada != 0:
            sindrome += pos_paridad
    
    print(f"Verificaciones de paridad: {verificaciones_paridad}")
    print(f"Síndrome: {sindrome}")
    
    resultado = {
        'trama_recibida': trama_recibida,
        'posiciones_paridad': posiciones_paridad,
        'sindrome': sindrome,
        'error_detectado': sindrome != 0,
        'error_corregido': False,
        'posicion_error': None,
        'trama_corregida': trama_recibida,
        'datos_originales': ''
    }
    
    if sindrome == 0:
        print("✓ No se detectaron errores")
        resultado['datos_originales'] = extraer_datos_originales(trama_lista, posiciones_paridad)
        print(f"Datos originales: {resultado['datos_originales']}")
        
    else:
        print(f"✗ Error detectado en posición: {sindrome}")
        resultado['posicion_error'] = sindrome
        
        if sindrome <= longitud_trama:
            print(f"Corrigiendo bit en posición {sindrome}...")
            trama_lista[sindrome - 1] = 1 - trama_lista[sindrome - 1]
            resultado['trama_corregida'] = ''.join(map(str, trama_lista))
            resultado['error_corregido'] = True
            
            print(f"Trama corregida: {resultado['trama_corregida']}")
            resultado['datos_originales'] = extraer_datos_originales(trama_lista, posiciones_paridad)
            print(f"Datos originales: {resultado['datos_originales']}")
            
            print(f"\n--- VERIFICACIÓN POST-CORRECCIÓN ---")
            sindrome_post = 0
            for pos_paridad in posiciones_paridad:
                paridad_post = calcular_bit_paridad(trama_lista, pos_paridad, longitud_trama)
                if paridad_post != 0:
                    sindrome_post += pos_paridad
            print(f"Síndrome post-corrección: {sindrome_post} (debe ser 0)")
            
        else:
            print(f"⚠ Error: Posición de error inválida ({sindrome})")
            resultado['datos_originales'] = "ERROR: No se puede corregir"
    
    return resultado

def introducir_error(trama, posicion):  
    if posicion < 1 or posicion > len(trama):
        raise ValueError(f"Posición inválida: {posicion}")
    
    trama_lista = list(trama)
    trama_lista[posicion - 1] = '1' if trama_lista[posicion - 1] == '0' else '0'
    return ''.join(trama_lista)

def probar_receptor():
    tramas_prueba = [
        ("1010101", "Mensaje '1101' - sin errores"),  
        ("0111101", "Mensaje '1101' - con error en posición 2"),
        ("1000101", "Mensaje '1101' - con error en posición 3"),
    ]
    
    print("=" * 60)
    print("PRUEBAS DEL RECEPTOR HAMMING CORREGIDO")
    print("=" * 60)
    
    for i, (trama, descripcion) in enumerate(tramas_prueba):
        try:
            print(f"\n--- PRUEBA {i + 1}: {descripcion} ---")
            resultado = receptor_hamming(trama)
            
            if resultado['error_detectado']:
                if resultado['error_corregido']:
                    print(f"RESULTADO: Error detectado y corregido en posición {resultado['posicion_error']}")
                else:
                    print(f"RESULTADO: Error detectado pero no corregido")
            else:
                print(f"RESULTADO: Trama recibida correctamente")
                
        except Exception as error:
            print(f"Error en prueba {i + 1}: {error}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python receptor-hamming.py <trama_codificada>")
        print("Ejemplo: python receptor-hamming.py 1010101")
        print("\nEjecutando pruebas por defecto...")
        probar_receptor()
        return
    
    try:
        trama = sys.argv[1]
        resultado = receptor_hamming(trama)
        
        print(f"\n{'='*40}")
        print("RESUMEN:")
        if resultado['error_detectado']:
            if resultado['error_corregido']:
                print(f"✓ Error corregido en posición {resultado['posicion_error']}")
                print(f"✓ Datos recuperados: {resultado['datos_originales']}")
            else:
                print(f"✗ Error detectado pero no corregible")
        else:
            print(f"✓ Trama recibida sin errores")
            print(f"✓ Datos: {resultado['datos_originales']}")
            
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
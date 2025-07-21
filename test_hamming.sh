#!/bin/bash

# Script de pruebas para CÓDIGO DE HAMMING únicamente
# Lab 2 - CC3067 Redes

echo "=========================================="
echo "PRUEBAS CÓDIGO DE HAMMING"
echo "=========================================="

# Mensajes de prueba acordados (coordinar con pareja)
MENSAJES=("1101" "10110" "111010011")
echo "Mensajes de prueba: ${MENSAJES[@]}"
echo ""

# Crear directorio para resultados
mkdir -p resultados_hamming
cd resultados_hamming

# Función para introducir error en posición específica
introducir_error() {
    local trama="$1"
    local posicion="$2"
    
    # Convertir a array
    trama_array=($(echo "$trama" | grep -o .))
    
    # Flip del bit
    if [ "${trama_array[$((posicion-1))]}" = "0" ]; then
        trama_array[$((posicion-1))]="1"
    else
        trama_array[$((posicion-1))]="0"
    fi
    
    # Reconstruir
    echo "${trama_array[@]}" | tr -d ' '
}

# Inicializar archivo de resultados
echo "=== RESULTADOS HAMMING - LABORATORIO 2 ===" > resultados_hamming.txt
echo "Fecha: $(date)" >> resultados_hamming.txt
echo "Algoritmo: Código de Hamming (Corrección de errores)" >> resultados_hamming.txt
echo "" >> resultados_hamming.txt

echo "🔧 PARTE 1: GENERACIÓN DE TRAMAS HAMMING" | tee -a resultados_hamming.txt
echo "==========================================" | tee -a resultados_hamming.txt

# Array para almacenar tramas generadas
declare -a TRAMAS_HAMMING

for i in "${!MENSAJES[@]}"; do
    mensaje="${MENSAJES[$i]}"
    
    echo "" | tee -a resultados_hamming.txt
    echo "--- MENSAJE $((i+1)): '$mensaje' (${#mensaje} bits) ---" | tee -a resultados_hamming.txt
    
    # Generar trama Hamming
    hamming_output=$(node ../correction/emitter-hamming.js "$mensaje" 2>&1)
    echo "$hamming_output" | tee -a resultados_hamming.txt
    
    # Extraer trama codificada
    trama_hamming=$(echo "$hamming_output" | grep "TRAMA CODIFICADA:" | cut -d' ' -f3)
    TRAMAS_HAMMING[$i]="$trama_hamming"
    
    echo "" | tee -a resultados_hamming.txt
    echo "TRAMA GENERADA: $trama_hamming" | tee -a resultados_hamming.txt
done

echo "" | tee -a resultados_hamming.txt
echo "🧪 PARTE 2: PRUEBAS SIN ERRORES" | tee -a resultados_hamming.txt
echo "================================" | tee -a resultados_hamming.txt

for i in "${!MENSAJES[@]}"; do
    mensaje="${MENSAJES[$i]}"
    trama="${TRAMAS_HAMMING[$i]}"
    
    echo "" | tee -a resultados_hamming.txt
    echo "=== PRUEBA SIN ERROR - MENSAJE $((i+1)): '$mensaje' ===" | tee -a resultados_hamming.txt
    echo "Trama enviada: $trama" | tee -a resultados_hamming.txt
    echo "" | tee -a resultados_hamming.txt
    
    resultado=$(python3 ../correction/receptor-hamming.py "$trama" 2>&1)
    echo "$resultado" | tee -a resultados_hamming.txt
done

echo "" | tee -a resultados_hamming.txt
echo "🧪 PARTE 3: PRUEBAS CON 1 ERROR" | tee -a resultados_hamming.txt
echo "=================================" | tee -a resultados_hamming.txt

for i in "${!MENSAJES[@]}"; do
    mensaje="${MENSAJES[$i]}"
    trama="${TRAMAS_HAMMING[$i]}"
    posicion_error=3
    
    trama_con_error=$(introducir_error "$trama" $posicion_error)
    
    echo "" | tee -a resultados_hamming.txt
    echo "=== PRUEBA CON 1 ERROR - MENSAJE $((i+1)): '$mensaje' ===" | tee -a resultados_hamming.txt
    echo "Trama original:    $trama" | tee -a resultados_hamming.txt
    echo "Trama con error:   $trama_con_error" | tee -a resultados_hamming.txt
    echo "Error en posición: $posicion_error" | tee -a resultados_hamming.txt
    echo "" | tee -a resultados_hamming.txt
    
    resultado=$(python3 ../correction/receptor-hamming.py "$trama_con_error" 2>&1)
    echo "$resultado" | tee -a resultados_hamming.txt
done

echo "" | tee -a resultados_hamming.txt
echo "🧪 PARTE 4: PRUEBAS CON 2+ ERRORES" | tee -a resultados_hamming.txt
echo "===================================" | tee -a resultados_hamming.txt

for i in "${!MENSAJES[@]}"; do
    mensaje="${MENSAJES[$i]}"
    trama="${TRAMAS_HAMMING[$i]}"
    
    # Introducir 2 errores
    trama_2errors=$(introducir_error "$trama" 2)
    trama_2errors=$(introducir_error "$trama_2errors" 5)
    
    echo "" | tee -a resultados_hamming.txt
    echo "=== PRUEBA CON 2 ERRORES - MENSAJE $((i+1)): '$mensaje' ===" | tee -a resultados_hamming.txt
    echo "Trama original:     $trama" | tee -a resultados_hamming.txt
    echo "Trama con 2 errores: $trama_2errors" | tee -a resultados_hamming.txt
    echo "Errores en posiciones: 2, 5" | tee -a resultados_hamming.txt
    echo "" | tee -a resultados_hamming.txt
    
    resultado=$(python3 ../correction/receptor-hamming.py "$trama_2errors" 2>&1)
    echo "$resultado" | tee -a resultados_hamming.txt
done

echo "" | tee -a resultados_hamming.txt
echo "🔍 PARTE 5: BÚSQUEDA DE CASOS NO DETECTABLES" | tee -a resultados_hamming.txt
echo "===============================================" | tee -a resultados_hamming.txt

echo "Buscando patrones de error que resulten en síndrome = 0..." | tee -a resultados_hamming.txt

for i in "${!MENSAJES[@]}"; do
    mensaje="${MENSAJES[$i]}"
    trama="${TRAMAS_HAMMING[$i]}"
    
    echo "" | tee -a resultados_hamming.txt
    echo "--- Análisis para mensaje '$mensaje' ---" | tee -a resultados_hamming.txt
    echo "Trama: $trama" | tee -a resultados_hamming.txt
    
    # Probar algunos patrones específicos que podrían dar síndrome 0
    # (Esto requiere análisis manual basado en las posiciones de paridad)
    echo "ANÁLISIS MANUAL REQUERIDO:" | tee -a resultados_hamming.txt
    echo "- Probar combinaciones de errores que sumen a 0 en el síndrome" | tee -a resultados_hamming.txt
    echo "- Documentar si existen patrones no detectables" | tee -a resultados_hamming.txt
done

echo "" | tee -a resultados_hamming.txt
echo "📊 RESUMEN PARA EL REPORTE" | tee -a resultados_hamming.txt
echo "============================" | tee -a resultados_hamming.txt
echo "" | tee -a resultados_hamming.txt
echo "VENTAJAS DEL CÓDIGO DE HAMMING:" | tee -a resultados_hamming.txt
echo "✓ Corrección automática de errores de 1 bit" | tee -a resultados_hamming.txt
echo "✓ Detección de errores de 2 bits" | tee -a resultados_hamming.txt
echo "✓ Indica posición exacta del error" | tee -a resultados_hamming.txt
echo "" | tee -a resultados_hamming.txt
echo "DESVENTAJAS DEL CÓDIGO DE HAMMING:" | tee -a resultados_hamming.txt
echo "✗ Alto overhead para mensajes cortos" | tee -a resultados_hamming.txt
echo "✗ Puede 'corregir' incorrectamente con 2+ errores" | tee -a resultados_hamming.txt
echo "✗ Complejidad computacional media" | tee -a resultados_hamming.txt

echo ""
echo "✅ Pruebas de Hamming completadas!"
echo "📄 Resultados en: resultados_hamming/resultados_hamming.txt"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Coordinar con tu pareja para que use los mismos mensajes: ${MENSAJES[@]}"
echo "2. Comparar resultados entre Hamming y Fletcher"
echo "3. Escribir reporte conjunto con análisis comparativo"

cd ..
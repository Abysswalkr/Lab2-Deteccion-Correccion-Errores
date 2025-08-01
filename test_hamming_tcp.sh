#!/bin/bash

echo "=========================================="
echo "PRUEBA TCP - HAMMING CORRECCIÓN v2.0"
echo "MÚLTIPLES BLOQUES HAMMING(7,4)"
echo "=========================================="

# Verificar que los archivos existen
if [ ! -f "correction/receptor-hamming.py" ]; then
    echo "❌ No se encontró correction/receptor-hamming.py"
    exit 1
fi

if [ ! -f "correction/emitter-hamming.js" ]; then
    echo "❌ No se encontró correction/emitter-hamming.js"
    exit 1
fi

echo "✅ Archivos encontrados"

# Puerto para las pruebas
PORT=5001
HOST="127.0.0.1"

echo "🚀 Iniciando receptor Hamming en puerto $PORT..."

# Iniciar receptor en background
python3 correction/receptor-hamming.py --tcp-port $PORT &
RECEPTOR_PID=$!

# Esperar a que el servidor inicie
sleep 2

echo "📡 Servidor iniciado (PID: $RECEPTOR_PID)"
echo ""

# Prueba 1: Mensaje corto sin errores
echo "🧪 PRUEBA 1: Mensaje 'A' sin errores"
echo "----------------------------------------"
node correction/emitter-hamming.js "A" --tcp-host $HOST --tcp-port $PORT --ber 0
echo ""

# Prueba 2: Mensaje corto con error manual (debería corregir)
echo "🧪 PRUEBA 2: Mensaje 'A' con error en posición 3 (corrección)"
echo "----------------------------------------"
node correction/emitter-hamming.js "A" --tcp-host $HOST --tcp-port $PORT --flip-bits "3"
echo ""

# Prueba 3: Mensaje más largo sin errores
echo "🧪 PRUEBA 3: Mensaje 'Hi' sin errores"
echo "----------------------------------------"
node correction/emitter-hamming.js "Hi" --tcp-host $HOST --tcp-port $PORT --ber 0
echo ""

# Prueba 4: Mensaje más largo con BER bajo (algunas correcciones)
echo "🧪 PRUEBA 4: Mensaje 'Test' con BER=0.05 (correcciones aleatorias)"
echo "----------------------------------------"
node correction/emitter-hamming.js "Test" --tcp-host $HOST --tcp-port $PORT --ber 0.05
echo ""

# Prueba 5: Error manual en segundo bloque
echo "🧪 PRUEBA 5: Mensaje 'Hi' con error en posición 10 (segundo bloque)"
echo "----------------------------------------"
node correction/emitter-hamming.js "Hi" --tcp-host $HOST --tcp-port $PORT --flip-bits "10"
echo ""

# Prueba 6: Múltiples errores (algunos corregibles, otros no)
echo "🧪 PRUEBA 6: Mensaje 'Code' con errores múltiples"
echo "----------------------------------------"
node correction/emitter-hamming.js "Code" --tcp-host $HOST --tcp-port $PORT --flip-bits "5,12"
echo ""

echo "⏱️  Esperando antes de cerrar servidor..."
sleep 3

# Matar el proceso del receptor
echo "🛑 Cerrando receptor..."
kill $RECEPTOR_PID 2>/dev/null
wait $RECEPTOR_PID 2>/dev/null

echo ""
echo "✅ PRUEBAS HAMMING TCP COMPLETADAS"
echo "📋 Resumen: El sistema Hamming(7,4) puede detectar y corregir"
echo "    errores de 1 bit por bloque de 7 bits."
echo "    Múltiples errores en el mismo bloque pueden no ser corregibles."
echo "=========================================="
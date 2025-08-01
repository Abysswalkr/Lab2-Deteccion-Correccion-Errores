const net = require('net');

// Función para parsear argumentos de línea de comandos
function parseArgs() {
    const args = process.argv.slice(2);
    const result = {
        mensaje: null,
        tcpHost: null,
        tcpPort: null,
        ber: 0.1, // probabilidad de error por defecto
        flipBits: [] // bits específicos a voltear
    };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--tcp-host':
                result.tcpHost = args[i + 1];
                i++;
                break;
            case '--tcp-port':
                result.tcpPort = parseInt(args[i + 1], 10);
                i++;
                break;
            case '--ber':
                result.ber = parseFloat(args[i + 1]);
                i++;
                break;
            case '--flip-bits':
                result.flipBits = args[i + 1].split(',').map(x => parseInt(x.trim(), 10)).filter(x => !isNaN(x));
                i++;
                break;
            default:
                if (!result.mensaje && !args[i].startsWith('--')) {
                    result.mensaje = args[i];
                }
        }
    }
    
    return result;
}

// Capa de Presentación: Convertir a binario
function toBinary(str) {
    return str.split('').map(char => char.charCodeAt(0).toString(2).padStart(8, '0')).join('');
}

// Capa de Enlace: Codificar con Hamming (7,4) para cada bloque de 4 bits
function hammingEncodeBlock(block) {
    // block: string de 4 bits
    const d = block.split('').map(Number);
    // Parity bits
    const p1 = d[0] ^ d[1] ^ d[3];
    const p2 = d[0] ^ d[2] ^ d[3];
    const p3 = d[1] ^ d[2] ^ d[3];
    // Estructura: p1 p2 d0 p3 d1 d2 d3
    return `${p1}${p2}${d[0]}${p3}${d[1]}${d[2]}${d[3]}`;
}

function hammingEncode(bin) {
    // Divide en bloques de 4 bits
    let result = '';
    for (let i = 0; i < bin.length; i += 4) {
        let block = bin.substr(i, 4);
        if (block.length < 4) block = block.padEnd(4, '0');
        result += hammingEncodeBlock(block);
    }
    return result;
}

// Capa de Ruido: Introducir errores
function addNoiseWithBER(data, ber) {
    let arr = data.split('');
    let flippedPositions = [];
    
    for (let i = 0; i < arr.length; i++) {
        if (Math.random() < ber) {
            arr[i] = arr[i] === '0' ? '1' : '0';
            flippedPositions.push(i);
        }
    }
    
    return {
        data: arr.join(''),
        flipped: flippedPositions
    };
}

function addNoiseManual(data, positions) {
    let arr = data.split('');
    let flipped = [];
    
    positions.forEach(pos => {
        if (pos >= 0 && pos < arr.length) {
            arr[pos] = arr[pos] === '0' ? '1' : '0';
            flipped.push(pos);
        }
    });
    
    return {
        data: arr.join(''),
        flipped: flipped
    };
}

// Convertir string binario a hex
function binaryToHex(binary) {
    // Asegurar que sea múltiplo de 8 para formar bytes válidos
    while (binary.length % 8 !== 0) {
        binary = binary + '0';
    }
    
    let hex = '';
    for (let i = 0; i < binary.length; i += 8) {
        const byte = binary.substr(i, 8);
        hex += parseInt(byte, 2).toString(16).padStart(2, '0');
    }
    return hex;
}

// Cliente TCP
function sendOverTCP(host, port, frameHex) {
    return new Promise((resolve, reject) => {
        const client = new net.Socket();
        let buffer = '';
        
        client.connect(port, host, () => {
            console.log(`=== CAPA TRANSMISIÓN (TCP) ===`);
            console.log(`Conectado a ${host}:${port}`);
            
            const payload = {
                frame_hex: frameHex
            };
            
            const message = JSON.stringify(payload) + '\n';
            console.log(`Enviando: ${JSON.stringify(payload)}`);
            client.write(message);
        });
        
        client.on('data', (data) => {
            buffer += data.toString();
            
            if (buffer.includes('\n')) {
                const response = buffer.split('\n')[0];
                try {
                    const parsed = JSON.parse(response);
                    resolve(parsed);
                } catch (e) {
                    reject(new Error(`Error parsing JSON: ${e.message}`));
                }
                client.destroy();
            }
        });
        
        client.on('error', (err) => {
            reject(err);
        });
        
        client.on('close', () => {
            if (!buffer.includes('\n')) {
                reject(new Error('Conexión cerrada sin respuesta completa'));
            }
        });
        
        // Timeout de 10 segundos
        setTimeout(() => {
            client.destroy();
            reject(new Error('Timeout de conexión TCP'));
        }, 10000);
    });
}

async function procesarMensaje(mensaje, args) {
    console.log('=== CAPA APLICACIÓN ===');
    console.log('Mensaje original:', mensaje);
    console.log('Algoritmo: Código de Hamming (7,4)');
    console.log('BER:', args.ber);
    console.log('Bits manuales a voltear:', args.flipBits);

    // Presentación
    console.log('\n=== CAPA PRESENTACIÓN ===');
    const binario = toBinary(mensaje);
    console.log('Mensaje en binario:', binario);

    // Enlace
    console.log('\n=== CAPA ENLACE ===');
    const codificado = hammingEncode(binario);
    console.log('TRAMA CODIFICADA:', codificado);
    console.log(`Longitud: ${codificado.length} bits`);

    // Ruido
    console.log('\n=== CAPA RUIDO (EMISOR) ===');
    let noisyResult;
    
    if (args.flipBits.length > 0) {
        console.log('Modo manual - volteando bits en posiciones:', args.flipBits);
        noisyResult = addNoiseManual(codificado, args.flipBits);
    } else {
        console.log(`Aplicando BER: ${args.ber}`);
        noisyResult = addNoiseWithBER(codificado, args.ber);
    }
    
    console.log('Trama con ruido:', noisyResult.data);
    console.log('Bits volteados en posiciones:', noisyResult.flipped);
    console.log(`Total de bits volteados: ${noisyResult.flipped.length}`);

    // Convertir a hex para transmisión
    const frameHex = binaryToHex(noisyResult.data);
    console.log('Trama en hex:', frameHex);

    // Transmisión TCP
    if (args.tcpHost && args.tcpPort) {
        try {
            const response = await sendOverTCP(args.tcpHost, args.tcpPort, frameHex);
            
            console.log('\n=== RESPUESTA DEL RECEPTOR ===');
            console.log('Respuesta completa:', JSON.stringify(response, null, 2));
            
            console.log('\n=== RESUMEN ===');
            if (response.ok) {
                if (response.error_detected) {
                    console.log(`✓ ${response.total_errors || 1} error(es) detectado(s)`);
                    if (response.corrected) {
                        console.log(`✓ ${response.total_corrected || 1} error(es) corregido(s) exitosamente`);
                        console.log(`✓ Mensaje recuperado: "${response.original_ascii}"`);
                    } else {
                        console.log('✗ Error(es) no pudieron ser corregidos');
                    }
                    console.log(`📊 Bloques procesados: ${response.blocks_processed || 'N/A'}`);
                } else {
                    console.log('✓ Mensaje recibido sin errores');
                    console.log(`✓ Mensaje: "${response.original_ascii}"`);
                    console.log(`📊 Bloques procesados: ${response.blocks_processed || 'N/A'}`);
                }
            } else {
                console.log('✗ Error en el procesamiento:', response.error || 'Error desconocido');
            }
            
            // Mostrar debug de bloques si está disponible
            if (response.debug_blocks && response.debug_blocks.length > 0) {
                console.log('\n--- Debug: Detalle por bloque ---');
                response.debug_blocks.forEach(block => {
                    const status = !block.error_detected ? '✓' : (block.corrected ? '⚠' : '✗');
                    console.log(`  Bloque ${block.block_num}: ${block.original} → ${block.data_bits} ${status}`);
                });
            }
            
        } catch (error) {
            console.error('Error de transmisión TCP:', error.message);
            process.exit(1);
        }
    } else {
        console.log('\n=== TRANSMISIÓN ===');
        console.log('No se especificó --tcp-host y --tcp-port');
        console.log('Ejecutar con: node emitter-hamming.js "mensaje" --tcp-host 127.0.0.1 --tcp-port 5001');
    }
    
    // Asegurar que el proceso termine
    process.exit(0);
}

function mostrarAyuda() {
    console.log(`
Uso: node emitter-hamming.js <mensaje> [opciones]

Opciones:
  --tcp-host <host>     Host del receptor (ej: 127.0.0.1)
  --tcp-port <puerto>   Puerto del receptor (ej: 5001)
  --ber <probabilidad>  Probabilidad de error por bit (ej: 0.1)
  --flip-bits <lista>   Bits específicos a voltear (ej: "2,5,7")

Ejemplos:
  node emitter-hamming.js "Hola" --tcp-host 127.0.0.1 --tcp-port 5001
  node emitter-hamming.js "Test" --tcp-host 127.0.0.1 --tcp-port 5001 --ber 0.05
  node emitter-hamming.js "A" --tcp-host 127.0.0.1 --tcp-port 5001 --flip-bits "3,7"
`);
}

function ejecutarPruebas() {
    const mensajesPrueba = ["1101", "A", "AB"];
    
    console.log("========================================");
    console.log("PRUEBAS DEL EMISOR HAMMING");
    console.log("========================================");
    
    mensajesPrueba.forEach((msg, index) => {
        console.log(`\n--- PRUEBA ${index + 1}: Mensaje "${msg}" ---`);
        
        const binario = msg.split('').map(char => {
            return typeof char === 'string' ? toBinary(char) : char;
        }).join('');
        
        const codificado = hammingEncode(binario);
        console.log(`Mensaje: ${msg}`);
        console.log(`Binario: ${binario}`);
        console.log(`Hamming: ${codificado}`);
        console.log(`Hex: ${binaryToHex(codificado)}`);
    });
}

async function main() {
    const args = parseArgs();
    
    if (!args.mensaje) {
        if (process.argv.length === 2) {
            // Sin argumentos - ejecutar pruebas
            ejecutarPruebas();
        } else {
            // Argumentos pero sin mensaje
            mostrarAyuda();
        }
        return;
    }
    
    await procesarMensaje(args.mensaje, args);
}

// Ejecutar
main().catch(console.error);
// Capa de Aplicación: Leer mensaje desde consola
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

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

// Capa de Ruido: Introducir error aleatorio en un bit
function addNoise(data) {
  let arr = data.split('');
  const pos = Math.floor(Math.random() * arr.length);
  arr[pos] = arr[pos] === '0' ? '1' : '0';
  return arr.join('');
}

rl.question('Ingrese el mensaje a enviar: ', (input) => {
  // Aplicación
  console.log('Mensaje original:', input);

  // Presentación
  const binario = toBinary(input);
  console.log('Mensaje en binario:', binario);

  // Enlace
  const codificado = hammingEncode(binario);
  console.log('Mensaje codificado (Hamming 7,4):', codificado);

  // Ruido
  const conRuido = addNoise(codificado);
  console.log('Mensaje con ruido:', conRuido);

  rl.close();
});
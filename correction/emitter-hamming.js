function calcularBitsParidad(longitud_datos) {
  let r = 1;
  while (longitud_datos + r + 1 > Math.pow(2, r)) {
      r++;
  }
  return r;
}

function obtenerPosicionesParidad(num_bits_paridad) {
  const posiciones = [];
  for (let i = 0; i < num_bits_paridad; i++) {
      posiciones.push(Math.pow(2, i));
  }
  return posiciones;
}

function construirTramaConParidad(datos_binarios) {
  const longitud_datos = datos_binarios.length;
  const num_bits_paridad = calcularBitsParidad(longitud_datos);
  const posiciones_paridad = obtenerPosicionesParidad(num_bits_paridad);
  
  const longitud_total = longitud_datos + num_bits_paridad;
  const trama = new Array(longitud_total + 1).fill(0);
  
  let indice_datos = 0;
  
  for (let pos = 1; pos <= longitud_total; pos++) {
      if (!posiciones_paridad.includes(pos)) {
          trama[pos] = parseInt(datos_binarios[indice_datos]);
          indice_datos++;
      }
  }
  
  return { trama, posiciones_paridad, longitud_total };
}

function calcularBitParidad(trama, posicion_paridad, longitud_total) {
  let paridad = 0;
  
  for (let pos = 1; pos <= longitud_total; pos++) {
      if (pos & posicion_paridad) {
          paridad ^= trama[pos];
      }
  }
  
  return paridad;
}

function emisorHamming(datos_binarios) {
  
  console.log(`\n=== EMISOR HAMMING ===`);
  console.log(`Datos originales: ${datos_binarios}`);
  
  if (!/^[01]+$/.test(datos_binarios)) {
      throw new Error("La entrada debe ser una cadena binaria (solo 0s y 1s)");
  }
  
  const { trama, posiciones_paridad, longitud_total } = construirTramaConParidad(datos_binarios);
  
  console.log(`Bits de datos: ${datos_binarios.length}`);
  console.log(`Bits de paridad necesarios: ${posiciones_paridad.length}`);
  console.log(`Posiciones de paridad: ${posiciones_paridad.join(', ')}`);
  
  for (const pos_paridad of posiciones_paridad) {
      trama[pos_paridad] = calcularBitParidad(trama, pos_paridad, longitud_total);
      console.log(`Bit de paridad en posición ${pos_paridad}: ${trama[pos_paridad]}`);
  }
  
  const trama_final = trama.slice(1).join('');
  
  console.log(`Trama con código de Hamming: ${trama_final}`);
  console.log(`Longitud total: ${trama_final.length} bits`);
  
  return {
      trama_original: datos_binarios,
      trama_codificada: trama_final,
      posiciones_paridad: posiciones_paridad,
      longitud_datos: datos_binarios.length,
      longitud_total: trama_final.length
  };
}

function probarEmisor() {
  const mensajes_prueba = [
      "1101",
      "10110",
      "111010011"
  ];
  
  console.log("=".repeat(50));
  console.log("PRUEBAS DEL EMISOR HAMMING");
  console.log("=".repeat(50));
  
  for (let i = 0; i < mensajes_prueba.length; i++) {
      try {
          console.log(`\n--- PRUEBA ${i + 1} ---`);
          const resultado = emisorHamming(mensajes_prueba[i]);
          console.log(`RESULTADO: ${resultado.trama_codificada}`);
      } catch (error) {
          console.error(`Error en prueba ${i + 1}:`, error.message);
      }
  }
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
      console.log("Uso: node emisor_hamming.js <datos_binarios>");
      console.log("Ejemplo: node emisor_hamming.js 1101");
      console.log("\nEjecutando pruebas por defecto...");
      probarEmisor();
      return;
  }
  
  try {
      const datos = args[0];
      const resultado = emisorHamming(datos);
      console.log(`\nTRAMA CODIFICADA: ${resultado.trama_codificada}`);
  } catch (error) {
      console.error("Error:", error.message);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  emisorHamming,
  calcularBitsParidad,
  obtenerPosicionesParidad
};
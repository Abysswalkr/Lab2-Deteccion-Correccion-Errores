#!/usr/bin/env node
// Uso: node detector/fletcher/receptor.js <8|16|32> <hex_frame>

const [,, blockSizeArg, hexFrame] = process.argv;
try {
  const blockSize = parseInt(blockSizeArg, 10);
  if (![8, 16, 32].includes(blockSize)) {
    throw new Error("block_size debe ser 8, 16 o 32");
  }

  const frame = Buffer.from(hexFrame, "hex");
  const byteBlock = blockSize / 8;
  const checksumLen = 2 * byteBlock;

  if (frame.length < checksumLen) {
    return printJSON(false, "");
  }

  const dataPart = frame.slice(0, frame.length - checksumLen);

  // ---- padding igual que el emisor Python ----
  let bufToCheck = dataPart;
  if (bufToCheck.length % byteBlock !== 0) {
    const padLen = byteBlock - (bufToCheck.length % byteBlock);
    bufToCheck = Buffer.concat([bufToCheck, Buffer.alloc(padLen)]);
  }

  const modulo = Math.pow(2, blockSize) - 1;

  function leerBloque(buf, offset) {
    switch (byteBlock) {
      case 1: return buf.readUInt8(offset);
      case 2: return buf.readUInt16BE(offset);
      case 4: return buf.readUInt32BE(offset);
      default: throw new Error("byteBlock inválido");
    }
  }

  function escribirBloque(buf, value, offset) {
    switch (byteBlock) {
      case 1: return buf.writeUInt8(value, offset);
      case 2: return buf.writeUInt16BE(value, offset);
      case 4: return buf.writeUInt32BE(value, offset);
    }
  }

  // ---- calcular Fletcher ----
  let sum1 = 0, sum2 = 0;
  for (let i = 0; i < bufToCheck.length; i += byteBlock) {
    const block = leerBloque(bufToCheck, i);
    sum1 = (sum1 + block) % modulo;
    sum2 = (sum2 + sum1) % modulo;
  }

  const expected = Buffer.alloc(checksumLen);
  escribirBloque(expected, sum1, 0);
  escribirBloque(expected, sum2, byteBlock);

  const got = frame.slice(frame.length - checksumLen);

  const ok = expected.equals(got);
  const original = ok ? dataPart.toString("hex") : "";

  return printJSON(ok, original);

} catch (e) {
  console.error(e.stack || e);
  process.exit(1);
}

function printJSON(ok, originalHex) {
  console.log(JSON.stringify({ ok, original: originalHex }));
  process.exit(0);
}

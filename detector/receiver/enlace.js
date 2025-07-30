function verifyFletcher(frameBuf, blockSize) {
  const byteBlock = blockSize / 8;
  const checksumLen = 2 * byteBlock;
  if (frameBuf.length < checksumLen) {
    return { ok: false, original: Buffer.alloc(0) };
  }
  const dataPart = frameBuf.slice(0, frameBuf.length - checksumLen);

  // aplicar el mismo padding que el emisor antes de calcular
  let bufToCheck = dataPart;
  if (bufToCheck.length % byteBlock !== 0) {
    const padLen = byteBlock - (bufToCheck.length % byteBlock);
    bufToCheck = Buffer.concat([bufToCheck, Buffer.alloc(padLen)]);
  }

  const modulo = Math.pow(2, blockSize) - 1;

  function readBlock(buf, offset) {
    switch (byteBlock) {
      case 1: return buf.readUInt8(offset);
      case 2: return buf.readUInt16BE(offset);
      case 4: return buf.readUInt32BE(offset);
      default: throw new Error("byteBlock inválido");
    }
  }
  function writeBlock(buf, value, offset) {
    switch (byteBlock) {
      case 1: return buf.writeUInt8(value, offset);
      case 2: return buf.writeUInt16BE(value, offset);
      case 4: return buf.writeUInt32BE(value, offset);
    }
  }

  let sum1 = 0, sum2 = 0;
  for (let i = 0; i < bufToCheck.length; i += byteBlock) {
    const block = readBlock(bufToCheck, i);
    sum1 = (sum1 + block) % modulo;
    sum2 = (sum2 + sum1) % modulo;
  }

  const expected = Buffer.alloc(checksumLen);
  writeBlock(expected, sum1, 0);
  writeBlock(expected, sum2, byteBlock);

  const got = frameBuf.slice(frameBuf.length - checksumLen);
  const ok = expected.equals(got);
  const original = ok ? dataPart : Buffer.alloc(0);

  return { ok, original };
}

module.exports = { verifyFletcher };

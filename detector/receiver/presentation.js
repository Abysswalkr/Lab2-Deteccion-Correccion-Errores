function bufferToAscii(buf) {
  try {
    return buf.toString("ascii");
  } catch {
    return "";
  }
}
function hexToBuffer(hex) {
  return Buffer.from(hex, "hex");
}
module.exports = { bufferToAscii, hexToBuffer };

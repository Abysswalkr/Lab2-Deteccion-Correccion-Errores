const { bufferToAscii } = require("./presentation");
const { verifyFletcher } = require("./enlace");

function processFrame(alg, blockSize, frameBuf) {
  if (alg !== "fletcher") {
    return { ok: false, message: "Algoritmo no soportado", original_hex: "", original_ascii: "" };
  }
  const { ok, original } = verifyFletcher(frameBuf, blockSize);
  const original_hex = ok ? original.toString("hex") : "";
  const original_ascii = ok ? bufferToAscii(original) : "";
  return { ok, original_hex, original_ascii };
}

module.exports = { processFrame };

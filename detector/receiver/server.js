const net = require("net");
const { processFrame } = require("./application");
const { hexToBuffer } = require("./presentation");

function parseArgs() {
  const args = process.argv.slice(2);
  const idx = args.indexOf("--port");
  const port = (idx >= 0 && args[idx+1]) ? parseInt(args[idx+1], 10) : 5000;
  return { port };
}

function startServer(port) {
  const server = net.createServer((socket) => {
    let buffered = "";
    socket.on("data", (chunk) => {
      buffered += chunk.toString("utf-8");
      let idx;
      while ((idx = buffered.indexOf("\n")) >= 0) {
        const line = buffered.slice(0, idx);
        buffered = buffered.slice(idx + 1);
        handleLine(line, socket);
      }
    });
    socket.on("error", (err) => {
      console.error("Socket error:", err.message);
    });
  });

  server.listen(port, () => {
    console.log(`Receptor escuchando en tcp://0.0.0.0:${port}`);
  });
}

function handleLine(line, socket) {
  if (!line.trim()) return;
  let payload;
  try {
    payload = JSON.parse(line);
  } catch (e) {
    socket.write(JSON.stringify({ ok:false, error: "JSON inválido" }) + "\n");
    return;
  }
  const { alg, block_size, frame_hex } = payload;
  if (!alg || !block_size || !frame_hex) {
    socket.write(JSON.stringify({ ok:false, error: "Campos faltantes" }) + "\n");
    return;
  }
  const frameBuf = hexToBuffer(frame_hex);
  const result = processFrame(alg, block_size, frameBuf);
  socket.write(JSON.stringify(result) + "\n");
}

const { port } = parseArgs();
startServer(port);

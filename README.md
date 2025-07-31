# Lab2: Detección de errores con Fletcher Checksum

Este repositorio contiene la primera parte del Laboratorio 2 de **Esquemas de Detección y Corrección de Errores**, en la que implementamos el algoritmo **Fletcher Checksum** para **detección** de errores.
El **emisor** está en **Python** (arquitectura por capas) y el **receptor** en **JavaScript (Node.js)**, cumpliendo la consigna de usar **lenguajes distintos**.

---

## 🗂️ Estructura del proyecto

```text
Lab2-Deteccion-Correccion-Errores/
├─ detector/
│  ├─ __init__.py
│  ├─ fletcher/
│  │  ├─ __init__.py           # Exporta emisor_fletcher, calcular_fletcher (Python)
│  │  ├─ constants.py          # Tamaños de bloque permitidos (8/16/32)
│  │  └─ emisor.py             # Cálculo Fletcher + construcción de trama
│  ├─ emitter/                 # CAPAS (lado emisor, en Python)
│  │  ├─ application.py        # Aplicación: entrada de parámetros, resumen
│  │  ├─ presentation.py       # Presentación: ASCII <-> bits/hex
│  │  ├─ enlace.py             # Enlace: emisor_fletcher, armado de trama
│  │  ├─ ruido.py              # "Ruido": BER y flips manuales (--flip-bits)
│  │  ├─ transmision.py        # TCP JSONL (send_over_tcp + JsonlClient persistente)
│  │  └─ main.py               # CLI principal del emisor
│  ├─ receiver/                # RECEPTOR (lado receptor, en Node.js)
│  │  └─ server.js             # Servidor TCP JSONL: verifica Fletcher y responde JSON
│  ├─ tests/
│  │  └─ test_fletcher_cross.py  # Suite pytest cross-language (Python→Node)
│  └─ benchmarks/
│     └─ fletcher_bench.py     # Pruebas masivas, CSV y gráficas
├─ docs/
│  ├─ fletcher_stats.csv       # Resultados (se genera al correr el benchmark)
│  └─ plots/                   # Gráficas PNG (se generan al correr el benchmark)
├─ README.md                   # Este archivo
└─ requirements.txt            # Dependencias Python (pytest, matplotlib, etc.)
```

---

## ✅ Requisitos

* **Python 3.12 (64-bit recomendado)**

  > *Nota:* para generar gráficas con `matplotlib` en Windows, evita Python de 32-bit.
* **Node.js 14+** (se recomienda 18+)
* **pip** y **pytest**
* (Opcional) **Entorno virtual** (`venv`)

```bash
# Instalar pytest (si no usas requirements.txt)
python -m pip install --user pytest
```

> **Sugerencia (Windows/PowerShell):** crea un venv con Python 3.12 (64-bit):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 🚀 Instalación y Setup

### 1) Clonar el repositorio

```bash
git clone <URL-del-repo>
cd Lab2-Deteccion-Correccion-Errores
```

### 2) Instalar dependencias Python

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> Si no usas `requirements.txt`:
> `python -m pip install pytest matplotlib`

### 3) Iniciar el **receptor** (Node.js)

En **otra terminal**:

```bash
node detector/receiver/server.js --port 5000
```

Verás un mensaje de que está **escuchando** y aceptando JSON por línea (**JSONL**) en TCP.

---

## 🧪 Tests (cross-language)

Ejecuta la suite que valida emisor Python + receptor Node:

```bash
pytest detector/tests/test_fletcher_cross.py
# o en PowerShell
python -m pytest detector/tests/test_fletcher_cross.py
```

Debería mostrar algo como **27 passed**.

---

## ▶️ Emisor por capas (CLI)

Formato general:

```bash
python -m detector.emitter.main \
  --msg "Hola Mundo" \
  --alg fletcher \
  --block-size 8|16|32 \
  --ber 0.01 \
  --send-host 127.0.0.1 --send-port 5000
```

**PowerShell (una línea):**

```powershell
python -m detector.emitter.main --msg "Hola Mundo" --alg fletcher --block-size 16 --ber 0.01 --send-host 127.0.0.1 --send-port 5000
```

### Flips manuales (reproducibles)

* Un bit: `--flip-bits "0"`
* Dos bits: `--flip-bits "0,1"`

Ejemplo **1 bit** con bloque 8:

```powershell
python -m detector.emitter.main --msg "Hola Mundo" --alg fletcher --block-size 8 --ber 0.0 --flip-bits "0" --send-host 127.0.0.1 --send-port 5000
```

El emisor imprime:

* **Aplicación**: parámetros y BER
* **Presentación**: ASCII bytes (hex) y bits
* **Enlace**: trama emitida (hex/bits)
* **Ruido**: bits volteados y trama resultante
* **Transmisión**: respuesta JSON del receptor
* **Resumen**: original vs con ruido (hex)

---

## 📈 Pruebas masivas (benchmark)

Lanza el **receptor** primero:

```bash
node detector/receiver/server.js --port 5000
```

Corre el **benchmark**:

```powershell
python -m detector.benchmarks.fletcher_bench `
  --host 127.0.0.1 --port 5000 `
  --trials 1000 `
  --lengths 5,11,50 `
  --bers 0,0.001,0.01,0.05 `
  --blocks 8,16,32 `
  --seed 123 `
  --out-csv docs/fletcher_stats.csv `
  --plots-dir docs/plots
```

Genera:

* **CSV**: `docs/fletcher_stats.csv`
* **Gráficas** (PNG) en `docs/plots/`:

  * `detection_rate_len5.png`, `detection_rate_len11.png`, `detection_rate_len50.png`
  * `false_negative_rate_len5.png`, `false_negative_rate_len11.png`, `false_negative_rate_len50.png`

> El benchmark usa una **conexión TCP persistente** (JSONL) por combinación para evitar `WinError 10048` (puertos efímeros en `TIME_WAIT`).

---

## 📜 Licencia / Créditos

Proyecto académico para el curso de **Redes** – *Esquemas de Detección y Corrección de Errores*.
Autores: *Angel Herrarte y José Gramajo*.

---

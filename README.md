```markdown
# Lab2: Detección de errores con Fletcher Checksum

Este repositorio contiene la primera parte del Laboratorio 2 de **Esquemas de Detección y Corrección de Errores**, en el que implementamos el algoritmo **Fletcher Checksum** para detección de errores. El emisor está en **Python** y el receptor en **JavaScript (Node.js)**, cumpliendo la consigna de usar distintos lenguajes.

---

## 📁 Estructura del proyecto

```

Lab2-Deteccion-Correccion-Errores/
├── detector/
│   ├── **init**.py
│   ├── fletcher/
│   │   ├── **init**.py
│   │   ├── constants.py        # Tamaños de bloque permitidos
│   │   ├── emisor.py           # Emisor & funciones de cálculo (Python)
│   │   └── receptor.js         # Receptor (Node.js)
│   └── tests/
│       └── test\_fletcher\_cross.py  # Suite pytest cross‑language
├── docs/
│   └── reporte.pdf             # Informe de laboratorio
├── README.md                   # Este archivo
└── requirements.txt            # Dependencias Python

````

---

## ⚙️ Requisitos

- **Python 3.9+**  
- **Node.js 14+** (incluye `node`)  
- **pip** y **pytest**  
  ```bash
  python -m pip install --user pytest
````

* (Opcional) Entorno virtual para Python:

  ```bash
  python -m venv venv
  source venv/bin/activate     # Linux/macOS
  venv\Scripts\activate        # Windows
  ```

---

## 🚀 Instalación y Setup

1. **Clona el repositorio**

   ```bash
   git clone https://github.com/Abysswalkr/Lab2-Deteccion-Correccion-Errores.git
   cd Lab2-Deteccion-Correccion-Errores
   ```

2. **Instala dependencias Python**

   ```bash
   python -m pip install --user -r requirements.txt
   ```

3. **Verifica Node.js**

   ```bash
   node --version
   ```

---

## 🧩 Uso

### 1. Emisor (Python)

En Python puedes importar y usar el emisor:

```python
from detector.fletcher import emisor_fletcher

data = b"Hola Mundo"
frame = emisor_fletcher(data, block_size=16)
print(frame.hex())  # muestra data‖sum1‖sum2 en hexadecimal
```

### 2. Receptor (Node.js)

El receptor lee desde la línea de comandos:

```bash
# block_size ∈ {8,16,32}, hex_frame = frame.hex()
node detector/fletcher/receptor.js 16 486f6c61204d756e646f...
# → {"ok":true,"original":"486f6c61204d756e646f"}
```

Si `ok` es `false`, la trama fue descartada.

---

## ✅ Pruebas Automáticas

La suite `pytest` corre 27 casos (3 mensajes × 3 bloques × 3 escenarios):

```bash
# Ejecutar únicamente las pruebas Fletcher cross-language
python -m pytest detector/tests/test_fletcher_cross.py
```

O bien, para ejecutar todas las pruebas:

```bash
python -m pytest
```

Deberías ver:

```
collected 27 items
detector/tests/test_fletcher_cross.py ...........................
27 passed in 2.5s
```

---

## 📄 Documentación

* **Informe completo**: `docs/reporte.pdf`
  Contiene portadas, metodología, resultados (tablas y capturas), discusión de colisiones y comparativas.

* **Comentarios en el código**:
  Cada módulo incluye docstrings y comentarios que explican su propósito y funcionamiento.

---

## 🏷️ Licencia

Este código es parte de la asignatura CC3067 en la Universidad del Valle de Guatemala y está sujeto a políticas de uso académico interno.


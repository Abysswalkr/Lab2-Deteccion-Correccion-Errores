# Guía de Configuración Rápida

## ✅ Configuración del Entorno Completada

¡Tu entorno de Node.js y Python para el sistema de corrección de códigos Hamming está completamente configurado!

### Lo que se configuró:

1. **Configuración del Proyecto Node.js**
   - `package.json` con scripts y metadatos
   - Dependencias instaladas (ninguna requerida para este proyecto)
   - Scripts npm para ejecución fácil

2. **Entorno Python**
   - `requirements.txt` (sin dependencias externas necesarias)
   - Compatible con Python 3.6+

3. **Infraestructura de Pruebas**
   - `run-tests.sh` - Ejecutor de pruebas automatizado
   - Casos de prueba integrados en ambos ejecutables
   - Manejo completo de errores

4. **Documentación**
   - `README.md` - Guía completa de uso
   - `.gitignore` - Exclusiones apropiadas de control de versiones

### Comandos Rápidos:

```bash
# Ejecutar emisor (Node.js)
npm start                    # Pruebas por defecto
node emitter-hamming.js 1101 # Entrada personalizada

# Ejecutar receptor (Python)
npm run receptor            # Pruebas por defecto  
python3 receptor-hamming.py 0011101 # Entrada personalizada

# Ejecutar todas las pruebas
./run-tests.sh

# Ejemplo de flujo completo
node emitter-hamming.js 1101 | grep "TRAMA CODIFICADA"
python3 receptor-hamming.py 1010101
```

### Requisitos del Sistema Cumplidos:
- ✅ Node.js v23.11.0
- ✅ Python 3.13.3
- ✅ Todos los ejecutables funcionando correctamente
- ✅ Casos de prueba pasando

### Estructura de Archivos:
```
correction/
├── emitter-hamming.js    # Emisor Node.js
├── receptor-hamming.py   # Receptor Python
├── package.json          # Config Node.js
├── requirements.txt      # Dependencias Python
├── README.md            # Documentación
├── run-tests.sh         # Ejecutor de pruebas
├── .gitignore           # Exclusiones Git
└── SETUP.md            # Este archivo
```

¡Tu entorno está listo para usar! 🚀 
# Hamming Code Error Detection and Correction

This directory contains a complete Hamming code implementation with both emitter (Node.js) and receptor (Python) components.

## Prerequisites

### Node.js Setup
- Node.js version 14.0.0 or higher
- npm (comes with Node.js)

### Python Setup
- Python 3.6 or higher
- pip (Python package manager)

## Installation

### 1. Install Node.js Dependencies
```bash
npm install
```

### 2. Verify Python Installation
```bash
python3 --version
# or
python --version
```

## Usage

### Running the Emitter (Node.js)
The emitter creates Hamming codes from binary data:

```bash
# Run with default test cases
npm start

# Run with custom binary data
node emitter-hamming.js 1101

# Using npm script
npm run emitter 1101
```

### Running the Receptor (Python)
The receptor detects and corrects errors in Hamming codes:

```bash
# Run with default test cases
python3 receptor-hamming.py

# Run with custom Hamming code
python3 receptor-hamming.py 0011101

# Using npm script
npm run receptor 0011101
```

## Example Workflow

1. **Generate Hamming code:**
   ```bash
   node emitter-hamming.js 1101
   # Output: 0011101
   ```

2. **Detect/correct errors:**
   ```bash
   python3 receptor-hamming.py 0011101
   # Output: No errors detected, original data: 1101
   ```

3. **Test with error:**
   ```bash
   python3 receptor-hamming.py 0111101
   # Output: Error detected and corrected in position 2
   ```

## File Structure

- `emitter-hamming.js` - Node.js emitter that creates Hamming codes
- `receptor-hamming.py` - Python receptor that detects and corrects errors
- `package.json` - Node.js project configuration
- `requirements.txt` - Python dependencies (none required)
- `README.md` - This file

## Testing

Both executables include built-in test cases. Run them without arguments to see the test results:

```bash
# Test emitter
npm start

# Test receptor
python3 receptor-hamming.py
```

## Troubleshooting

### Node.js Issues
- Ensure Node.js is installed: `node --version`
- Install dependencies: `npm install`

### Python Issues
- Ensure Python 3.6+ is installed: `python3 --version`
- Use `python3` instead of `python` if needed
- No external dependencies required

### Permission Issues
- Make sure files are executable: `chmod +x *.js *.py`
- On Windows, use `node` and `python` commands directly 
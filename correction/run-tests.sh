#!/bin/bash

# Hamming Code Test Runner
# This script runs both the emitter and receptor with test cases

echo "=========================================="
echo "HAMMING CODE ERROR DETECTION & CORRECTION"
echo "=========================================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ Python version: $($PYTHON_CMD --version)"
echo ""

# Test 1: Basic functionality
echo "🧪 TEST 1: Basic Hamming Code Generation"
echo "----------------------------------------"
node emitter-hamming.js 1101
echo ""

# Test 2: Error-free reception
echo "🧪 TEST 2: Error-free Reception"
echo "--------------------------------"
$PYTHON_CMD receptor-hamming.py 0011101
echo ""

# Test 3: Error detection and correction
echo "🧪 TEST 3: Error Detection and Correction"
echo "----------------------------------------"
$PYTHON_CMD receptor-hamming.py 0111101
echo ""

# Test 4: Run built-in tests
echo "🧪 TEST 4: Built-in Test Cases"
echo "------------------------------"
echo "Emitter tests:"
node emitter-hamming.js
echo ""

echo "Receptor tests:"
$PYTHON_CMD receptor-hamming.py
echo ""

echo "=========================================="
echo "✅ All tests completed!"
echo "==========================================" 
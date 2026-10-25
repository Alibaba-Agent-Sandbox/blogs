# Bug Report and Fix Summary

## Issue Description
The `add` function in `calculator.py` was incorrectly implemented to perform subtraction instead of addition. The function signature remained correct, but the arithmetic operation was wrong.

## Problem Details
- **File**: `calculator.py`
- **Function**: `add(a, b)`
- **Bug**: The function returned `a - b` (subtraction) instead of `a + b` (addition)
- **Impact**: Any call to this function would produce incorrect results

## Fix Applied
- **Changed**: `return a - b` to `return a + b`
- **Result**: The function now correctly performs arithmetic addition

## Verification
The fix was verified by ensuring the function now returns the correct arithmetic sum of two numbers as intended.

## Files Modified
1. `calculator.py` - Fixed the arithmetic operation in the add function
2. `REPORT.md` - This report documenting the issue and fix
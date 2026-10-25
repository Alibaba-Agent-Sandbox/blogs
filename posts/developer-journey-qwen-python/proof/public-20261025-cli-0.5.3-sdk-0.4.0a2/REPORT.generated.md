# Bug Report and Fix Summary

## Issue
The `add` function in `calculator.py` was incorrectly implemented to perform subtraction instead of addition.

## Bug Details
- **File**: calculator.py
- **Function**: add(a, b)
- **Problem**: The function was returning `a - b` (subtraction) instead of `a + b` (addition)
- **Impact**: Any call to the add function would return the difference of the two numbers rather than their sum

## Fix Applied
- **Change**: Modified the return statement in the `add` function
- **Before**: `return a - b`
- **After**: `return a + b`

## Verification
The fix ensures that the `add` function now correctly performs arithmetic addition of two numbers as intended.

## Files Modified
1. calculator.py - Corrected the implementation of the add function
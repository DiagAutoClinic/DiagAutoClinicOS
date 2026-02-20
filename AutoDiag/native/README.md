# AutoDiag Native (C/C++)

This folder contains native C++ utilities for AutoDiag hardware validation.

## `j2534_native_probe`

A small Windows-native executable that validates a J2534 DLL can:

1. Load successfully.
2. Export required J2534 functions.
3. Open and close a PassThru device session.

This is useful when Python reports architecture or loader errors and you need low-level confirmation.

## Build (Windows)

- Configure with CMake and your preferred generator (Visual Studio recommended).
- Build target: `j2534_native_probe`.

## Usage

Run executable with a full path to a J2534 DLL:

`j2534_native_probe "C:\\path\\to\\vendor\\driver.dll"`

The tool prints JSON-like status output to stdout/stderr for easy scripting.

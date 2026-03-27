# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Initial responsibilities
- Zig toolchain policy checks
- bootstrap validation
- future ABI/layout guards
- artifact diff helpers for host-side tools

Rules
- keep helpers narrow and product-facing
- do not duplicate general Linux scripts here
- if a helper becomes broadly useful, move it or integrate it with the native subsystem flow

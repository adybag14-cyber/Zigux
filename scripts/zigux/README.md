# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Initial responsibilities
- Zig toolchain policy checks
- bootstrap validation
- committed parity fixture generation and checking
- future ABI/layout guards
- artifact diff helpers for host-side tools

Current bootstrap helpers
- `check-zig-toolchain.py`
- `validate-bootstrap.py`
- `install-zig.py`
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
- `check-phase2-cross.py`
- `check-phase3-abi.py`
- `check-phase3-bitmap-cpumask.py`
- `check-phase3-list-hlist.py`
- `check-phase3-errptr-xarray.py`
- `check-phase3-xarray-slot.py`
- `check-phase3-idr-slot.py`
- `check-phase3-ida-bitmap.py`
- `check-phase3-ida-alloc.py`
- `check-phase3-ida-range.py`
- `check-phase3-ida-range-set.py`
- `check-mk-elfconfig-diff.py`
- `fixdep.zig`
- `genksyms.zig`
- `genksyms_crc.zig`
- `kconfig/conf_bridge.zig`
- `kconfig/confdata_bridge.zig`
- `mk_elfconfig.zig`
- `artifact_diff.py`

Rules
- keep helpers narrow and product-facing
- do not duplicate general Linux scripts here
- if a helper becomes broadly useful, move it or integrate it with the native subsystem flow

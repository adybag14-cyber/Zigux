# Artifact Diff Policy

Zigux uses committed artifacts only when they anchor a bounded parity claim.

Current Phase 1 use
- `zigux/tests/fixtures/phase1_helpers.json` is generated from the in-tree C helper implementations.
- `scripts/zigux/check-phase1-parity.py` rebuilds that artifact and compares it against the committed JSON.
- `scripts/zigux/artifact_diff.py` is the generic comparison layer that future Phase 2 tooling work will reuse.

Current Phase 2 use
- `zigux/tests/fixtures/fixdep/sample_expected.txt` is generated from the current in-tree C `scripts/basic/fixdep.c` behavior on a bounded committed sample.
- `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt` widens that claim with a second committed depfile covering multi-target parsing, comments, duplicate deps, no-parse files, and escaped `#`.
- `scripts/zigux/check-fixdep-diff.py` compares the committed fixdep samples against both the C tool and `scripts/zigux/fixdep.zig`.
- `zigux/tests/fixtures/genksyms_bridge/*.json` capture bounded wrapper-first `genksyms` invocation planning for committed flag combinations.
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json` anchors the smallest wrapper-first `genksyms` invocation claim.
- `scripts/zigux/check-genksyms-bridge.py` compares those committed JSON fixtures against both a bounded C harness and `scripts/zigux/genksyms.zig`.
- `zigux/tests/fixtures/genksyms_crc/expected.json` is generated from a bounded C harness that ports the current `scripts/genksyms/genksyms.c` CRC logic over committed symbol-like input strings.
- `scripts/zigux/check-genksyms-crc-diff.py` compares that committed JSON against both the bounded C harness and `scripts/zigux/genksyms_crc.zig`.
- `zigux/tests/fixtures/kconfig_bridge/*.json` capture bounded wrapper-first `conf` / `confdata` bridge outputs for committed Kconfig inputs.
- `scripts/zigux/check-kconfig-bridge.py` compares those committed JSON fixtures against `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig`.
- `zigux/tests/fixtures/phase2_cross_targets.json` fixes the bounded cross-target compile set for the Phase 2 tool tranche.
- `zigux/tests/fixtures/mk_elfconfig/elf32_expected.json` and sibling JSON fixtures capture bounded stdin-driven behavior for `scripts/mod/mk_elfconfig.c`.
- `scripts/zigux/check-mk-elfconfig-diff.py` compares those committed JSON results against both the C tool and `scripts/zigux/mk_elfconfig.zig`.

Current Phase 3 use
- `zigux/tests/fixtures/phase3_abi/expected.json` fixes the first permanent C/Zigux ABI layout claim for the substrate skeleton.
- `scripts/zigux/check-phase3-abi.py` compares that committed JSON fixture against both the bounded C harness and the Zig substrate dump.
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json` fixes the first permanent bitmap/cpumask interop claim on top of that substrate.
- `scripts/zigux/check-phase3-bitmap-cpumask.py` compares that committed JSON fixture against both the bounded C harness and the Zig bitmap/cpumask dump.
- `zigux/tests/fixtures/phase3_list_hlist/expected.json` fixes the first permanent list/hlist interop claim on top of that substrate.
- `scripts/zigux/check-phase3-list-hlist.py` compares that committed JSON fixture against both the bounded C harness and the Zig list/hlist dump.
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json` fixes the first permanent err_ptr and encoded value-entry interop claim on top of that substrate.
- `scripts/zigux/check-phase3-errptr-xarray.py` compares that committed JSON fixture against both the bounded C harness and the Zig err_ptr/value-entry dump.
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json` fixes the first bounded xarray slot-array classification claim on top of the err_ptr/value-entry substrate.
- `scripts/zigux/check-phase3-xarray-slot.py` compares that committed JSON fixture against both the bounded C harness and the Zig xarray slot dump.

Rules
- artifact fixtures must be generated from the current in-tree source of truth
- fixture scope must stay small and reviewable
- fixture updates must be intentional and committed alongside the code change that caused them
- do not use opaque binary blobs for early bootstrap parity when a text or JSON artifact is possible

Near-term target
- reuse the same artifact-diff pattern for Phase 2 dual-implementation and bridge outputs such as `fixdep`, `genksyms`, `genksyms_crc`, `kconfig_bridge`, and `mk_elfconfig`
- keep using the same pattern for bounded Phase 3 ABI layout and bitmap/cpumask/list/hlist/err_ptr/value-entry/xarray-slot interop claims before any broader interop substrate expansion

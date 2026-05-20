# Zigux Alpha Bootstrap Commit Ledger

This ledger turns the roadmap into the first product commit train.

## Commit Train

1. `docs(zigux-alpha): establish roadmap and folder charter`
- `zigux-alpha/README.md`
- `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

2. `docs(zigux): add documentation root, review checklist, and freeze map`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/freeze-map.md`

3. `build(scripts/zigux): add bootstrap validation and toolchain checks`
- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/validate-bootstrap.py`

4. `test(zigux): establish differential-test root`
- `zigux/tests/README.md`

5. `ci(zigux): add bootstrap workflow`
- `.github/workflows/zigux-bootstrap.yml`

6. `feat(tools/lib): start phase-1 helper ports`
- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/string.zig`
- `tools/lib/rbtree.zig`

7. `test(zigux): add phase-1 helper harness and workflow gate`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/build.zig`
- `scripts/zigux/validate-phase1.py`
- `.github/workflows/zigux-bootstrap.yml`

8. `feat(tools/lib): expand phase-1 helper batch`
- `tools/lib/argv_split.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/hweight.zig`

9. `test(zigux): add phase-1 golden parity fixtures and artifact diff gate`
- `scripts/zigux/artifact_diff.py`
- `scripts/zigux/check-phase1-parity.py`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/phase1_helpers.zig`
- `.github/workflows/zigux-bootstrap.yml`

10. `feat(tools/lib): add phase-1 memory and formatting helper ports`
- `tools/lib/slab.zig`
- `tools/lib/str_error_r.zig`
- `tools/lib/vsprintf.zig`
- `tools/lib/zalloc.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/tests/fixtures/phase1_helpers.json`

11. `feat(scripts/zigux): add bounded Phase 2 fixdep dual-implementation lane`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/validate-phase2.py`
- `zigux/tests/fixtures/fixdep/sample.d`
- `zigux/tests/fixtures/fixdep/sample.c`
- `zigux/tests/fixtures/fixdep/sample.h`
- `zigux/tests/fixtures/fixdep/sample-config.h`
- `zigux/tests/fixtures/fixdep/sample.rmeta`
- `zigux/tests/fixtures/fixdep/sample_expected.txt`
- `.github/workflows/zigux-bootstrap.yml`

12. `feat(tools/lib): complete bounded phase-1 helper coverage`
- `tools/lib/list_sort.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/tests/fixtures/phase1_helpers.json`

13. `test(zigux): widen bounded fixdep parity fixtures`
- `zigux/tests/fixtures/fixdep/cases.json`
- `zigux/tests/fixtures/fixdep/sample_multi_target.d`
- `zigux/tests/fixtures/fixdep/sample2.c`
- `zigux/tests/fixtures/fixdep/sample2-config.h`
- `zigux/tests/fixtures/fixdep/shared#config.h`
- `zigux/tests/fixtures/fixdep/sample2.so`
- `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`

14. `feat(scripts/zigux): add bounded Phase 2 mk_elfconfig lane`
- `scripts/zigux/mk_elfconfig.zig`
- `scripts/zigux/check-mk-elfconfig-diff.py`
- `zigux/tests/fixtures/mk_elfconfig/cases.json`
- `zigux/tests/fixtures/mk_elfconfig/elf32.hex`
- `zigux/tests/fixtures/mk_elfconfig/elf64.hex`
- `zigux/tests/fixtures/mk_elfconfig/invalid_class.hex`
- `zigux/tests/fixtures/mk_elfconfig/not_elf.hex`
- `zigux/tests/fixtures/mk_elfconfig/truncated.hex`
- `zigux/tests/fixtures/mk_elfconfig/elf32_expected.json`
- `zigux/tests/fixtures/mk_elfconfig/elf64_expected.json`
- `zigux/tests/fixtures/mk_elfconfig/invalid_class_expected.json`
- `zigux/tests/fixtures/mk_elfconfig/not_elf_expected.json`
- `zigux/tests/fixtures/mk_elfconfig/truncated_expected.json`
- `.github/workflows/zigux-bootstrap.yml`

15. `docs(zigux): close bounded phase-1 helper tranche`
- `Documentation/zigux/phase1-closure.md`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

16. `test(zigux): harden phase-1 closure gates`
- `scripts/zigux/check-phase1-bench.py`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `scripts/zigux/validate-phase1-closure.py`
- `.github/workflows/zigux-bootstrap.yml`

17. `ci(zigux): harden phase-1 closure workflow viability`
- `.github/workflows/zigux-bootstrap.yml`
- `Documentation/zigux/phase1-closure.md`
- `scripts/zigux/validate-phase1-closure.py`

18. `build(zigux): remove node-20-bound Zig action from phase-1 closure path`
- `scripts/zigux/install-zig.py`
- `.github/workflows/zigux-bootstrap.yml`
- `scripts/zigux/validate-phase1-closure.py`

19. `feat(scripts/zigux): start bounded Phase 2 genksyms lane`
- `scripts/zigux/genksyms_crc.zig`
- `scripts/zigux/check-genksyms-crc-diff.py`
- `zigux/tests/fixtures/genksyms_crc/genksyms_crc_c_harness.c`
- `zigux/tests/fixtures/genksyms_crc/inputs.txt`
- `zigux/tests/fixtures/genksyms_crc/expected.json`
- `.github/workflows/zigux-bootstrap.yml`

20. `feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/check-kconfig-bridge.py`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/kconfig_bridge/olddefconfig_expected.json`
- `zigux/tests/fixtures/kconfig_bridge/syncconfig_expected.json`
- `zigux/tests/fixtures/kconfig_bridge/sample.config`
- `zigux/tests/fixtures/kconfig_bridge/sample_expected.json`

21. `ci(zigux): add Phase 2 cross-arch build matrix`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `.github/workflows/zigux-bootstrap.yml`

22. `docs(zigux): close bounded Phase 2 toolchain tranche`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

23. `feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/check-genksyms-bridge.py`
- `zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`

24. `ci(zigux): widen Phase 2 closure matrix`
- `.github/workflows/zigux-bootstrap.yml`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`

25. `docs(zigux): reopen and close broadened Phase 2 tranche`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/artifact-diff.md`
- `scripts/zigux/README.md`
- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- current direct-readback note: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/README.md`, and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` are directly readable on current `master`
- current direct-readback note: `Documentation/zigux/artifact-diff.md` is still absent on current `master`, so keep this broadened Phase 2 tranche framed as the target same-lane packet rather than fully landed current-master evidence until that companion returns

## Scope Note

- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.
- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.

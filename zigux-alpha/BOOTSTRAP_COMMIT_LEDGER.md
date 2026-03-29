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

26. `feat(zigux): start bounded Phase 3 abi substrate skeleton`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/helpers/layout_assert.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/uapi/version.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/check-phase3-abi.py`
- `scripts/zigux/validate-phase3.py`
- `Documentation/zigux/phase3-abi-slice.md`
- `zigux/Makefile`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

27. `feat(zigux): add bounded Phase 3 bitmap/cpumask interop slice`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

28. `feat(zigux): add bounded Phase 3 list/hlist interop slice`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
- `zigux/tests/fixtures/phase3_list_hlist_manifest.json`
- `scripts/zigux/check-phase3-list-hlist.py`
- `Documentation/zigux/phase3-list-hlist-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/unsafe/narrow.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

29. `feat(zigux): add bounded Phase 3 err_ptr/xarray interop slice`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_errptr_xarray_dump.zig`
- `zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c`
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json`
- `zigux/tests/fixtures/phase3_errptr_xarray_manifest.json`
- `scripts/zigux/check-phase3-errptr-xarray.py`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

30. `feat(zigux): add bounded Phase 3 xarray slot interop slice`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json`
- `zigux/tests/fixtures/phase3_xarray_slot_manifest.json`
- `scripts/zigux/check-phase3-xarray-slot.py`
- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

31. `feat(zigux): add bounded Phase 3 idr slot interop slice`
- `zigux/helpers/idr_slot_view.zig`
- `zigux/tests/phase3_idr_slot_dump.zig`
- `zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_idr_slot/expected.json`
- `zigux/tests/fixtures/phase3_idr_slot_manifest.json`
- `scripts/zigux/check-phase3-idr-slot.py`
- `Documentation/zigux/phase3-idr-slot-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

32. `feat(zigux): add bounded Phase 3 ida bitmap interop slice`
- `zigux/helpers/ida_bitmap_view.zig`
- `zigux/tests/phase3_ida_bitmap_dump.zig`
- `zigux/tests/fixtures/phase3_ida_bitmap/phase3_ida_bitmap_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_bitmap/expected.json`
- `zigux/tests/fixtures/phase3_ida_bitmap_manifest.json`
- `scripts/zigux/check-phase3-ida-bitmap.py`
- `Documentation/zigux/phase3-ida-bitmap-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

33. `feat(zigux): add bounded Phase 3 ida allocation interop slice`
- `zigux/helpers/ida_alloc_view.zig`
- `zigux/tests/phase3_ida_alloc_dump.zig`
- `zigux/tests/fixtures/phase3_ida_alloc/phase3_ida_alloc_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_alloc/expected.json`
- `zigux/tests/fixtures/phase3_ida_alloc_manifest.json`
- `scripts/zigux/check-phase3-ida-alloc.py`
- `Documentation/zigux/phase3-ida-alloc-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

34. `feat(zigux): add bounded Phase 3 ida range interop slice`
- `zigux/helpers/ida_range_view.zig`
- `zigux/tests/phase3_ida_range_dump.zig`
- `zigux/tests/fixtures/phase3_ida_range/phase3_ida_range_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_range/expected.json`
- `zigux/tests/fixtures/phase3_ida_range_manifest.json`
- `scripts/zigux/check-phase3-ida-range.py`
- `Documentation/zigux/phase3-ida-range-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

35. `feat(zigux): add bounded Phase 3 ida range-set interop slice`
- `zigux/helpers/ida_range_set_view.zig`
- `zigux/tests/phase3_ida_range_set_dump.zig`
- `zigux/tests/fixtures/phase3_ida_range_set/phase3_ida_range_set_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_range_set/expected.json`
- `zigux/tests/fixtures/phase3_ida_range_set_manifest.json`
- `scripts/zigux/check-phase3-ida-range-set.py`
- `Documentation/zigux/phase3-ida-range-set-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

36. `feat(zigux): add bounded Phase 3 ida policy interop slice`
- `zigux/helpers/ida_policy_view.zig`
- `zigux/tests/phase3_ida_policy_dump.zig`
- `zigux/tests/fixtures/phase3_ida_policy/phase3_ida_policy_c_harness.c`
- `zigux/tests/fixtures/phase3_ida_policy/expected.json`
- `zigux/tests/fixtures/phase3_ida_policy_manifest.json`
- `scripts/zigux/check-phase3-ida-policy.py`
- `Documentation/zigux/phase3-ida-policy-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

37. `feat(zigux): add bounded Phase 3 minor alloc interop slice`
- `zigux/helpers/minor_alloc_plan.zig`
- `zigux/tests/phase3_minor_alloc_dump.zig`
- `zigux/tests/fixtures/phase3_minor_alloc/phase3_minor_alloc_c_harness.c`
- `zigux/tests/fixtures/phase3_minor_alloc/expected.json`
- `zigux/tests/fixtures/phase3_minor_alloc_manifest.json`
- `scripts/zigux/check-phase3-minor-alloc.py`
- `Documentation/zigux/phase3-minor-alloc-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

38. `feat(zigux): add bounded Phase 3 dev region interop slice`
- `zigux/helpers/dev_region_plan.zig`
- `zigux/tests/phase3_dev_region_dump.zig`
- `zigux/tests/fixtures/phase3_dev_region/phase3_dev_region_c_harness.c`
- `zigux/tests/fixtures/phase3_dev_region/expected.json`
- `zigux/tests/fixtures/phase3_dev_region_manifest.json`
- `scripts/zigux/check-phase3-dev-region.py`
- `Documentation/zigux/phase3-dev-region-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

39. `feat(zigux): add bounded Phase 3 cdev add interop slice`
- `zigux/helpers/cdev_add_plan.zig`
- `zigux/tests/phase3_cdev_add_dump.zig`
- `zigux/tests/fixtures/phase3_cdev_add/phase3_cdev_add_c_harness.c`
- `zigux/tests/fixtures/phase3_cdev_add/expected.json`
- `zigux/tests/fixtures/phase3_cdev_add_manifest.json`
- `scripts/zigux/check-phase3-cdev-add.py`
- `Documentation/zigux/phase3-cdev-add-slice.md`

40. `feat(zigux): add bounded Phase 3 cdev lookup interop slice`
- `zigux/helpers/cdev_lookup_plan.zig`
- `zigux/tests/phase3_cdev_lookup_dump.zig`
- `zigux/tests/fixtures/phase3_cdev_lookup/phase3_cdev_lookup_c_harness.c`
- `zigux/tests/fixtures/phase3_cdev_lookup/expected.json`
- `zigux/tests/fixtures/phase3_cdev_lookup_manifest.json`
- `scripts/zigux/check-phase3-cdev-lookup.py`
- `Documentation/zigux/phase3-cdev-lookup-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

41. `feat(zigux): add bounded Phase 3 chrdev open interop slice`
- `zigux/helpers/chrdev_open_plan.zig`
- `zigux/tests/phase3_chrdev_open_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_open/phase3_chrdev_open_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_open/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_open_manifest.json`
- `scripts/zigux/check-phase3-chrdev-open.py`
- `Documentation/zigux/phase3-chrdev-open-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

42. `feat(zigux): add bounded Phase 3 chrdev fops interop slice`
- `zigux/helpers/chrdev_fops_plan.zig`
- `zigux/tests/phase3_chrdev_fops_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_fops/phase3_chrdev_fops_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_fops/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_fops_manifest.json`
- `scripts/zigux/check-phase3-chrdev-fops.py`
- `Documentation/zigux/phase3-chrdev-fops-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

43. `feat(zigux): add bounded Phase 3 chrdev route interop slice`
- `zigux/helpers/chrdev_route_plan.zig`
- `zigux/tests/phase3_chrdev_route_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_route/phase3_chrdev_route_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_route/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_route_manifest.json`
- `scripts/zigux/check-phase3-chrdev-route.py`
- `Documentation/zigux/phase3-chrdev-route-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

44. `feat(zigux): add bounded Phase 3 chrdev io interop slice`
- `zigux/helpers/chrdev_io_plan.zig`
- `zigux/tests/phase3_chrdev_io_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_io/phase3_chrdev_io_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_io/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_io_manifest.json`
- `scripts/zigux/check-phase3-chrdev-io.py`
- `Documentation/zigux/phase3-chrdev-io-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

45. `feat(zigux): add bounded Phase 3 chrdev xfer interop slice`
- `zigux/helpers/chrdev_xfer_plan.zig`
- `zigux/tests/phase3_chrdev_xfer_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_xfer/phase3_chrdev_xfer_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_xfer/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_xfer_manifest.json`
- `scripts/zigux/check-phase3-chrdev-xfer.py`
- `Documentation/zigux/phase3-chrdev-xfer-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

46. `feat(zigux): add bounded Phase 3 chrdev resume interop slice`
- `zigux/helpers/chrdev_resume_plan.zig`
- `zigux/tests/phase3_chrdev_resume_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_resume/phase3_chrdev_resume_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_resume/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_resume_manifest.json`
- `scripts/zigux/check-phase3-chrdev-resume.py`
- `Documentation/zigux/phase3-chrdev-resume-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

47. `feat(zigux): add bounded Phase 3 chrdev retry interop slice`
- `zigux/helpers/chrdev_retry_plan.zig`
- `zigux/tests/phase3_chrdev_retry_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_retry/phase3_chrdev_retry_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_retry/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_retry_manifest.json`
- `scripts/zigux/check-phase3-chrdev-retry.py`
- `Documentation/zigux/phase3-chrdev-retry-slice.md`

### `feat(zigux): add bounded Phase 3 chrdev requeue interop slice`
- `zigux/helpers/chrdev_requeue_plan.zig`
- `zigux/tests/phase3_chrdev_requeue_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_requeue/phase3_chrdev_requeue_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_requeue/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_requeue_manifest.json`
- `scripts/zigux/check-phase3-chrdev-requeue.py`
- `Documentation/zigux/phase3-chrdev-requeue-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev complete interop slice`
- `zigux/helpers/chrdev_complete_plan.zig`
- `zigux/tests/phase3_chrdev_complete_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_complete/phase3_chrdev_complete_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_complete/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_complete_manifest.json`
- `scripts/zigux/check-phase3-chrdev-complete.py`
- `Documentation/zigux/phase3-chrdev-complete-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify interop slice`
- `zigux/helpers/chrdev_notify_plan.zig`
- `zigux/tests/phase3_chrdev_notify_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify/phase3_chrdev_notify_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify.py`
- `Documentation/zigux/phase3-chrdev-notify-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify policy interop slice`
- `zigux/helpers/chrdev_notify_policy_plan.zig`
- `zigux/tests/phase3_chrdev_notify_policy_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_policy/phase3_chrdev_notify_policy_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_policy/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_policy_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-policy.py`
- `Documentation/zigux/phase3-chrdev-notify-policy-slice.md`
### `feat(zigux): add bounded Phase 3 chrdev notify budget interop slice`
- `zigux/helpers/chrdev_notify_budget_plan.zig`
- `zigux/tests/phase3_chrdev_notify_budget_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_budget/phase3_chrdev_notify_budget_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_budget/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_budget_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-budget.py`
- `Documentation/zigux/phase3-chrdev-notify-budget-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack interop slice`
- `zigux/helpers/chrdev_notify_ack_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack/phase3_chrdev_notify_ack_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack policy interop slice`
- `zigux/helpers/chrdev_notify_ack_policy_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_policy_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_policy/phase3_chrdev_notify_ack_policy_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_policy/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_policy_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-policy.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-policy-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`
- `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack budget interop slice`
- `zigux/helpers/chrdev_notify_ack_budget_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_budget_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_budget/phase3_chrdev_notify_ack_budget_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_budget/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_budget_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-budget.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-budget-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window interop slice`
- `zigux/helpers/chrdev_notify_ack_window_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window/phase3_chrdev_notify_ack_window_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy/phase3_chrdev_notify_ack_window_policy_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy budget interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget/phase3_chrdev_notify_ack_window_policy_budget_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy budget window interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window/phase3_chrdev_notify_ack_window_policy_budget_window_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window.py`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-slice.md`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy budget window delivery window interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy budget window delivery window budget interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy budget window delivery window budget window interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy budget window delivery window budget window delivery interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan.zig`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan.zig`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_manifest.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_manifest.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery.py`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window.py`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack window policy budget window delivery window budget window delivery window interop slice`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan.zig`
- `zigux/helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump.zig`
- `zigux/tests/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_manifest.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window.py`
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`

### `feat(zigux): add bounded Phase 3 chrdev notify ack delivery budget guard interop slice`
- `zigux/helpers/chrdev_notify_ack_delivery_budget_guard_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_delivery_budget_guard_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard/phase3_chrdev_notify_ack_delivery_budget_guard_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `scripts/zigux/validate-phase3.py`
- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

### `feat(zigux): add bounded Phase 3 chrdev notify ack delivery budget guard window interop slice`
- `zigux/helpers/chrdev_notify_ack_delivery_budget_guard_window_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_delivery_budget_guard_window_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window/phase3_chrdev_notify_ack_delivery_budget_guard_window_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window/phase3_chrdev_notify_ack_delivery_budget_guard_window_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`

### `feat(zigux): add bounded Phase 3 chrdev notify ack delivery budget guard window policy interop slice`
- `zigux/helpers/chrdev_notify_ack_delivery_budget_guard_window_policy_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `scripts/zigux/validate-phase3.py`
- `Documentation/zigux/README.md`
- `Documentation/zigux/artifact-diff.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

### `feat(zigux): add bounded Phase 3 chrdev notify ack delivery budget guard window policy budget interop slice`
- `zigux/helpers/chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.zig`
- `zigux/tests/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_c_harness.c`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget/expected.json`
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_manifest.json`
- `scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget.py`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-slice.md`
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/bindings/abi.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/build.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `scripts/zigux/validate-phase3.py`
- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

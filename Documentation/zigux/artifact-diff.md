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
- `zigux/tests/fixtures/phase3_idr_slot/expected.json` fixes the first bounded idr-style slot classification claim on top of the xarray-slot substrate.
- `scripts/zigux/check-phase3-idr-slot.py` compares that committed JSON fixture against both the bounded C harness and the Zig idr slot dump.
- `zigux/tests/fixtures/phase3_ida_bitmap/expected.json` fixes the first bounded ida-style bitmap allocation-state claim on top of the bitmap and idr substrates.
- `scripts/zigux/check-phase3-ida-bitmap.py` compares that committed JSON fixture against both the bounded C harness and the Zig ida bitmap dump.
- `zigux/tests/fixtures/phase3_ida_alloc/expected.json` fixes the first bounded ida-style first-fit allocation-planning claim on top of the ida bitmap substrate.
- `scripts/zigux/check-phase3-ida-alloc.py` compares that committed JSON fixture against both the bounded C harness and the Zig ida allocation dump.
- `zigux/tests/fixtures/phase3_ida_range/expected.json` fixes the first bounded ida-style candidate-range planning claim on top of the ida allocation substrate.
- `scripts/zigux/check-phase3-ida-range.py` compares that committed JSON fixture against both the bounded C harness and the Zig ida range dump.
- `zigux/tests/fixtures/phase3_ida_range_set/expected.json` fixes the first bounded ida-style non-overlapping range-set selection claim on top of the ida range substrate.
- `scripts/zigux/check-phase3-ida-range-set.py` compares that committed JSON fixture against both the bounded C harness and the Zig ida range-set dump.
- `zigux/tests/fixtures/phase3_ida_policy/expected.json` fixes the first bounded ida-style fit-policy selection claim on top of the ida allocation and range substrates.
- `scripts/zigux/check-phase3-ida-policy.py` compares that committed JSON fixture against both the bounded C harness and the Zig ida policy dump.
- `zigux/tests/fixtures/phase3_minor_alloc/expected.json` fixes the first bounded kernel-facing device-minor allocation-planning claim on top of the ida policy substrate.
- `scripts/zigux/check-phase3-minor-alloc.py` compares that committed JSON fixture against both the bounded C harness and the Zig minor allocation dump.
- `zigux/tests/fixtures/phase3_dev_region/expected.json` fixes the first bounded kernel-facing device-region planning claim on top of the minor allocation substrate.
- `scripts/zigux/check-phase3-dev-region.py` compares that committed JSON fixture against both the bounded C harness and the Zig dev-region planning dump.
- `zigux/tests/fixtures/phase3_cdev_add/expected.json` fixes the first bounded kernel-facing cdev-add planning claim on top of the device-region substrate.
- `scripts/zigux/check-phase3-cdev-add.py` compares that committed JSON fixture against both the bounded C harness and the Zig cdev-add planning dump.
- `zigux/tests/fixtures/phase3_cdev_lookup/expected.json` fixes the first bounded kernel-facing cdev-lookup planning claim on top of the cdev-add substrate.
- `scripts/zigux/check-phase3-cdev-lookup.py` compares that committed JSON fixture against both the bounded C harness and the Zig cdev-lookup planning dump.
- `zigux/tests/fixtures/phase3_chrdev_open/expected.json` fixes the first bounded kernel-facing chrdev-open planning claim on top of the cdev-lookup substrate.
- `scripts/zigux/check-phase3-chrdev-open.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-open planning dump.
- `zigux/tests/fixtures/phase3_chrdev_fops/expected.json` fixes the first bounded kernel-facing chrdev-fops planning claim on top of the chrdev-open substrate.
- `scripts/zigux/check-phase3-chrdev-fops.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-fops planning dump.
- `zigux/tests/fixtures/phase3_chrdev_route/expected.json` fixes the bounded kernel-facing chrdev-route planning claim on top of the chrdev-fops substrate.
- `scripts/zigux/check-phase3-chrdev-route.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-route planning dump.
- `zigux/tests/fixtures/phase3_chrdev_io/expected.json` fixes the bounded kernel-facing chrdev-io planning claim on top of the chrdev-route substrate.
- `scripts/zigux/check-phase3-chrdev-io.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-io planning dump.
- `zigux/tests/fixtures/phase3_chrdev_xfer/expected.json` fixes the bounded kernel-facing chrdev-xfer planning claim on top of the chrdev-io substrate.
- `scripts/zigux/check-phase3-chrdev-xfer.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-xfer planning dump.
- `zigux/tests/fixtures/phase3_chrdev_resume/expected.json` fixes the bounded kernel-facing chrdev-resume planning claim on top of the chrdev-xfer substrate.
- `scripts/zigux/check-phase3-chrdev-resume.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-resume planning dump.
- `zigux/tests/fixtures/phase3_chrdev_retry/expected.json` fixes the bounded kernel-facing chrdev-retry planning claim on top of the chrdev-resume substrate.
- `scripts/zigux/check-phase3-chrdev-retry.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-retry planning dump.
- `zigux/tests/fixtures/phase3_chrdev_requeue/expected.json` fixes the bounded kernel-facing chrdev-requeue planning claim on top of the chrdev-retry substrate.
- `scripts/zigux/check-phase3-chrdev-requeue.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-requeue planning dump.
- `zigux/tests/fixtures/phase3_chrdev_complete/expected.json` fixes the bounded kernel-facing chrdev-complete planning claim on top of the chrdev-requeue substrate.
- `scripts/zigux/check-phase3-chrdev-complete.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-complete planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify/expected.json` fixes the bounded kernel-facing chrdev-notify planning claim on top of the chrdev-complete substrate.
- `scripts/zigux/check-phase3-chrdev-notify.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_policy/expected.json` fixes the bounded kernel-facing chrdev-notify-policy planning claim on top of the chrdev-notify substrate.
- `scripts/zigux/check-phase3-chrdev-notify-policy.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-policy planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_budget/expected.json` fixes the bounded kernel-facing chrdev-notify-budget planning claim on top of the chrdev-notify-policy substrate.
- `scripts/zigux/check-phase3-chrdev-notify-budget.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-budget planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack/expected.json` fixes the bounded kernel-facing chrdev-notify-ack planning claim on top of the chrdev-notify-budget substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_policy/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-policy planning claim on top of the chrdev-notify-ack substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-policy.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-policy planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_budget/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-budget planning claim on top of the chrdev-notify-ack-policy substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-budget.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-budget planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window planning claim on top of the chrdev-notify-ack-budget substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy planning claim on top of the chrdev-notify-ack-window substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget planning claim on top of the chrdev-notify-ack-window-policy substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window planning claim on top of the chrdev-notify-ack-window-policy-budget substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window-delivery planning claim on top of the chrdev-notify-ack-window-policy-budget-window substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window-delivery planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window-delivery-window planning claim on top of the chrdev-notify-ack-window-policy-budget-window-delivery substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window-delivery-window planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window-delivery-window-budget planning claim on top of the chrdev-notify-ack-window-policy-budget-window-delivery-window substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window-delivery-window-budget planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window planning claim on top of the chrdev-notify-ack-window-policy-budget-window-delivery-window-budget substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery planning claim on top of the chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window substrate.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window planning claim on top of the chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window substrate.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget planning claim on top of the chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery planning dump.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window planning dump.
- `scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-delivery-budget-guard planning claim on top of the stable final delivery-budget substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-delivery-budget-guard planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-delivery-budget-guard-window planning claim on top of the stable delivery-budget-guard substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-delivery-budget-guard-window planning dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy/expected.json` fixes the bounded kernel-facing chrdev-notify-ack-delivery-budget-guard-window-policy planning claim on top of the stable delivery-budget-guard-window substrate.
- `scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy.py` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev-notify-ack-delivery-budget-guard-window-policy planning dump.

Rules
- artifact fixtures must be generated from the current in-tree source of truth
- fixture scope must stay small and reviewable
- fixture updates must be intentional and committed alongside the code change that caused them
- do not use opaque binary blobs for early bootstrap parity when a text or JSON artifact is possible

Near-term target
- reuse the same artifact-diff pattern for Phase 2 dual-implementation and bridge outputs such as `fixdep`, `genksyms`, `genksyms_crc`, `kconfig_bridge`, and `mk_elfconfig`
- keep using the same pattern for bounded Phase 3 ABI layout and bitmap/cpumask/list/hlist/err_ptr/value-entry/xarray-slot/idr-slot/ida-bitmap/ida-alloc/ida-range/ida-range-set/ida-policy/minor-alloc/dev-region/cdev-add/cdev-lookup/chrdev-open/chrdev-fops/chrdev-route/chrdev-io/chrdev-xfer/chrdev-resume/chrdev-retry/chrdev-requeue/chrdev-complete/chrdev-notify/chrdev-notify-policy/chrdev-notify-budget/chrdev-notify-ack/chrdev-notify-ack-policy/chrdev-notify-ack-budget/chrdev-notify-ack-window/chrdev-notify-ack-window-policy/chrdev-notify-ack-window-policy-budget/chrdev-notify-ack-window-policy-budget-window interop claims before any broader interop substrate expansion

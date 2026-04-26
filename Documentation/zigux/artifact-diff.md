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
- `zigux/tests/fixtures/phase3_abi/expected.json` anchors the bounded Phase 3 ABI layout parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug abi` compares that committed JSON fixture against both the bounded C harness and the Zig ABI layout dump.
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json` anchors the bounded Phase 3 bitmap/cpumask parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug bitmap-cpumask` compares that committed JSON fixture against both the bounded C harness and the Zig bitmap/cpumask dump.
- `zigux/tests/fixtures/phase3_cdev_add/expected.json` anchors the bounded Phase 3 cdev add parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug cdev-add` compares that committed JSON fixture against both the bounded C harness and the Zig cdev add dump.
- `zigux/tests/fixtures/phase3_cdev_lookup/expected.json` anchors the bounded Phase 3 cdev lookup parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug cdev-lookup` compares that committed JSON fixture against both the bounded C harness and the Zig cdev lookup dump.
- `zigux/tests/fixtures/phase3_chrdev_complete/expected.json` anchors the bounded Phase 3 chrdev complete parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-complete` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev complete dump.
- `zigux/tests/fixtures/phase3_chrdev_fops/expected.json` anchors the bounded Phase 3 chrdev fops parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-fops` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev fops dump.
- `zigux/tests/fixtures/phase3_chrdev_io/expected.json` anchors the bounded Phase 3 chrdev io parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-io` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev io dump.
- `zigux/tests/fixtures/phase3_chrdev_notify/expected.json` anchors the bounded Phase 3 chrdev notify parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack/expected.json` anchors the bounded Phase 3 chrdev notify ack parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_budget/expected.json` anchors the bounded Phase 3 chrdev notify ack budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget windo|
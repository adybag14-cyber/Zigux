# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Scope

  * is the target phase named explicitly?
  * is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?
  * is the Linux anchor file or tree path named directly?
## Safety

  * does the change avoid mirror-tree sprawl?
  * is real code co-located with the owning Linux subsystem when appropriate?
  * does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?
## Validation
  * are parity tests or fixture checks included?
  * is there a stated performance gate if the code is algorithmic, queueing-sensitive, or driver-facing?
  * is there a stated rollback owner and fallback path?
  * if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/zig-toolchain-policy.json`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` still agree on the same current directly readable Phase 2 toolchain, kbuild, and kconfig bridge packet, while `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` stay framed as historical packet members rather than shipped current-`master` evidence until those routes are republished?
## ABI and Runtime

  * are bindings and ABI assumptions centralized?
  * does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?
  * if unsafe code exists, is it narrow, visible, and review-owned?
## Product Discipline

  * does the patch make Zigux more buildable, more testable, or more reviewable?
  * if it came from ZAR research, is the transfer rationale explicit?
  * if the target stays in C, does the change record that ongoing policy honestly instead of implying a premature port commitment?
  * does the change strengthen the product repo instead of just extending experimental scope?
## Footer

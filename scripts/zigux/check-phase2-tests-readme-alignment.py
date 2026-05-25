#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
REQUIRED_TESTS_README_MARKERS = (
    "Phase 2 review packet",
    "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "`third_party/README.md`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`scripts/zigux/fixdep.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/Makefile`",
    "current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)
EXACT_COUNT_TESTS_README_MARKERS = (
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
)
FORBIDDEN_TESTS_README_MARKERS = (
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "keep the fixture-backed tool-manifest and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as historical packet members rather than shipped current-`master` evidence",
)
REQUIRED_DOCS_ROOT_MARKERS = (
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/validate-phase2.py`",
    "keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain, shared-reminder, and manifest guards, the selected kconfig bridge helpers, the bounded genksyms bridge helper packet, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.",
    "the current docs-root Phase 2 reminder packet should stay parked on `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/Makefile`, with `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, the current kconfig bridge manifests, and the current genksyms bridge fixture roster keeping the same packet aligned across docs-root, scripts-root, and tests-root surfaces.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
)
REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/fixdep/cases.json",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def resolve_path(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def collect_manifest_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        strings: set[str] = set()
        for item in value:
            strings.update(collect_manifest_strings(item))
        return strings
    if isinstance(value, dict):
        strings: set[str] = set()
        for item in value.values():
            strings.update(collect_manifest_strings(item))
        return strings
    return set()


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_missing_manifest_surfaces(strings: set[str]) -> list[tuple[str, str]]:
    return [
        ("MISSING_PHASE2_TOOL_MANIFEST_SURFACES", surface)
        for surface in REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES
        if surface not in strings
    ]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    docs_root_text = read_text(resolve_path(root, DOCS_ROOT_README))
    phase2_tool_manifest = read_manifest(resolve_path(root, PHASE2_TOOL_MANIFEST))
    manifest_strings = collect_manifest_strings(phase2_tool_manifest)
    issues = collect_missing_markers(tests_readme_text, REQUIRED_TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS")
    issues.extend(collect_exact_count_markers(tests_readme_text, EXACT_COUNT_TESTS_README_MARKERS, "EXACT_COUNT_TESTS_README_MARKERS"))
    issues.extend(collect_forbidden_markers(tests_readme_text, FORBIDDEN_TESTS_README_MARKERS, "FORBIDDEN_TESTS_README_MARKERS"))
    issues.extend(collect_missing_markers(docs_root_text, REQUIRED_DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKERS"))
    issues.extend(collect_missing_manifest_surfaces(manifest_strings))
    if phase2_tool_manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_PHASE2_TOOL_MANIFEST_GAPS", json.dumps(phase2_tool_manifest.get("repo_reality_gaps"), sort_keys=True)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TESTS_README_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, TESTS_README), "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
    write_text(
        resolve_path(root, PHASE2_TOOL_MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {"all": list(REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES)},
                "repo_reality_gaps": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def remove_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(EXACT_COUNT_TESTS_README_MARKERS)
        + len(FORBIDDEN_TESTS_README_MARKERS)
        + len(REQUIRED_DOCS_ROOT_MARKERS)
        + len(REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES)
        + 1
    )
    with tempfile.TemporaryDirectory(prefix="zigux_p2_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)

        assert collect_issues(root) == []
        checks_run += 1

        tests_readme_path = resolve_path(root, TESTS_README)
        tests_readme_text = read_text(tests_readme_path)
        for marker in REQUIRED_TESTS_README_MARKERS:
            write_text(tests_readme_path, remove_all(tests_readme_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues, (marker, issues)
            build_self_test_root(root)
            tests_readme_text = read_text(tests_readme_path)
            checks_run += 1

        for marker in EXACT_COUNT_TESTS_README_MARKERS:
            write_text(tests_readme_path, tests_readme_text + marker + "\n")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_TESTS_README_MARKERS", f"2::{marker}") in issues, (marker, issues)
            build_self_test_root(root)
            tests_readme_text = read_text(tests_readme_path)
            checks_run += 1

        for marker in FORBIDDEN_TESTS_README_MARKERS:
            write_text(tests_readme_path, tests_readme_text + marker + "\n")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_README_MARKERS", marker) in issues, (marker, issues)
            build_self_test_root(root)
            tests_readme_text = read_text(tests_readme_path)
            checks_run += 1

        docs_root_path = resolve_path(root, DOCS_ROOT_README)
        docs_root_text = read_text(docs_root_path)
        for marker in REQUIRED_DOCS_ROOT_MARKERS:
            write_text(docs_root_path, remove_all(docs_root_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_DOCS_ROOT_MARKERS", marker) in issues, (marker, issues)
            build_self_test_root(root)
            docs_root_text = read_text(docs_root_path)
            checks_run += 1

        manifest_path = resolve_path(root, PHASE2_TOOL_MANIFEST)
        manifest = read_manifest(manifest_path)
        for surface in REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES:
            manifest["present_surfaces"]["all"] = [
                entry for entry in manifest["present_surfaces"]["all"] if entry != surface
            ]
            write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            issues = collect_issues(root)
            assert ("MISSING_PHASE2_TOOL_MANIFEST_SURFACES", surface) in issues, (surface, issues)
            build_self_test_root(root)
            manifest = read_manifest(manifest_path)
            checks_run += 1

        manifest["repo_reality_gaps"] = ["gap"]
        write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert ("NONEMPTY_PHASE2_TOOL_MANIFEST_GAPS", json.dumps(["gap"])) in issues, issues
        checks_run += 1

        if checks_run != expected_case_count:
            raise AssertionError(
                f"self-test count drift: expected {expected_case_count}, got {checks_run}"
            )

    print("PHASE2_TESTS_README_ALIGNMENT=self-test-pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASES={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in regression checks instead of repo validation",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (defaults to current repo root).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
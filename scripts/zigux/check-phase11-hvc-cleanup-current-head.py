#!/usr/bin/env python3
"""Fail-close the current-head Phase 11 HVC cleanup packet.

This checker is intentionally narrow. It validates only the live HVC survey,
slice, teardown, validation-matrix, and sysrq-helper markers that the current
head companion note already identifies as the truthful bounded packet.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[3]

REQUIRED_FILES = {
    "survey": "Documentation/zigux/phase11-hvc-console-survey.md",
    "slice": "Documentation/zigux/phase11-hvc-console-slice.md",
    "teardown": "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig",
}

SURVEY_MARKERS = [
    "`drivers/tty/hvc/hvc_console_sysrq.zig`",
    "the direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions explicit.",
    "the bounded `hv_ops` callback-signature proof",
    "the exported-helper signature proof through `notifier_hangup_irq`",
    "remaining same-lane work is execution-facing follow-through rather than a missing simple-driver starter or missing survey-backed validation packet.",
]

SLICE_MARKERS = [
    "`PHASE11_HVC_CONSOLE_SLICE_STATUS=starter_packet_archived`",
    "Current `master` also materializes direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions.",
    "including the targetless notifier no-unregister edge",
    "`hvc_cleanup()` tty-port release handoff summary",
]

TEARDOWN_MARKERS = [
    "`PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`",
    "`drivers/tty/hvc/hvc_console_sysrq.zig`",
    "close-path and cleanup-path failure-mode cues explicit around tty detachment",
    "The direct verify, replay, and cleanup companions remain bounded host-free evidence rather than proof of live console integration.",
]

MATRIX_MARKERS = [
    "`PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`",
    "`drivers/tty/hvc/hvc_console_sysrq.zig`",
    "the exported-helper signature proof",
    "keeps the remove-handoff path explicit when the tty is already absent",
    "targetless sysrq dispatch from implying notifier callbacks",
    "sysrq toggle handoff, pending-dispatch separation, literal-byte fallback, and post-teardown unavailability stay explicit beside `drivers/tty/hvc/hvc_console_sysrq.zig`",
]

SYSRQ_HELPER_MARKERS = [
    "pub const SysrqHandoffRequest = struct {",
    "pub const SysrqHandoffSnapshot = struct {",
    "pub const keeps_live_sysrq_execution_out_of_scope = true;",
    "pub fn summarizeSysrqHandoff(request: SysrqHandoffRequest) SysrqHandoffSnapshot {",
    "const literal_fallback = !request.is_kernel_console or request.target_vtermno == null;",
    '.invokes_sysrq_handler = request.invokes_sysrq_handler and !literal_fallback,',
    '.falls_back_to_literal = literal_fallback,',
    'test "phase11 hvc sysrq handoff keeps live execution out of scope" {',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    missing: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            missing.append(f"missing:{label}:{rel_path}")
    if missing:
        return missing

    checks = [
        ("survey", read_text(root, REQUIRED_FILES["survey"]), SURVEY_MARKERS),
        ("slice", read_text(root, REQUIRED_FILES["slice"]), SLICE_MARKERS),
        ("teardown", read_text(root, REQUIRED_FILES["teardown"]), TEARDOWN_MARKERS),
        ("matrix", read_text(root, REQUIRED_FILES["matrix"]), MATRIX_MARKERS),
        ("sysrq_helper", read_text(root, REQUIRED_FILES["sysrq_helper"]), SYSRQ_HELPER_MARKERS),
    ]
    for label, text, markers in checks:
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")
    return missing


def fixture_texts() -> dict[str, str]:
    return {
        REQUIRED_FILES["survey"]: "\n".join(
            [
                "# Phase 11 HVC Console Survey",
                "* `drivers/tty/hvc/hvc_console_sysrq.zig`",
                "* the direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions explicit.",
                "* the bounded `hv_ops` callback-signature proof",
                "* the exported-helper signature proof through `notifier_hangup_irq`",
                "remaining same-lane work is execution-facing follow-through rather than a missing simple-driver starter or missing survey-backed validation packet.",
                "",
            ]
        ),
        REQUIRED_FILES["slice"]: "\n".join(
            [
                "# Phase 11 HVC Console Slice",
                "* `PHASE11_HVC_CONSOLE_SLICE_STATUS=starter_packet_archived`",
                "Current `master` also materializes direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions.",
                "including the targetless notifier no-unregister edge",
                "* `hvc_cleanup()` tty-port release handoff summary",
                "",
            ]
        ),
        REQUIRED_FILES["teardown"]: "\n".join(
            [
                "# Phase 11 HVC Console Teardown Note",
                "* `PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`",
                "* `drivers/tty/hvc/hvc_console_sysrq.zig`",
                "close-path and cleanup-path failure-mode cues explicit around tty detachment",
                "The direct verify, replay, and cleanup companions remain bounded host-free evidence rather than proof of live console integration.",
                "",
            ]
        ),
        REQUIRED_FILES["matrix"]: "\n".join(
            [
                "# Phase 11 HVC Console Validation Matrix",
                "* `PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`",
                "* `drivers/tty/hvc/hvc_console_sysrq.zig`",
                "the exported-helper signature proof",
                "keeps the remove-handoff path explicit when the tty is already absent",
                "targetless sysrq dispatch from implying notifier callbacks",
                "sysrq toggle handoff, pending-dispatch separation, literal-byte fallback, and post-teardown unavailability stay explicit beside `drivers/tty/hvc/hvc_console_sysrq.zig`",
                "",
            ]
        ),
        REQUIRED_FILES["sysrq_helper"]: "\n".join(
            [
                'const std = @import("std");',
                "",
                "pub const SysrqHandoffRequest = struct {",
                "    target_vtermno: ?u32,",
                "    byte: u8,",
                "    toggles_sysrq_mode: bool,",
                "    invokes_sysrq_handler: bool,",
                "    is_kernel_console: bool,",
                "    keeps_live_sysrq_execution_out_of_scope: bool = true,",
                "};",
                "",
                "pub const SysrqHandoffSnapshot = struct {",
                "    toggles_sysrq_mode: bool,",
                "    invokes_sysrq_handler: bool,",
                "    falls_back_to_literal: bool,",
                "    keeps_live_sysrq_execution_out_of_scope: bool,",
                "};",
                "",
                "pub const keeps_live_sysrq_execution_out_of_scope = true;",
                "",
                "pub fn summarizeSysrqHandoff(request: SysrqHandoffRequest) SysrqHandoffSnapshot {",
                "    const literal_fallback = !request.is_kernel_console or request.target_vtermno == null;",
                "    return .{",
                "        .invokes_sysrq_handler = request.invokes_sysrq_handler and !literal_fallback,",
                "        .falls_back_to_literal = literal_fallback,",
                "    };",
                "}",
                "",
                'test "phase11 hvc sysrq handoff keeps live execution out of scope" {',
                "    try std.testing.expect(true);",
                "}",
                "",
            ]
        ),
    }


def create_fixture(root: Path) -> None:
    for rel_path, text in fixture_texts().items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def expect_missing(label: str, root: Path, marker: str) -> None:
    problems = validate(root)
    expected = f"{label}:{marker}"
    if expected not in problems:
        raise AssertionError(f"expected missing marker {expected!r}, got {problems!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase11-hvc-cleanup-current-head-") as tmpdir:
        root = Path(tmpdir)
        create_fixture(root)
        problems = validate(root)
        if problems:
            raise AssertionError(f"expected clean fixture, got {problems!r}")
        case_count += 1

        for label, rel_path, marker in [
            ("survey", REQUIRED_FILES["survey"], SURVEY_MARKERS[0]),
            ("slice", REQUIRED_FILES["slice"], SLICE_MARKERS[0]),
            ("teardown", REQUIRED_FILES["teardown"], TEARDOWN_MARKERS[0]),
            ("matrix", REQUIRED_FILES["matrix"], MATRIX_MARKERS[0]),
            ("sysrq_helper", REQUIRED_FILES["sysrq_helper"], SYSRQ_HELPER_MARKERS[0]),
        ]:
            create_fixture(root)
            path = root / rel_path
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            expect_missing(label, root, marker)
            case_count += 1

        shutil.rmtree(root / "drivers")
        problems = validate(root)
        expected = f"missing:sysrq_helper:{REQUIRED_FILES['sysrq_helper']}"
        if expected not in problems:
            raise AssertionError(f"expected {expected!r}, got {problems!r}")
        case_count += 1

    print("PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST=pass")
    print(f"PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    problems = validate(args.root.resolve())
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    print("phase11 hvc cleanup current-head checker: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

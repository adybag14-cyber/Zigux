#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


HEX40 = re.compile(r"^[0-9a-f]{40}$")
DEFAULT_ROOT = Path(__file__).resolve().parent
FIXTURE_COMMIT = "a5fdfc2f82f52a4babccc9dca60e8b1ba6228b59"

REQUIRED_FILES = {
    "manifest": "zigux/tests/phase11_hvc_console_manifest.json",
    "survey": "Documentation/zigux/phase11-hvc-console-survey.md",
    "slice": "Documentation/zigux/phase11-hvc-console-slice.md",
    "matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "modem_control_split": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "poll_retry_split": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig",
    "hvc_test": "zigux/tests/phase11_hvc_console.zig",
}

SURVEY_MARKERS = [
    "reviewed against live `master` `{commit}`",
    "`zigux/tests/phase11_hvc_console_modem_control_split.zig` now keeps the already-landed `tiocmget()` and `tiocmset()` callback-presence split, fallback-versus-direct routing, and set-versus-clear mask passthrough explicit inside the shared Phase 11 gate so modem-control failure modes do not stay implicit in the older single-file HVC replay",
    "`zigux/tests/phase11_hvc_console_poll_retry_split.zig` now keeps the already-landed `__hvc_poll()` IRQ-backed may-sleep drained-read split, the may-sleep IRQ-free retry-rearm split, the partial-write-versus-stalled-write split, and the bounded sysrq toggle-versus-dispatch split plus the later non-kernel `^O` literal fallback and teardown-time `error.ConsoleUnavailable` rejection explicit inside the shared Phase 11 gate so those read-versus-write retry details and primary-console sysrq teardown edges do not stay implicit in the older single-file HVC replay",
    "The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small host-free sysrq or khvcd handoff that is not already covered by the notifier-add open handoff, the bounded sysrq helper, the `struct winsize` layout proof, the `struct hv_ops` layout proof, the `hv_ops` callback-signature proof, and the exported hvc helper signature proof; otherwise avoid widening straight into live tty teardown, notifier execution, sysrq handling, live khvcd worker behavior, `struct hvc_struct`, or host-backed teardown.",
]

SLICE_MARKERS = [
    "`hvc_cleanup()` tty-port release handoff summary",
    "The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless another comparably small host-free notifier callback or khvcd handoff becomes obvious; otherwise avoid widening straight into live tty teardown, live khvcd worker behavior, or host-backed teardown.",
]

MATRIX_MARKERS = [
    "PHASE11_HVC_CONSOLE_STATUS=cleanup_handoff_landed",
    "the dedicated archival survey gate remains `zigux/tests/phase11_hvc_console_survey.zig`",
    "host-free khvcd, notifier, remove, or cleanup handoff",
]

MODEM_CONTROL_SPLIT_MARKERS = [
    'test "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks" {',
    "    try std.testing.expect(summary.tiocmget_returns_einval_fallback);",
    "    try std.testing.expect(summary.tiocmset_returns_einval_fallback);",
    'test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back" {',
    "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    "    try std.testing.expect(summary.set_mask_passthrough);",
    "    try std.testing.expect(summary.clear_mask_passthrough);",
    'test "phase11 hvc console keeps modem-control teardown fallout unavailable after slot removal" {',
    "    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeModemControl(.{",
]

POLL_RETRY_SPLIT_MARKERS = [
    'test "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep" {',
    "    try std.testing.expect(drained_without_sleep.read_poll_pending_after_drain);",
    "    try std.testing.expect(!drained_with_sleep.read_poll_pending_after_drain);",
    'test "phase11 hvc console keeps may-sleep drained reads retry-armed when irq delivery is unavailable" {',
    "    try std.testing.expect(irq_free_drained.read_poll_armed_without_irq);",
    "    try std.testing.expect(!irq_backed_drained.read_poll_pending_after_drain);",
    'test "phase11 hvc console keeps partial write progress distinct from stalled __hvc_poll retries" {',
    "    try std.testing.expect(partial_write.write_progress_resets_timeout);",
    "    try std.testing.expect(stalled_write.stalled_write_uses_min_timeout);",
    'test "phase11 hvc console keeps sysrq toggle handoff distinct from literal fallback on the primary console" {',
    "    try std.testing.expect(enter_sysrq.toggles_sysrq_mode);",
    'test "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes" {',
    "    try std.testing.expect(dispatch.invokes_sysrq_handler);",
    'test "phase11 hvc console keeps non-kernel ^O as a literal byte without toggling sysrq state" {',
    "    try std.testing.expect(non_kernel_toggle.emits_literal_char);",
    "    try std.testing.expect(!non_kernel_toggle.consumes_input_without_flip);",
    'test "phase11 hvc console keeps sysrq handoff unavailable after teardown" {',
    "    try std.testing.expectError(error.ConsoleUnavailable, hvc_console_sysrq.summarizeSysrqHandoff(&console, .{",
]

SYSRQ_HELPER_MARKERS = [
    "pub const SysrqHandoffRequest = struct {",
    "pub const SysrqHandoffSnapshot = struct {",
    "pub fn summarizeSysrqHandoff(",
    "    const is_toggle = request.is_kernel_console and request.input_char == 0x0f;",
    "    const invokes_sysrq_handler = request.is_kernel_console and request.sysrq_pressed_before and !is_toggle;",
    "    const emits_literal_char = if (!request.is_kernel_console)",
    "        .emits_literal_char = emits_literal_char,",
    "        .consumes_input_without_flip = !emits_literal_char,",
    "        .invokes_sysrq_handler = invokes_sysrq_handler,",
    "        .keeps_live_sysrq_execution_out_of_scope = true,",
]

HVC_TEST_MARKERS = [
    'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {',
    "    try std.testing.expect(final_cleanup.tty_port_put_requested);",
    "    try std.testing.expect(final_cleanup.drops_tty_port_reference);",
    "    try std.testing.expect(final_cleanup.defers_final_release_to_port_destruct);",
    "    try std.testing.expect(hangup_cleanup.close_skipped);",
    "    try std.testing.expect(hangup_cleanup.tty_port_put_requested);",
    "    try std.testing.expect(hangup_cleanup.drops_tty_port_reference);",
    "    try std.testing.expect(hangup_cleanup.defers_final_release_to_port_destruct);",
]


def resolve_root() -> Path:
    if "--root" in sys.argv[1:]:
        idx = sys.argv.index("--root")
        try:
            return Path(sys.argv[idx + 1]).resolve()
        except IndexError as exc:
            raise SystemExit("--root requires a path") from exc
    if "ZIGUX_PHASE11_ROOT" in os.environ:
        return Path(os.environ["ZIGUX_PHASE11_ROOT"]).resolve()
    return DEFAULT_ROOT


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], prefix: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{prefix}:{marker}")


def validate(root: Path) -> list[str]:
    missing: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            missing.append(f"missing:{label}:{rel_path}")
    if missing:
        return missing

    manifest = json.loads(read_text(root, REQUIRED_FILES["manifest"]))
    if manifest.get("lane_key") != "P11-L18":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 11":
        missing.append("manifest:phase")
    commit = str(manifest.get("surveyed_commit", ""))
    if not HEX40.fullmatch(commit):
        missing.append("manifest:surveyed_commit")

    survey = read_text(root, REQUIRED_FILES["survey"])
    expected_survey = [marker.format(commit=commit) for marker in SURVEY_MARKERS]
    check_markers(missing, "survey", survey, expected_survey)

    slice_note = read_text(root, REQUIRED_FILES["slice"])
    check_markers(missing, "slice", slice_note, SLICE_MARKERS)

    matrix = read_text(root, REQUIRED_FILES["matrix"])
    if commit and commit not in matrix:
        missing.append("matrix:surveyed_commit")
    check_markers(missing, "matrix", matrix, MATRIX_MARKERS)

    check_markers(missing, "modem_control_split", read_text(root, REQUIRED_FILES["modem_control_split"]), MODEM_CONTROL_SPLIT_MARKERS)
    check_markers(missing, "poll_retry_split", read_text(root, REQUIRED_FILES["poll_retry_split"]), POLL_RETRY_SPLIT_MARKERS)
    check_markers(missing, "sysrq_helper", read_text(root, REQUIRED_FILES["sysrq_helper"]), SYSRQ_HELPER_MARKERS)
    check_markers(missing, "hvc_test", read_text(root, REQUIRED_FILES["hvc_test"]), HVC_TEST_MARKERS)
    return missing


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-hvc-cleanup-alignment.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clone_fixture_root(root: Path) -> None:
    write_text(root / "scripts/zigux/check-phase11-hvc-cleanup-alignment.py", Path(__file__).read_text(encoding="utf-8"))
    write_text(
        root / REQUIRED_FILES["manifest"],
        json.dumps({"lane_key": "P11-L18", "phase": "Phase 11", "surveyed_commit": FIXTURE_COMMIT}, indent=2) + "\n",
    )
    write_text(
        root / REQUIRED_FILES["survey"],
        "\n".join([
            f"reviewed against live `master` `{FIXTURE_COMMIT}`",
            SURVEY_MARKERS[1],
            SURVEY_MARKERS[2],
            SURVEY_MARKERS[3],
            "",
        ]),
    )
    write_text(root / REQUIRED_FILES["slice"], "\n".join(SLICE_MARKERS) + "\n")
    write_text(root / REQUIRED_FILES["matrix"], "\n".join([f"reviewed against live `master` `{FIXTURE_COMMIT}`", *MATRIX_MARKERS]) + "\n")
    write_text(root / REQUIRED_FILES["modem_control_split"], "\n".join(MODEM_CONTROL_SPLIT_MARKERS) + "\n")
    write_text(root / REQUIRED_FILES["poll_retry_split"], "\n".join(POLL_RETRY_SPLIT_MARKERS) + "\n")
    write_text(root / REQUIRED_FILES["sysrq_helper"], "\n".join(SYSRQ_HELPER_MARKERS) + "\n")
    write_text(root / REQUIRED_FILES["hvc_test"], "\n".join(HVC_TEST_MARKERS) + "\n")


def expect_missing(label: str, root: Path, needle: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-hvc-cleanup-self-test:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(f"phase11-hvc-cleanup-self-test:{label}:expected:{needle}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_hvc_cleanup_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_validator(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-hvc-cleanup-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        manifest_path = tmp_root / REQUIRED_FILES["manifest"]
        original = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(original.replace('"lane_key": "P11-L18"', '"lane_key": "P11-L99"', 1), encoding="utf-8")
        expect_missing("manifest_lane_key", tmp_root, "manifest:lane_key")
        manifest_path.write_text(original, encoding="utf-8")

        survey_path = tmp_root / REQUIRED_FILES["survey"]
        original = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(original.replace(SURVEY_MARKERS[2], "poll retry summary", 1), encoding="utf-8")
        expect_missing("survey_poll_retry_marker", tmp_root, f"survey:{SURVEY_MARKERS[2]}")
        survey_path.write_text(original, encoding="utf-8")

        poll_path = tmp_root / REQUIRED_FILES["poll_retry_split"]
        original = poll_path.read_text(encoding="utf-8")
        poll_path.write_text(original.replace("    try std.testing.expect(non_kernel_toggle.emits_literal_char);\n", "", 1), encoding="utf-8")
        expect_missing("poll_retry_non_kernel_literal", tmp_root, "poll_retry_split:    try std.testing.expect(non_kernel_toggle.emits_literal_char);")
        poll_path.write_text(original, encoding="utf-8")

        poll_path.write_text(original.replace("    try std.testing.expectError(error.ConsoleUnavailable, hvc_console_sysrq.summarizeSysrqHandoff(&console, .{\n", "", 1), encoding="utf-8")
        expect_missing("poll_retry_teardown_unavailable", tmp_root, "poll_retry_split:    try std.testing.expectError(error.ConsoleUnavailable, hvc_console_sysrq.summarizeSysrqHandoff(&console, .{")
        poll_path.write_text(original, encoding="utf-8")

        sysrq_path = tmp_root / REQUIRED_FILES["sysrq_helper"]
        original = sysrq_path.read_text(encoding="utf-8")
        sysrq_path.write_text(original.replace("        .emits_literal_char = emits_literal_char,\n", "", 1), encoding="utf-8")
        expect_missing("sysrq_helper_literal_marker", tmp_root, "sysrq_helper:        .emits_literal_char = emits_literal_char,")
        sysrq_path.write_text(original, encoding="utf-8")

        hvc_test_path = tmp_root / REQUIRED_FILES["hvc_test"]
        original = hvc_test_path.read_text(encoding="utf-8")
        hvc_test_path.write_text(original.replace("    try std.testing.expect(final_cleanup.tty_port_put_requested);\n", "", 1), encoding="utf-8")
        expect_missing("hvc_test_cleanup_marker", tmp_root, "hvc_test:    try std.testing.expect(final_cleanup.tty_port_put_requested);")
        hvc_test_path.write_text(original, encoding="utf-8")

        (tmp_root / REQUIRED_FILES["poll_retry_split"]).unlink()
        expect_missing("poll_retry_file_presence", tmp_root, f"missing:poll_retry_split:{REQUIRED_FILES['poll_retry_split']}")

    print("PHASE11_HVC_CLEANUP_ALIGNMENT_SELF_TEST=pass")
    print("PHASE11_HVC_CLEANUP_ALIGNMENT_SELF_TEST_CASE_COUNT=7")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print("PHASE11_HVC_CLEANUP_ALIGNMENT=fail")
    print("PHASE11_HVC_CLEANUP_ALIGNMENT_MISSING_START")
    for problem in problems:
        print(problem)
    print("PHASE11_HVC_CLEANUP_ALIGNMENT_MISSING_END")
    raise SystemExit(1)

print("PHASE11_HVC_CLEANUP_ALIGNMENT=pass")
print(f"PHASE11_HVC_CLEANUP_ALIGNMENT_ROOT={ROOT}")
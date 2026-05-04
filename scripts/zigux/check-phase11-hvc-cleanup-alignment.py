#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import os
import re
import subprocess
import sys
import tempfile


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
    args = sys.argv[1:]
    if "--root" in args:
        index = args.index("--root")
        try:
            return Path(args[index + 1]).resolve()
        except IndexError as exc:
            raise SystemExit("--root requires a path") from exc
    env_root = Path(os.environ["ZIGUX_PHASE11_ROOT"]).resolve() if "ZIGUX_PHASE11_ROOT" in os.environ else None
    if env_root is not None:
        return env_root
    return DEFAULT_ROOT


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads(read_text(root, REQUIRED_FILES["manifest"]))


def validate(root: Path) -> list[str]:
    missing: list[str] = []

    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            missing.append(f"missing:{label}:{rel_path}")
    if missing:
        return missing

    manifest = load_manifest(root)
    lane_key = manifest.get("lane_key")
    phase = manifest.get("phase")
    commit = str(manifest.get("surveyed_commit", ""))

    if lane_key != "P11-L18":
        missing.append("manifest:lane_key")
    if phase != "Phase 11":
        missing.append("manifest:phase")
    if not HEX40.fullmatch(commit):
        missing.append("manifest:surveyed_commit")

    survey = read_text(root, REQUIRED_FILES["survey"])
    slice_note = read_text(root, REQUIRED_FILES["slice"])
    matrix = read_text(root, REQUIRED_FILES["matrix"])
    modem_control_split = read_text(root, REQUIRED_FILES["modem_control_split"])
    poll_retry_split = read_text(root, REQUIRED_FILES["poll_retry_split"])
    sysrq_helper = read_text(root, REQUIRED_FILES["sysrq_helper"])
    hvc_test = read_text(root, REQUIRED_FILES["hvc_test"])

    for marker in SURVEY_MARKERS:
        expected = marker.format(commit=commit)
        if expected not in survey:
            missing.append(f"survey:{expected}")

    for marker in SLICE_MARKERS:
        if marker not in slice_note:
            missing.append(f"slice:{marker}")

    if commit and commit not in matrix:
        missing.append("matrix:surveyed_commit")
    for marker in MATRIX_MARKERS:
        if marker not in matrix:
            missing.append(f"matrix:{marker}")

    for marker in MODEM_CONTROL_SPLIT_MARKERS:
        if marker not in modem_control_split:
            missing.append(f"modem_control_split:{marker}")

    for marker in POLL_RETRY_SPLIT_MARKERS:
        if marker not in poll_retry_split:
            missing.append(f"poll_retry_split:{marker}")

    for marker in SYSRQ_HELPER_MARKERS:
        if marker not in sysrq_helper:
            missing.append(f"sysrq_helper:{marker}")

    for marker in HVC_TEST_MARKERS:
        if marker not in hvc_test:
            missing.append(f"hvc_test:{marker}")

    return missing


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-hvc-cleanup-alignment.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def clone_fixture_root(destination_root: Path) -> None:
    script_target = destination_root / "scripts/zigux/check-phase11-hvc-cleanup-alignment.py"
    script_target.parent.mkdir(parents=True, exist_ok=True)
    script_target.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

    (destination_root / REQUIRED_FILES["manifest"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["manifest"]).write_text(
        json.dumps(
            {
                "lane_key": "P11-L18",
                "phase": "Phase 11",
                "surveyed_commit": FIXTURE_COMMIT,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (destination_root / REQUIRED_FILES["survey"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["survey"]).write_text(
        "\n".join(
            [
                "# Phase 11 HVC Console Survey",
                f"- reviewed against live `master` `{FIXTURE_COMMIT}`",
                "- `hvc_cleanup()` remains bounded",
                "- `zigux/tests/phase11_hvc_console_modem_control_split.zig` now keeps the already-landed `tiocmget()` and `tiocmset()` callback-presence split, fallback-versus-direct routing, and set-versus-clear mask passthrough explicit inside the shared Phase 11 gate so modem-control failure modes do not stay implicit in the older single-file HVC replay",
                "- `zigux/tests/phase11_hvc_console_poll_retry_split.zig` now keeps the already-landed `__hvc_poll()` IRQ-backed may-sleep drained-read split, the may-sleep IRQ-free retry-rearm split, the partial-write-versus-stalled-write split, and the bounded sysrq toggle-versus-dispatch split plus the later non-kernel `^O` literal fallback and teardown-time `error.ConsoleUnavailable` rejection explicit inside the shared Phase 11 gate so those read-versus-write retry details and primary-console sysrq teardown edges do not stay implicit in the older single-file HVC replay",
                "- The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small host-free sysrq or khvcd handoff that is not already covered by the notifier-add open handoff, the bounded sysrq helper, the `struct winsize` layout proof, the `struct hv_ops` layout proof, the `hv_ops` callback-signature proof, and the exported hvc helper signature proof; otherwise avoid widening straight into live tty teardown, notifier execution, sysrq handling, live khvcd worker behavior, `struct hvc_struct`, or host-backed teardown.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (destination_root / REQUIRED_FILES["slice"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["slice"]).write_text(
        "\n".join(
            [
                "# Phase 11 HVC Console Slice",
                "- `hvc_cleanup()` tty-port release handoff summary",
                "- The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless another comparably small host-free notifier callback or khvcd handoff becomes obvious; otherwise avoid widening straight into live tty teardown, live khvcd worker behavior, or host-backed teardown.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (destination_root / REQUIRED_FILES["matrix"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["matrix"]).write_text(
        "\n".join(
            [
                "# Phase 11 HVC Console Validation Matrix",
                "",
                "- `PHASE11_HVC_CONSOLE_STATUS=cleanup_handoff_landed`",
                f"- reviewed against live `master` `{FIXTURE_COMMIT}`",
                "- the dedicated archival survey gate remains `zigux/tests/phase11_hvc_console_survey.zig`",
                "- host-free khvcd, notifier, remove, or cleanup handoff",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (destination_root / REQUIRED_FILES["modem_control_split"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["modem_control_split"]).write_text(
        "\n".join(
            [
                'test "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks" {',
                "    try std.testing.expect(summary.tiocmget_returns_einval_fallback);",
                "    try std.testing.expect(summary.tiocmset_returns_einval_fallback);",
                "}",
                "",
                'test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back" {',
                "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
                "    try std.testing.expect(summary.set_mask_passthrough);",
                "    try std.testing.expect(summary.clear_mask_passthrough);",
                "}",
                "",
                'test "phase11 hvc console keeps modem-control teardown fallout unavailable after slot removal" {',
                "    try std.testing.expectError(error.ConsoleUnavailable, console.summarizeModemControl(.{",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (destination_root / REQUIRED_FILES["poll_retry_split"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["poll_retry_split"]).writeText?
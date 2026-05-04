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
                "const std = @import(\"std\");",
                "const hvc_console = @import(\"hvc_console\");",
                "",
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
    (destination_root / REQUIRED_FILES["poll_retry_split"]).write_text(
        "\n".join(
            [
                "const std = @import(\"std\");",
                "const hvc_console = @import(\"hvc_console\");",
                "",
                'test "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep" {',
                "    try std.testing.expect(drained_without_sleep.read_poll_pending_after_drain);",
                "    try std.testing.expect(!drained_with_sleep.read_poll_pending_after_drain);",
                "}",
                "",
                'test "phase11 hvc console keeps may-sleep drained reads retry-armed when irq delivery is unavailable" {',
                "    try std.testing.expect(irq_free_drained.read_poll_armed_without_irq);",
                "    try std.testing.expect(!irq_backed_drained.read_poll_pending_after_drain);",
                "}",
                "",
                'test "phase11 hvc console keeps partial write progress distinct from stalled __hvc_poll retries" {',
                "    try std.testing.expect(partial_write.write_progress_resets_timeout);",
                "    try std.testing.expect(stalled_write.stalled_write_uses_min_timeout);",
                "}",
                "",
                'test "phase11 hvc console keeps sysrq toggle handoff distinct from literal fallback on the primary console" {',
                "    try std.testing.expect(enter_sysrq.toggles_sysrq_mode);",
                "}",
                "",
                'test "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes" {',
                "    try std.testing.expect(dispatch.invokes_sysrq_handler);",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (destination_root / REQUIRED_FILES["sysrq_helper"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["sysrq_helper"]).write_text(
        "\n".join(
            [
                "const hvc_console = @import(\"./hvc_console.zig\");",
                "",
                "pub const SysrqHandoffRequest = struct {",
                "    is_kernel_console: bool = false,",
                "    sysrq_pressed_before: bool = false,",
                "    input_char: u8 = 0,",
                "};",
                "",
                "pub const SysrqHandoffSnapshot = struct {",
                "    anchor: []const u8,",
                "    slot_index: usize,",
                "    vtermno: u32,",
                "    adapter_present: bool,",
                "    is_kernel_console: bool,",
                "    sysrq_pressed_before: bool,",
                "    input_char: u8,",
                "    toggles_sysrq_mode: bool,",
                "    sysrq_pressed_after: bool,",
                "    invokes_sysrq_handler: bool,",
                "    clears_sysrq_after_handler: bool,",
                "    emits_literal_char: bool,",
                "    consumes_input_without_flip: bool,",
                "    keeps_tty_registration_out_of_scope: bool,",
                "    keeps_live_hypervisor_io_out_of_scope: bool,",
                "    keeps_live_sysrq_execution_out_of_scope: bool,",
                "};",
                "",
                "pub fn summarizeSysrqHandoff(",
                "    console: *const hvc_console.HvcConsoleLab,",
                "    request: SysrqHandoffRequest,",
                ") !SysrqHandoffSnapshot {",
                "    const slot = console.slotSnapshot();",
                "    if (!slot.usable_for_console) return error.ConsoleUnavailable;",
                "",
                "    const is_toggle = request.is_kernel_console and request.input_char == 0x0f;",
                "    const invokes_sysrq_handler = request.is_kernel_console and request.sysrq_pressed_before and !is_toggle;",
                "    const clears_sysrq_after_handler = invokes_sysrq_handler;",
                "    const sysrq_pressed_after = if (is_toggle)",
                "        !request.sysrq_pressed_before",
                "    else if (invokes_sysrq_handler)",
                "        false",
                "    else",
                "        request.sysrq_pressed_before;",
                "    const emits_literal_char = if (!request.is_kernel_console)",
                "        true",
                "    else if (is_toggle)",
                "        request.sysrq_pressed_before",
                "    else",
                "        !request.sysrq_pressed_before;",
                "",
                "    return .{",
                "        .anchor = hvc_console.HvcConsoleLab.descriptor().anchor,",
                "        .slot_index = slot.slot_index,",
                "        .vtermno = slot.vtermno,",
                "        .adapter_present = slot.adapter_present,",
                "        .is_kernel_console = request.is_kernel_console,",
                "        .sysrq_pressed_before = request.sysrq_pressed_before,",
                "        .input_char = request.input_char,",
                "        .toggles_sysrq_mode = is_toggle,",
                "        .sysrq_pressed_after = sysrq_pressed_after,",
                "        .invokes_sysrq_handler = invokes_sysrq_handler,",
                "        .clears_sysrq_after_handler = clears_sysrq_after_handler,",
                "        .emits_literal_char = emits_literal_char,",
                "        .consumes_input_without_flip = !emits_literal_char,",
                "        .keeps_tty_registration_out_of_scope = true,",
                "        .keeps_live_hypervisor_io_out_of_scope = true,",
                "        .keeps_live_sysrq_execution_out_of_scope = true,",
                "    };",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (destination_root / REQUIRED_FILES["hvc_test"]).parent.mkdir(parents=True, exist_ok=True)
    (destination_root / REQUIRED_FILES["hvc_test"]).write_text(
        "\n".join(
            [
                "const std = @import(\"std\");",
                "const hvc_console = @import(\"hvc_console\");",
                "",
                'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {',
                "    try std.testing.expect(final_cleanup.tty_port_put_requested);",
                "    try std.testing.expect(final_cleanup.drops_tty_port_reference);",
                "    try std.testing.expect(final_cleanup.defers_final_release_to_port_destruct);",
                "    try std.testing.expect(hangup_cleanup.close_skipped);",
                "    try std.testing.expect(hangup_cleanup.tty_port_put_requested);",
                "    try std.testing.expect(hangup_cleanup.drops_tty_port_reference);",
                "    try std.testing.expect(hangup_cleanup.defers_final_release_to_port_destruct);",
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_missing(label: str, root: Path, needle: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-hvc-cleanup-self-test:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase11-hvc-cleanup-self-test:{label}:expected:{needle}:actual:{actual}"
        )


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
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace(
                '"lane_key": "P11-L18"',
                '"lane_key": "P11-L99"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing("manifest_lane_key", tmp_root, "manifest:lane_key")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                f'"surveyed_commit": "{FIXTURE_COMMIT}"',
                '"surveyed_commit": "1234567890abcdef1234567890abcdef12345678"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing("matrix_commit_sync", tmp_root, "matrix:surveyed_commit")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        matrix_path = tmp_root / REQUIRED_FILES["matrix"]
        original_matrix = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            original_matrix.replace(
                "PHASE11_HVC_CONSOLE_STATUS=cleanup_handoff_landed",
                "PHASE11_HVC_CONSOLE_STATUS=remove_handoff_landed",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "cleanup_status",
            tmp_root,
            "matrix:PHASE11_HVC_CONSOLE_STATUS=cleanup_handoff_landed",
        )
        matrix_path.write_text(original_matrix, encoding="utf-8")

        survey_path = tmp_root / REQUIRED_FILES["survey"]
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "`zigux/tests/phase11_hvc_console_modem_control_split.zig` now keeps the already-landed `tiocmget()` and `tiocmset()` callback-presence split, fallback-versus-direct routing, and set-versus-clear mask passthrough explicit inside the shared Phase 11 gate so modem-control failure modes do not stay implicit in the older single-file HVC replay",
                "`zigux/tests/phase11_hvc_console_modem_control_split.zig` now keeps modem-control callback coverage explicit inside the shared Phase 11 gate",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "survey_modem_control_split_marker",
            tmp_root,
            "survey:`zigux/tests/phase11_hvc_console_modem_control_split.zig` now keeps the already-landed `tiocmget()` and `tiocmset()` callback-presence split, fallback-versus-direct routing, and set-versus-clear mask passthrough explicit inside the shared Phase 11 gate so modem-control failure modes do not stay implicit in the older single-file HVC replay",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "partial-write-versus-stalled-write split, and the bounded sysrq toggle-versus-dispatch split plus the later non-kernel `^O` literal fallback and teardown-time `error.ConsoleUnavailable` rejection explicit inside the shared Phase 11 gate",
                "partial-write-versus-stalled-write split explicit inside the shared Phase 11 gate",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "survey_poll_retry_split_marker",
            tmp_root,
            "survey:`zigux/tests/phase11_hvc_console_poll_retry_split.zig` now keeps the already-landed `__hvc_poll()` IRQ-backed may-sleep drained-read split, the may-sleep IRQ-free retry-rearm split, the partial-write-versus-stalled-write split, and the bounded sysrq toggle-versus-dispatch split plus the later non-kernel `^O` literal fallback and teardown-time `error.ConsoleUnavailable` rejection explicit inside the shared Phase 11 gate so those read-versus-write retry details and primary-console sysrq teardown edges do not stay implicit in the older single-file HVC replay",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "host-free sysrq or khvcd handoff that is not already covered by the notifier-add open handoff, the bounded sysrq helper, the `struct winsize` layout proof, the `struct hv_ops` layout proof, the `hv_ops` callback-signature proof, and the exported hvc helper signature proof; otherwise avoid widening straight into live tty teardown, notifier execution, sysrq handling, live khvcd worker behavior, `struct hvc_struct`, or host-backed teardown.",
                "host-free khvcd handoff that is not already covered by the notifier-add open handoff, the `struct winsize` layout proof, the `struct hv_ops` layout proof, and the `hv_ops` callback-signature proof; otherwise avoid widening straight into live tty teardown, notifier execution, live khvcd worker behavior, `struct hvc_struct`, or host-backed teardown.",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "survey_next_step",
            tmp_root,
            "survey:The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small host-free sysrq or khvcd handoff that is not already covered by the notifier-add open handoff, the bounded sysrq helper, the `struct winsize` layout proof, the `struct hv_ops` layout proof, the `hv_ops` callback-signature proof, and the exported hvc helper signature proof; otherwise avoid widening straight into live tty teardown, notifier execution, sysrq handling, live khvcd worker behavior, `struct hvc_struct`, or host-backed teardown.",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        slice_path = tmp_root / REQUIRED_FILES["slice"]
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace(
                "host-free notifier callback or khvcd handoff becomes obvious; otherwise avoid widening straight into live tty teardown, live khvcd worker behavior, or host-backed teardown.",
                "host-free khvcd handoff becomes obvious; otherwise avoid widening straight into live khvcd worker behavior or host-backed teardown.",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing("slice_next_step", tmp_root, "slice:The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless another comparably small host-free notifier callback or khvcd handoff becomes obvious; otherwise avoid widening straight into live tty teardown, live khvcd worker behavior, or host-backed teardown.")
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "`hvc_cleanup()` tty-port release handoff summary",
                "`hvc_remove()` handoff summary",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "slice_cleanup_marker",
            tmp_root,
            "slice:`hvc_cleanup()` tty-port release handoff summary",
        )
        slice_path.write_text(original_slice, encoding="utf-8")

        modem_control_split_path = tmp_root / REQUIRED_FILES["modem_control_split"]
        original_modem_control_split = modem_control_split_path.read_text(encoding="utf-8")
        modem_control_split_path.write_text(
            original_modem_control_split.replace(
                "    try std.testing.expect(summary.tiocmset_returns_einval_fallback);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "modem_control_split_fallback_marker",
            tmp_root,
            "modem_control_split:    try std.testing.expect(summary.tiocmset_returns_einval_fallback);",
        )
        modem_control_split_path.write_text(original_modem_control_split, encoding="utf-8")

        modem_control_split_path.write_text(
            original_modem_control_split.replace(
                "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "modem_control_split_tiocmset_result_marker",
            tmp_root,
            "modem_control_split:    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
        )
        modem_control_split_path.write_text(original_modem_control_split, encoding="utf-8")

        poll_retry_split_path = tmp_root / REQUIRED_FILES["poll_retry_split"]
        original_poll_retry_split = poll_retry_split_path.read_text(encoding="utf-8")
        poll_retry_split_path.write_text(
            original_poll_retry_split.replace(
                "    try std.testing.expect(stalled_write.stalled_write_uses_min_timeout);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "poll_retry_split_stalled_write_marker",
            tmp_root,
            "poll_retry_split:    try std.testing.expect(stalled_write.stalled_write_uses_min_timeout);",
        )
        poll_retry_split_path.write_text(original_poll_retry_split, encoding="utf-8")

        poll_retry_split_path.write_text(
            original_poll_retry_split.replace(
                "    try std.testing.expect(dispatch.invokes_sysrq_handler);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "poll_retry_split_sysrq_dispatch_marker",
            tmp_root,
            "poll_retry_split:    try std.testing.expect(dispatch.invokes_sysrq_handler);",
        )
        poll_retry_split_path.write_text(original_poll_retry_split, encoding="utf-8")

        sysrq_helper_path = tmp_root / REQUIRED_FILES["sysrq_helper"]
        original_sysrq_helper = sysrq_helper_path.read_text(encoding="utf-8")
        sysrq_helper_path.write_text(
            original_sysrq_helper.replace(
                "        .keeps_live_sysrq_execution_out_of_scope = true,\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "sysrq_helper_scope_marker",
            tmp_root,
            "sysrq_helper:        .keeps_live_sysrq_execution_out_of_scope = true,",
        )
        sysrq_helper_path.write_text(original_sysrq_helper, encoding="utf-8")

        sysrq_helper_path.write_text(
            original_sysrq_helper.replace(
                "        .emits_literal_char = emits_literal_char,\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "sysrq_helper_emits_literal_char_marker",
            tmp_root,
            "sysrq_helper:        .emits_literal_char = emits_literal_char,",
        )
        sysrq_helper_path.write_text(original_sysrq_helper, encoding="utf-8")

        hvc_test_path = tmp_root / REQUIRED_FILES["hvc_test"]
        original_hvc_test = hvc_test_path.read_text(encoding="utf-8")
        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(final_cleanup.tty_port_put_requested);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "hvc_test_final_cleanup_marker",
            tmp_root,
            "hvc_test:    try std.testing.expect(final_cleanup.tty_port_put_requested);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(hangup_cleanup.close_skipped);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "hvc_test_hangup_cleanup_close_skipped_marker",
            tmp_root,
            "hvc_test:    try std.testing.expect(hangup_cleanup.close_skipped);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(hangup_cleanup.defers_final_release_to_port_destruct);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "hvc_test_hangup_cleanup_release_marker",
            tmp_root,
            "hvc_test:    try std.testing.expect(hangup_cleanup.defers_final_release_to_port_destruct);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.unlink()
        expect_missing(
            "hvc_test_file_presence",
            tmp_root,
            f"missing:hvc_test:{REQUIRED_FILES['hvc_test']}",
        )
        clone_fixture_root(tmp_root)

        modem_control_split_path = tmp_root / REQUIRED_FILES["modem_control_split"]
        modem_control_split_path.unlink()
        expect_missing(
            "modem_control_split_file_presence",
            tmp_root,
            f"missing:modem_control_split:{REQUIRED_FILES['modem_control_split']}",
        )
        clone_fixture_root(tmp_root)

        poll_retry_split_path = tmp_root / REQUIRED_FILES["poll_retry_split"]
        poll_retry_split_path.unlink()
        expect_missing(
            "poll_retry_split_file_presence",
            tmp_root,
            f"missing:poll_retry_split:{REQUIRED_FILES['poll_retry_split']}",
        )
        clone_fixture_root(tmp_root)

        sysrq_helper_path = tmp_root / REQUIRED_FILES["sysrq_helper"]
        sysrq_helper_path.unlink()
        expect_missing(
            "sysrq_helper_file_presence",
            tmp_root,
            f"missing:sysrq_helper:{REQUIRED_FILES['sysrq_helper']}",
        )

    print("PHASE11_HVC_CLEANUP_ALIGNMENT_SELF_TEST=pass")
    print("PHASE11_HVC_CLEANUP_ALIGNMENT_SELF_TEST_CASE_COUNT=20")
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
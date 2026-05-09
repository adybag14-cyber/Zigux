#!/usr/bin/env python3
"""Check the bounded Phase 11 shared header-boundary packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


EXPECTED_LANE_KEY = "P11-L18"
EXPECTED_PHASE = "Phase 11"
EXPECTED_ANCHOR = (
    "include/uapi/linux/watchdog.h + include/uapi/asm-generic/termios.h + "
    "drivers/tty/hvc/hvc_console.h"
)
EXPECTED_ROADMAP_DESTINATIONS = [
    "drivers/watchdog/*.zig",
    "drivers/tty/hvc/*.zig",
    "zigux/tests/",
    "Documentation/zigux/",
]
EXPECTED_SURVEY_SUMMARY = {
    "shared_phase11_build_present": True,
    "shared_phase11_header_note_present": True,
    "shared_phase11_header_survey_present": True,
    "watchdog_info_layout_assert_present": True,
    "winsize_layout_assert_present": True,
    "hvc_header_constants_checked": True,
    "hvc_export_surface_checked": True,
}

REQUIRED_GAP_SPECS = {
    "phase11-build-gate": {
        "status": "starter_landed",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase11_build.zig",
        "why_now_contains": "shared Phase 11 build gate",
    },
    "phase11-uapi-header-parity-survey-gate": {
        "status": "starter_landed",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "why_now_contains": "watchdog_info and winsize layout checkpoints",
    },
    "phase11-uapi-header-parity-note": {
        "status": "starter_landed",
        "kind": "documentation",
        "zigux_destination": "Documentation/zigux/phase11-uapi-header-parity-survey.md",
        "why_now_contains": "shared-versus-dedicated replay split",
    },
    "phase11-dw-wdt-watchdog-info-layout-assert": {
        "status": "starter_landed",
        "kind": "header_layout",
        "zigux_destination": "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "why_now_contains": "size 40, alignment 4",
    },
    "phase11-hvc-console-winsize-layout-assert": {
        "status": "starter_landed",
        "kind": "header_layout",
        "zigux_destination": "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "why_now_contains": "size 8, alignment 2",
    },
    "phase11-hvc-console-header-constant-assert": {
        "status": "starter_landed",
        "kind": "header_constants",
        "zigux_destination": "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "why_now_contains": "MAX_NR_HVC_CONSOLES and HVC_ALLOC_TTY_ADAPTERS",
    },
    "phase11-hvc-console-export-signature-assert": {
        "status": "starter_landed",
        "kind": "export_surface",
        "zigux_destination": "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "why_now_contains": "notifier_hangup_irq",
    },
}

REQUIRED_NOTE_MARKERS = [
    "PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored",
    f"lane: `{EXPECTED_LANE_KEY}`",
    "phase11-dw-wdt-watchdog-header-boundary",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-header-constant-assert",
    "phase11-hvc-console-export-signature-assert",
    "phase11-uapi-header-parity-surface",
    "MAX_NR_HVC_CONSOLES",
    "HVC_ALLOC_TTY_ADAPTERS",
    "notifier_hangup_irq",
    "dedicated `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` step",
    "rather than the shared `test` step",
]

FORBIDDEN_NOTE_MARKERS = [
    "drivers/tty/hvc/hvc_console.zig",
]

REQUIRED_SURVEY_MARKERS = [
    "phase11 shared header parity survey manifest records the maintained packet cleanly",
    "phase11 shared header parity survey keeps a bounded watchdog_info layout proof",
    "phase11 shared header parity survey keeps a bounded winsize layout proof",
    "phase11 shared header parity survey keeps the note pinned to the manifest provenance",
    "phase11 shared header parity survey keeps shared replay markers explicit without a missing inventory fixture",
    "phase11 shared header parity survey keeps the hvc header constants explicit",
    "phase11 shared header parity survey keeps the exported hvc header declarations explicit",
    "phase11 shared header parity survey keeps the shared build hook explicit",
    "layout_assert.assertSize(WatchdogInfo, 40);",
    "layout_assert.assertAlign(WatchdogInfo, 4);",
    'layout_assert.assertFieldType(WatchdogInfo, "options", u32);',
    'layout_assert.assertFieldType(WatchdogInfo, "firmware_version", u32);',
    'layout_assert.assertFieldType(WatchdogInfo, "identity", [32]u8);',
    'layout_assert.assertOffset(WatchdogInfo, "options", 0);',
    'layout_assert.assertOffset(WatchdogInfo, "firmware_version", 4);',
    'layout_assert.assertOffset(WatchdogInfo, "identity", 8);',
    "layout_assert.assertSize(WinSize, 8);",
    "layout_assert.assertAlign(WinSize, 2);",
    'layout_assert.assertFieldType(WinSize, "ws_row", u16);',
    'layout_assert.assertFieldType(WinSize, "ws_col", u16);',
    'layout_assert.assertFieldType(WinSize, "ws_xpixel", u16);',
    'layout_assert.assertFieldType(WinSize, "ws_ypixel", u16);',
    'layout_assert.assertOffset(WinSize, "ws_row", 0);',
    'layout_assert.assertOffset(WinSize, "ws_col", 2);',
    'layout_assert.assertOffset(WinSize, "ws_xpixel", 4);',
    'layout_assert.assertOffset(WinSize, "ws_ypixel", 6);',
    'try expectContains(hvc_header, "#define MAX_NR_HVC_CONSOLES\\t16");',
    'try expectContains(hvc_header, "#define HVC_ALLOC_TTY_ADAPTERS\\t8");',
]

REQUIRED_BUILD_MARKERS = [
    "phase11_uapi_header_parity_survey.zig",
    "phase11-uapi-header-parity-survey-tests",
    "phase11-hvc-console-survey-tests",
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
    'phase11_uapi_header_parity_survey_module.addImport("layout_assert", layout_assert_module);',
]

REQUIRED_CONTRACT_MARKERS = [
    "PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`",
    "there is no broader multi-checker Phase 11 validator stack on `master`",
]

REQUIRED_HVC_HEADER_MARKERS = [
    "#define MAX_NR_HVC_CONSOLES\t16",
    "#define HVC_ALLOC_TTY_ADAPTERS\t8",
    "extern int hvc_instantiate(uint32_t vtermno, int index,",
    "extern struct hvc_struct * hvc_alloc(uint32_t vtermno, int data,",
    "extern void hvc_remove(struct hvc_struct *hp);",
    "int hvc_poll(struct hvc_struct *hp);",
    "void hvc_kick(void);",
    "extern void __hvc_resize(struct hvc_struct *hp, struct winsize ws);",
    "extern int notifier_add_irq(struct hvc_struct *hp, int data);",
    "extern void notifier_del_irq(struct hvc_struct *hp, int data);",
    "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);",
]

FIXTURE_SURVEYED_COMMIT = "fixture-phase11-shared-header-packet"


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{label} missing markers: {', '.join(missing)}")


def forbid_markers(text: str, markers: list[str], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise SystemExit(f"{label} contains stale markers: {', '.join(present)}")


def check_manifest(manifest: dict[str, object]) -> None:
    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        raise SystemExit("manifest lane_key mismatch")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise SystemExit("manifest phase mismatch")
    if manifest.get("anchor") != EXPECTED_ANCHOR:
        raise SystemExit("manifest anchor mismatch")
    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        raise SystemExit("manifest roadmap destinations mismatch")
    if manifest.get("survey_summary") != EXPECTED_SURVEY_SUMMARY:
        raise SystemExit("manifest survey_summary mismatch")

    gaps = manifest.get("gaps", [])
    gap_specs = {gap["id"]: gap for gap in gaps}
    if set(gap_specs) != set(REQUIRED_GAP_SPECS):
        raise SystemExit(f"manifest gap ids mismatch: {sorted(gap_specs)}")

    for gap_id, expected in REQUIRED_GAP_SPECS.items():
        gap = gap_specs[gap_id]
        for key in ("status", "kind", "zigux_destination"):
            if gap.get(key) != expected[key]:
                raise SystemExit(f"{gap_id} {key} mismatch")
        why_now = gap.get("why_now")
        if not isinstance(why_now, str) or expected["why_now_contains"] not in why_now:
            raise SystemExit(f"{gap_id} why_now mismatch")


def check_repo(root: Path) -> None:
    manifest = json.loads(read_text(root, "zigux/tests/phase11_uapi_header_parity_manifest.json"))
    check_manifest(manifest)

    note = read_text(root, "Documentation/zigux/phase11-uapi-header-parity-survey.md")
    survey = read_text(root, "zigux/tests/phase11_uapi_header_parity_survey.zig")
    build = read_text(root, "zigux/tests/phase11_build.zig")
    contract = read_text(root, "Documentation/zigux/phase11-shared-replay-contract.md")
    hvc_header = read_text(root, "drivers/tty/hvc/hvc_console.h")

    require_markers(note, REQUIRED_NOTE_MARKERS + [manifest["surveyed_commit"]], "note")
    forbid_markers(note, FORBIDDEN_NOTE_MARKERS, "note")
    require_markers(survey, REQUIRED_SURVEY_MARKERS, "survey")
    require_markers(build, REQUIRED_BUILD_MARKERS, "build")
    require_markers(contract, REQUIRED_CONTRACT_MARKERS, "contract")
    require_markers(hvc_header, REQUIRED_HVC_HEADER_MARKERS, "hvc_header")


def build_fixture_repo(root: Path) -> None:
    manifest = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": FIXTURE_SURVEYED_COMMIT,
        "anchor": EXPECTED_ANCHOR,
        "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "survey_summary": EXPECTED_SURVEY_SUMMARY,
        "gaps": [
            {
                "id": gap_id,
                "status": spec["status"],
                "kind": spec["kind"],
                "zigux_destination": spec["zigux_destination"],
                "why_now": f"fixture {spec['why_now_contains']}",
            }
            for gap_id, spec in REQUIRED_GAP_SPECS.items()
        ],
    }
    write_text(
        root,
        "zigux/tests/phase11_uapi_header_parity_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase11-uapi-header-parity-survey.md",
        "\n".join(REQUIRED_NOTE_MARKERS + [FIXTURE_SURVEYED_COMMIT]) + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "\n".join(REQUIRED_SURVEY_MARKERS) + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase11_build.zig",
        "\n".join(REQUIRED_BUILD_MARKERS) + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase11-shared-replay-contract.md",
        "\n".join(REQUIRED_CONTRACT_MARKERS) + "\n",
    )
    write_text(
        root,
        "drivers/tty/hvc/hvc_console.h",
        "\n".join(REQUIRED_HVC_HEADER_MARKERS) + "\n",
    )


def expect_failure(root: Path, rel: str, stale_marker: str, replacement: str, expected_fragment: str) -> None:
    path = root / rel
    original = path.read_text(encoding="utf-8")
    if stale_marker not in original:
        raise SystemExit(f"fixture is missing stale marker for {rel}: {stale_marker}")
    path.write_text(original.replace(stale_marker, replacement, 1), encoding="utf-8")
    try:
        check_repo(root)
    except SystemExit as exc:
        if expected_fragment not in str(exc):
            raise SystemExit(f"unexpected failure for {rel}: {exc}") from exc
    else:
        raise SystemExit(f"expected failure for {rel}")
    finally:
        path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def run_case(rel: str, stale_marker: str, replacement: str, expected_fragment: str) -> None:
        nonlocal case_count
        expect_failure(root, rel, stale_marker, replacement, expected_fragment)
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase11-header-packet-") as tmp:
        root = Path(tmp)
        build_fixture_repo(root)
        check_repo(root)
        run_case(
            "Documentation/zigux/phase11-uapi-header-parity-survey.md",
            "phase11-uapi-header-parity-surface",
            "phase11-uapi-header-parity-surface\ndrivers/tty/hvc/hvc_console.zig",
            "note contains stale markers",
        )
        run_case(
            "Documentation/zigux/phase11-uapi-header-parity-survey.md",
            "phase11-uapi-header-parity-surface",
            "phase11-uapi-header-packet-absent",
            "note missing markers",
        )
        run_case(
            "Documentation/zigux/phase11-uapi-header-parity-survey.md",
            "phase11-hvc-console-header-constant-assert",
            "phase11-hvc-console-header-constant-proof",
            "note missing markers",
        )
        run_case(
            "Documentation/zigux/phase11-uapi-header-parity-survey.md",
            "rather than the shared `test` step",
            "through the shared test step",
            "note missing markers",
        )
        run_case(
            "Documentation/zigux/phase11-shared-replay-contract.md",
            "zigux/tests/phase11_uapi_header_parity_survey.zig",
            "zigux/tests/phase11_header_packet_absent.zig",
            "contract missing markers",
        )
        run_case(
            "drivers/tty/hvc/hvc_console.h",
            "#define HVC_ALLOC_TTY_ADAPTERS\t8",
            "#define HVC_ALLOC_TTY_ADAPTERS\t4",
            "hvc_header missing markers",
        )
        run_case(
            "drivers/tty/hvc/hvc_console.h",
            "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);",
            "extern void notifier_hangup_irq(struct hvc_struct *hp, unsigned long data);",
            "hvc_header missing markers",
        )
        run_case(
            "zigux/tests/phase11_uapi_header_parity_manifest.json",
            '"winsize_layout_assert_present": true',
            '"winsize_layout_assert_present": false',
            "manifest survey_summary mismatch",
        )
        run_case(
            "zigux/tests/phase11_uapi_header_parity_manifest.json",
            '"zigux_destination": "zigux/tests/phase11_uapi_header_parity_survey.zig"',
            '"zigux_destination": "zigux/tests/phase11_uapi_header_packet_survey.zig"',
            "zigux_destination mismatch",
        )
        run_case(
            "zigux/tests/phase11_uapi_header_parity_survey.zig",
            'layout_assert.assertOffset(WatchdogInfo, "identity", 8);',
            'layout_assert.assertOffset(WatchdogInfo, "identity", 12);',
            "survey missing markers",
        )
        run_case(
            "zigux/tests/phase11_uapi_header_parity_survey.zig",
            'layout_assert.assertFieldType(WinSize, "ws_ypixel", u16);',
            'layout_assert.assertFieldType(WinSize, "ws_ypixel", u32);',
            "survey missing markers",
        )
        run_case(
            "zigux/tests/phase11_uapi_header_parity_survey.zig",
            'try expectContains(hvc_header, "#define HVC_ALLOC_TTY_ADAPTERS\\t8");',
            'try expectContains(hvc_header, "#define HVC_ALLOC_TTY_ADAPTERS\\t4");',
            "survey missing markers",
        )
    print("phase11-header-boundary-packet: self-test passed")
    print(f"phase11-header-boundary-packet: self-test cases={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.repo_root).resolve()
    check_repo(root)
    print("phase11-header-boundary-packet: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

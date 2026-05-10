#!/usr/bin/env python3

"""Audit the newer shared Phase 11 header-boundary contract markers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REQUIRED_GAP_IDS = {
    "phase11-build-gate",
    "phase11-uapi-header-parity-survey-gate",
    "phase11-uapi-header-parity-note",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
}

REQUIRED_NOTE_MARKERS = [
    "PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored",
    "lane: `P11-L18`",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
    "drivers/tty/hvc/hvc_console.h",
    "notifier_hangup_irq",
    "dedicated `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` step",
    "rather than the shared `test` step",
]

FORBIDDEN_NOTE_MARKERS = [
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "drivers/tty/hvc/hvc_console.zig",
]

REQUIRED_CONTRACT_MARKERS = [
    "there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`",
    "scripts/zigux/check-phase11-header-boundary-packet.py",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "zigux/tests/phase11_uapi_header_parity_manifest.json",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
]

REQUIRED_HEADER_MARKERS = [
    "struct hv_ops",
    "extern int hvc_instantiate",
    "extern struct hvc_struct * hvc_alloc",
    "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);",
]


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def require_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{label} missing markers: {', '.join(missing)}")


def require_absent(text: str, markers: list[str], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise SystemExit(f"{label} still carries stale markers: {', '.join(present)}")


def check_repo(root: Path) -> None:
    manifest = json.loads(read_text(root, "zigux/tests/phase11_uapi_header_parity_manifest.json"))
    note = read_text(root, "Documentation/zigux/phase11-uapi-header-parity-survey.md")
    contract = read_text(root, "Documentation/zigux/phase11-shared-replay-contract.md")
    header = read_text(root, "drivers/tty/hvc/hvc_console.h")

    if manifest.get("lane_key") != "P11-L18":
        raise SystemExit("manifest lane_key mismatch")
    if manifest.get("phase") != "Phase 11":
        raise SystemExit("manifest phase mismatch")
    if "drivers/tty/hvc/hvc_console.h" not in manifest.get("anchor", ""):
        raise SystemExit("manifest anchor missing hvc_console.h")

    summary = manifest.get("survey_summary", {})
    required_true = [
        "shared_phase11_build_present",
        "shared_phase11_header_note_present",
        "shared_phase11_header_survey_present",
        "watchdog_info_layout_assert_present",
        "winsize_layout_assert_present",
        "hvc_export_surface_checked",
    ]
    for key in required_true:
        if not summary.get(key):
            raise SystemExit(f"manifest survey_summary missing truthy {key}")

    gaps = manifest.get("gaps", [])
    gap_ids = {gap.get("id") for gap in gaps}
    if gap_ids != REQUIRED_GAP_IDS:
        raise SystemExit(f"manifest gap ids mismatch: {sorted(gap_ids)}")

    export_gap = next(
        (gap for gap in gaps if gap.get("id") == "phase11-hvc-console-export-signature-assert"),
        None,
    )
    if export_gap is None or "notifier_hangup_irq" not in export_gap.get("why_now", ""):
        raise SystemExit("manifest export gap missing notifier_hangup_irq")

    survey_gap = next(
        (gap for gap in gaps if gap.get("id") == "phase11-uapi-header-parity-survey-gate"),
        None,
    )
    if survey_gap is None:
        raise SystemExit("manifest missing survey gate")
    if "build-inventory" in survey_gap.get("why_now", ""):
        raise SystemExit("manifest survey gate still mentions build-inventory")

    require_markers(note, REQUIRED_NOTE_MARKERS + [manifest["surveyed_commit"]], "note")
    require_absent(note, FORBIDDEN_NOTE_MARKERS, "note")
    require_markers(contract, REQUIRED_CONTRACT_MARKERS, "shared replay contract")
    require_markers(header, REQUIRED_HEADER_MARKERS, "hvc header")


def run_self_test() -> None:
    good_manifest = {
        "lane_key": "P11-L18",
        "phase": "Phase 11",
        "surveyed_commit": "ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839",
        "anchor": "include/uapi/linux/watchdog.h + include/uapi/asm-generic/termios.h + drivers/tty/hvc/hvc_console.h",
        "survey_summary": {
            "shared_phase11_build_present": True,
            "shared_phase11_header_note_present": True,
            "shared_phase11_header_survey_present": True,
            "watchdog_info_layout_assert_present": True,
            "winsize_layout_assert_present": True,
            "hvc_export_surface_checked": True,
        },
        "gaps": [
            {
                "id": "phase11-build-gate",
                "why_now": "keep the shared build gate explicit",
            },
            {
                "id": "phase11-uapi-header-parity-survey-gate",
                "why_now": "replays the bounded watchdog_info and winsize layout checkpoints plus the exported hvc helper surface",
            },
            {
                "id": "phase11-uapi-header-parity-note",
                "why_now": "shared note",
            },
            {
                "id": "phase11-dw-wdt-watchdog-info-layout-assert",
                "why_now": "watchdog layout",
            },
            {
                "id": "phase11-hvc-console-winsize-layout-assert",
                "why_now": "winsize layout",
            },
            {
                "id": "phase11-hvc-console-export-signature-assert",
                "why_now": "checks notifier_hangup_irq in the bounded public header surface",
            },
        ],
    }

    good_note = "\n".join(
        [
            "`PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored`",
            "- lane: `P11-L18`",
            "- `phase11-dw-wdt-watchdog-info-layout-assert`",
            "- `phase11-hvc-console-winsize-layout-assert`",
            "- `phase11-hvc-console-export-signature-assert`",
            "- `drivers/tty/hvc/hvc_console.h`",
            "- `notifier_hangup_irq`",
            "- dedicated `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` step",
            "- rather than the shared `test` step",
            "- `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`",
        ]
    )
    good_contract = "\n".join(REQUIRED_CONTRACT_MARKERS)
    good_header = "\n".join(REQUIRED_HEADER_MARKERS)

    root = Path("/tmp/phase11-header-current-contract-self-test")
    if root.exists():
        for path in sorted(root.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()
    (root / "Documentation/zigux").mkdir(parents=True)
    (root / "zigux/tests").mkdir(parents=True)
    (root / "drivers/tty/hvc").mkdir(parents=True)
    (root / "Documentation/zigux/phase11-uapi-header-parity-survey.md").write_text(good_note, encoding="utf-8")
    (root / "Documentation/zigux/phase11-shared-replay-contract.md").write_text(good_contract, encoding="utf-8")
    (root / "drivers/tty/hvc/hvc_console.h").write_text(good_header, encoding="utf-8")
    (root / "zigux/tests/phase11_uapi_header_parity_manifest.json").write_text(
        json.dumps(good_manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    check_repo(root)

    bad_manifest = dict(good_manifest)
    bad_manifest["lane_key"] = "P11-L08"
    (root / "zigux/tests/phase11_uapi_header_parity_manifest.json").write_text(
        json.dumps(bad_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        check_repo(root)
    except SystemExit as exc:
        if "lane_key mismatch" not in str(exc):
            raise
    else:
        raise SystemExit("self-test expected manifest lane mismatch")

    (root / "zigux/tests/phase11_uapi_header_parity_manifest.json").write_text(
        json.dumps(good_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "Documentation/zigux/phase11-uapi-header-parity-survey.md").write_text(
        good_note + "\nzigux/tests/fixtures/phase11_build_inventory.json\n",
        encoding="utf-8",
    )
    try:
        check_repo(root)
    except SystemExit as exc:
        if "stale markers" not in str(exc):
            raise
    else:
        raise SystemExit("self-test expected stale note marker failure")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("phase11-header-boundary-current-contract: self-test passed")
        return 0

    root = Path(args.repo_root).resolve()
    check_repo(root)
    print("phase11-header-boundary-current-contract: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

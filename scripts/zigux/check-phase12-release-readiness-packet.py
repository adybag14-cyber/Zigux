#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=release_readiness_packet

Fail-closed checker for the bounded Phase 12 release-readiness fallback note.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=release_readiness_packet"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
ROADMAP_PATH = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
PHASE12_SECTION_HEADING = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers"
ROADMAP_ANCHORS = [
    "`drivers/net/virtio_net.c`",
    "`drivers/nvme/host/pci.c`",
    "`drivers/scsi/virtio_scsi.c`",
    "`tools/lib/bpf/libbpf.c`",
]
RELEASE_READINESS_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_RELEASE_CLOSED=no`",
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
    "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "If `zig` is unavailable on `PATH`, keep that same smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing `phase12-validate`, a focused libbpf-only replay, or another unshipped Phase 12 replay surface.",
    "Keep the same degraded-workflow validation pair explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` should run before or beside those attached-toolchain Make reruns so build-only contract drift still fails closed when the local runtime needs the fallback path.",
    "The smaller unshipped boundary is still the validator-first side of the lane: current `master` now ships `scripts/zigux/validate-phase12.py` as an unwired helper plus the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` fallback-note guard, but it still does not expose a broader shared `check-phase12-*.py` family, a focused libbpf-only replay, a cross-build replay, or `make -C zigux phase12-validate`, so release-planning notes should keep treating `validate-phase12.py` as support material rather than as shipped release evidence while naming only the shipped checker pair, smoke shard, full complex-driver replay, Linux-style Make routes, and the parked survey or fallback companions.",
    "The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier foothold, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.",
    "During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet, so fallback wording should keep them visible without promoting them into extra commit-pinned artifacts.",
]


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_section(text: str, heading: str) -> str | None:
    active = False
    collected: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == heading:
            active = True
        elif active and stripped.startswith("## "):
            break
        if active:
            collected.append(line)
    if not collected:
        return None
    return "\n".join(collected) + "\n"


def extract_bullets(text: str, heading: str) -> list[str]:
    active = False
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == heading:
            active = True
            continue
        if not active:
            continue
        if bullets and stripped and not stripped.startswith("- "):
            break
        if stripped.startswith("- "):
            bullets.append(stripped[2:])
    return bullets


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    required_files = [
        root / RELEASE_READINESS_PATH,
        root / ROADMAP_PATH,
        root / BUILD_ONLY_CHECKER_PATH,
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(root).as_posix()}")
    if errors:
        return errors

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    release_text = read_text(root / RELEASE_READINESS_PATH)
    require_exact_count(
        errors,
        RELEASE_READINESS_PATH,
        release_text,
        RELEASE_READINESS_MARKERS,
    )

    roadmap_section = extract_section(read_text(root / ROADMAP_PATH), PHASE12_SECTION_HEADING)
    if roadmap_section is None:
        errors.append(f"missing roadmap section: {PHASE12_SECTION_HEADING}")
    else:
        anchors = extract_bullets(roadmap_section, "Primary Linux anchors:")
        if anchors != ROADMAP_ANCHORS:
            errors.append("roadmap Phase 12 anchor list drifted from the expected four-entry set")

    return errors


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def good_release_readiness_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Release Readiness Survey",
            "",
            "## Status",
            "- `PHASE12_STATUS=active`",
            "- `PHASE12_RELEASE_CLOSED=no`",
            "- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
            "- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "",
            "## Current Release Reading",
            "- If `zig` is unavailable on `PATH`, keep that same smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing `phase12-validate`, a focused libbpf-only replay, or another unshipped Phase 12 replay surface.",
            "- Keep the same degraded-workflow validation pair explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` should run before or beside those attached-toolchain Make reruns so build-only contract drift still fails closed when the local runtime needs the fallback path.",
            "- The smaller unshipped boundary is still the validator-first side of the lane: current `master` now ships `scripts/zigux/validate-phase12.py` as an unwired helper plus the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` fallback-note guard, but it still does not expose a broader shared `check-phase12-*.py` family, a focused libbpf-only replay, a cross-build replay, or `make -C zigux phase12-validate`, so release-planning notes should keep treating `validate-phase12.py` as support material rather than as shipped release evidence while naming only the shipped checker pair, smoke shard, full complex-driver replay, Linux-style Make routes, and the parked survey or fallback companions.",
            "- The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier foothold, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.",
            "- During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet, so fallback wording should keep them visible without promoting them into extra commit-pinned artifacts.",
            "",
        ]
    )


def good_roadmap_text() -> str:
    return "\n".join(
        [
            "# ZAR to Zigux Product Roadmap",
            "",
            PHASE12_SECTION_HEADING,
            "",
            "Primary Linux anchors:",
            *[f"- {item}" for item in ROADMAP_ANCHORS],
            "",
        ]
    )


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        raise SystemExit(f"{label}: {errors!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-check-"))
    try:
        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(tmp_root / ROADMAP_PATH, good_roadmap_text())
        write(tmp_root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")

        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "self-test expected support-checker failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "If `zig` is unavailable on `PATH`, keep that same smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing `phase12-validate`, a focused libbpf-only replay, or another unshipped Phase 12 replay surface.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "If `zig` is unavailable on `PATH`",
            "self-test expected fallback-command failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "Keep the same degraded-workflow validation pair explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` should run before or beside those attached-toolchain Make reruns so build-only contract drift still fails closed when the local runtime needs the fallback path.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Keep the same degraded-workflow validation pair explicit too:",
            "self-test expected checker-pair failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "The smaller unshipped boundary is still the validator-first side of the lane: current `master` now ships `scripts/zigux/validate-phase12.py` as an unwired helper plus the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` fallback-note guard, but it still does not expose a broader shared `check-phase12-*.py` family, a focused libbpf-only replay, a cross-build replay, or `make -C zigux phase12-validate`, so release-planning notes should keep treating `validate-phase12.py` as support material rather than as shipped release evidence while naming only the shipped checker pair, smoke shard, full complex-driver replay, Linux-style Make routes, and the parked survey or fallback companions.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "The smaller unshipped boundary is still the validator-first side of the lane:",
            "self-test expected validator-boundary failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier foothold, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "The public fallback split must stay explicit:",
            "self-test expected fallback-split failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet, so fallback wording should keep them visible without promoting them into extra commit-pinned artifacts.\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet",
            "self-test expected shared-tree-anchor failure",
        )

        write(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write(
            tmp_root / ROADMAP_PATH,
            good_roadmap_text().replace("- `drivers/scsi/virtio_scsi.c`\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "roadmap Phase 12 anchor list drifted",
            "self-test expected roadmap-anchor failure",
        )

        write(tmp_root / ROADMAP_PATH, good_roadmap_text())
        (tmp_root / BUILD_ONLY_CHECKER_PATH).unlink()
        expect_contains(
            check(tmp_root, source_text=MARKER),
            f"missing file: {BUILD_ONLY_CHECKER_PATH}",
            "self-test expected companion-checker presence failure",
        )
        write(tmp_root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")

        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "self-test expected checker-marker failure",
        )

    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="repository root to validate (defaults to the checker directory)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("phase12 release-readiness packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

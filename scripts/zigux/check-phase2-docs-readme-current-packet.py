#!/usr/bin/env python3
"""Guard the current docs-root Phase 2 reminder packet."""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

STATUS_PREFIX = "PHASE2_DOCS_README_CURRENT_PACKET"


@dataclass(frozen=True)
class PacketFile:
    path: str
    label: str
    markers: tuple[str, ...]


PACKET_FILES = (
    PacketFile(
        path="Documentation/zigux/README.md",
        label="DOCS",
        markers=(
            "Documentation/zigux/phase2-closure.md",
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "scripts/zigux/install-zig.py",
            "scripts/zigux/check-phase2-cross.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "make -C zigux phase2",
        ),
    ),
    PacketFile(
        path="Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        label="NOTES",
        markers=(
            "scripts/zigux/install-zig.py",
            "scripts/zigux/check-phase2-cross.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "make -C zigux phase2-genksyms",
        ),
    ),
    PacketFile(
        path="Documentation/zigux/review-checklist.md",
        label="REVIEW",
        markers=(
            "if the change touches the shared Phase 2 toolchain packet",
            "third_party/README.md",
            "scripts/zigux/check-phase2-tests-readme-alignment.py",
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/check-genksyms-bridge.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
            "scripts/zigux/check-phase2-cross.py",
            "zigux/tests/fixtures/phase2_cross_targets.json",
        ),
    ),
    PacketFile(
        path="zigux/tests/README.md",
        label="TESTS",
        markers=(
            "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
            "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
            "scripts/zigux/check-genksyms-bridge.py",
            "make -C zigux phase2-genksyms",
        ),
    ),
    PacketFile(
        path="third_party/README.md",
        label="THIRD_PARTY",
        markers=(
            "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
            "community-mirrors.txt",
            "scripts/zigux/check-lane05-local-first-archive-workflow.py",
            "scripts/zigux/check-lane05-install-zig-archive-verification.py",
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_content(packet: PacketFile) -> str:
    lines = [f"# sample for {packet.path}", ""]
    for marker in packet.markers:
        lines.append(f"- {marker}")
    lines.append("")
    return "\n".join(lines)


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for packet in PACKET_FILES:
        write_file(root / packet.path, sample_content(packet))


def check_root(root: Path) -> list[str]:
    outputs: list[str] = []
    for packet in PACKET_FILES:
        path = root / packet.path
        if not path.is_file():
            raise SystemExit(f"missing required path: {packet.path}")
        content = path.read_text(encoding="utf-8")
        missing = [marker for marker in packet.markers if marker not in content]
        if missing:
            raise SystemExit(
                f"{packet.path} missing marker(s): " + ", ".join(repr(marker) for marker in missing)
            )
        outputs.append(f"{STATUS_PREFIX}_{packet.label}_MARKER_COUNT={len(packet.markers)}")
    return outputs


def expect_failure(root: Path, needle: str) -> None:
    try:
        check_root(root)
    except SystemExit as exc:
        if needle not in str(exc):
            raise AssertionError(f"expected {needle!r} in {exc!s}") from exc
        return
    raise AssertionError(f"expected failure containing {needle!r}")


def run_self_test() -> None:
    base = Path("/tmp/phase2_docs_readme_current_packet_selftest")
    sample = base / "sample"
    cases = []

    write_sample_root(sample)
    check_root(sample)
    cases.append("round_trip")

    for packet in PACKET_FILES:
        case_root = base / f"missing_path_{packet.label.lower()}"
        write_sample_root(case_root)
        (case_root / packet.path).unlink()
        expect_failure(case_root, f"missing required path: {packet.path}")
        cases.append(f"missing_path_{packet.label.lower()}")

    for packet in PACKET_FILES:
        case_root = base / f"missing_marker_{packet.label.lower()}"
        write_sample_root(case_root)
        path = case_root / packet.path
        content = path.read_text(encoding="utf-8")
        path.write_text(content.replace(packet.markers[0], "marker removed", 1), encoding="utf-8")
        expect_failure(case_root, packet.markers[0])
        cases.append(f"missing_marker_{packet.label.lower()}")

    print(f"{STATUS_PREFIX}_SELF_TEST=pass")
    print(f"{STATUS_PREFIX}_SELF_TEST_CASE_COUNT={len(cases)}")


def main() -> int:
    args = parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)

    if args.self_test:
        run_self_test()
        return 0

    outputs = check_root(args.root)
    print(f"{STATUS_PREFIX}=pass")
    for line in outputs:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())

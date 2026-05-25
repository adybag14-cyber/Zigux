#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REQUIRED_FILES = [
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/build.zig",
    ".github/workflows/zigux-bootstrap.yml",
]

SURVEY_MARKERS = (
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "drivers/net/virtio_net_throughput_parity.zig",
    "throughput helper remains review-only throughput-ratio checks",
    "explicit receive-refill and transmit-recycle readiness booleans",
)

MANIFEST_MARKERS = (
    '"status": "throughput_parity_helper_present_review_only_runtime_completion_missing"',
    "review-only throughput-ratio checks",
    "explicit receive-refill and transmit-recycle readiness booleans",
    "Measured transport throughput evidence",
)

PHASE12_BUILD_MARKERS = (
    "../../drivers/net/virtio_net_throughput_parity.zig",
    '"phase12_virtio_net_throughput_parity.zig"',
    '"phase12-virtio-net-throughput-parity-tests"',
    "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
)

SHARED_BUILD_MARKERS = (
    "../../drivers/net/virtio_net_throughput_parity.zig",
    '"phase12_virtio_net_throughput_parity.zig"',
    '"phase12-virtio-net-throughput-parity"',
    "const phase12_virtio_net_throughput_parity = addPhase12VirtioNetThroughputParity(",
    "phase12_step.dependOn(&phase12_virtio_net_throughput_parity.step);",
    "phase12_throughput_step.dependOn(&phase12_virtio_net_throughput_parity.step);",
)

WORKFLOW_MARKERS = (
    "- name: Run current Phase 12 throughput-parity anchor",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
)


class CheckError(RuntimeError):
    pass


def require_file(root: Path, rel: str) -> Path:
    path = root / rel
    if not path.is_file():
        raise CheckError(f"missing required file: {rel}")
    return path


def require_markers(path: Path, markers: tuple[str, ...]) -> str:
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{path.as_posix()}: missing marker {marker!r}")
    return text


def run_check(root: Path) -> None:
    for rel in REQUIRED_FILES:
        require_file(root, rel)

    require_markers(
        require_file(root, "Documentation/zigux/phase12-virtio-net-survey.md"),
        SURVEY_MARKERS,
    )
    require_markers(
        require_file(root, "zigux/tests/phase12_virtio_net_manifest.json"),
        MANIFEST_MARKERS,
    )
    require_markers(
        require_file(root, "zigux/tests/phase12_build.zig"),
        PHASE12_BUILD_MARKERS,
    )
    require_markers(
        require_file(root, "zigux/tests/build.zig"),
        SHARED_BUILD_MARKERS,
    )
    require_markers(
        require_file(root, ".github/workflows/zigux-bootstrap.yml"),
        WORKFLOW_MARKERS,
    )

    manifest_path = root / "zigux/tests/phase12_virtio_net_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("lane_key") != "P12-L04":
        raise CheckError(f"{manifest_path.as_posix()}: lane_key drifted from 'P12-L04'")
    if manifest.get("anchor") != "drivers/net/virtio_net.c":
        raise CheckError(
            f"{manifest_path.as_posix()}: anchor drifted from 'drivers/net/virtio_net.c'"
        )


def make_fixture_tree(root: Path) -> None:
    payloads = {
        "Documentation/zigux/phase12-virtio-net-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
        "drivers/net/virtio_net_throughput_parity.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_throughput_parity.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_manifest.json": json.dumps(
            {
                "lane_key": "P12-L04",
                "anchor": "drivers/net/virtio_net.c",
                "roadmap_gap_check": {
                    "throughput_and_recovery_parity": {
                        "status": "throughput_parity_helper_present_review_only_runtime_completion_missing",
                        "current_surface": "review-only throughput-ratio checks with explicit receive-refill and transmit-recycle readiness booleans",
                        "blocked_by": "Measured transport throughput evidence remains outside the packet.",
                    }
                },
            },
            indent=2,
        ) + "\n",
        "zigux/tests/phase12_build.zig": "\n".join(PHASE12_BUILD_MARKERS) + "\n",
        "zigux/tests/build.zig": "\n".join(SHARED_BUILD_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
    }
    for rel, text in payloads.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-throughput-anchor-") as tmp:
        base = Path(tmp)
        make_fixture_tree(base)
        run_check(base)
        cases += 1

        for rel in (
            "Documentation/zigux/phase12-virtio-net-survey.md",
            "zigux/tests/phase12_virtio_net_manifest.json",
            "zigux/tests/phase12_build.zig",
            "zigux/tests/build.zig",
            ".github/workflows/zigux-bootstrap.yml",
        ):
            make_fixture_tree(base)
            (base / rel).write_text("broken\n", encoding="utf-8")
            try:
                run_check(base)
            except (CheckError, json.JSONDecodeError):
                pass
            else:
                raise AssertionError(f"expected failure for {rel}")
            cases += 1

    print("PHASE12_VIRTIO_NET_THROUGHPUT_ANCHOR_SELF_TEST=pass")
    print(f"PHASE12_VIRTIO_NET_THROUGHPUT_ANCHOR_SELF_TEST_CASES={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(args.root.resolve())
    except (CheckError, json.JSONDecodeError) as err:
        print("PHASE12_VIRTIO_NET_THROUGHPUT_ANCHOR=fail")
        print(str(err))
        return 1

    print("PHASE12_VIRTIO_NET_THROUGHPUT_ANCHOR=pass")
    print("PHASE12_VIRTIO_NET_THROUGHPUT_ANCHOR_SCOPE=shared-build-root-and-workflow-throughput-route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

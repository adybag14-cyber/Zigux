#!/usr/bin/env python3
"""Guard the live Phase 1 find_bit review workflow packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[3] if len(HERE.parents) > 3 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    CLOSURE_VALIDATOR_REL,
    FIND_BIT_REVIEW_CHECKER_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "Current `master` also ships `scripts/zigux/check-phase1-find-bit-review-packet.py` as the helper-local review-packet guard: it exact-checks `tools/lib/find_bit.zig`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zigux/tests/fixtures/phase1_helpers.json` so the same-word start-mask, inclusive-boundary, `clump8`, `getValue8()`, `findLastBit()`, alias, and committed tail-clamped plus tail-inclusive-boundary replay packet stay aligned on current `master`.",
        "- `PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    ),
    CLOSURE_VALIDATOR_REL: (
        'FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")',
        '    "find_bit_review_guard": "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",',
        '    (FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),',
    ),
    FIND_BIT_REVIEW_CHECKER_REL: (
        'HELPER_REL = Path("tools/lib/find_bit.zig")',
        '"andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",',
        '"review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",',
        'print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")',
        'print("PHASE1_FIND_BIT_REVIEW_PACKET=pass")',
    ),
}

REQUIRED_WORKFLOW_STEPS = (
    (
        "Self-test current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    ),
    (
        "Check current Phase 1 direct-anchor manifest gate",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    ),
    (
        "Self-test current Phase 1 string review checker",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 string review packet",
        "python3 scripts/zigux/check-phase1-string-review-packet.py",
    ),
    (
        "Self-test current Phase 1 find-bit review checker",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 find-bit review packet",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    ),
    (
        "Self-test current Phase 1 route summary checker",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "Check current Phase 1 route summary packet",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_text_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_line_once(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == line.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_workflow_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(
        require_line_once(
            workflow_text,
            f"workflow_step:{step_name}",
            f"- name: {step_name}",
        )
    )
    pair = f"      - name: {step_name}\n        run: {run_command}"
    count = workflow_text.count(pair)
    if count != 1:
        failures.append(f"workflow_run:{step_name}:expected=1:actual={count}")
    return failures


def require_workflow_chain(workflow_text: str) -> list[str]:
    names = workflow_step_names(workflow_text)
    chain = tuple(step for step, _ in REQUIRED_WORKFLOW_STEPS)
    width = len(chain)
    for index in range(len(names) - width + 1):
        if tuple(names[index : index + width]) == chain:
            return []
    return [f"workflow_chain:missing:{'->'.join(chain)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for index, marker in enumerate(markers):
            failures.extend(
                require_text_once(
                    text,
                    f"{relative_path.as_posix()}:marker_{index}",
                    marker,
                )
            )

    workflow_text = read_text(root, WORKFLOW_REL)
    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        failures.extend(require_workflow_step(workflow_text, step_name, run_command))
    failures.extend(require_workflow_chain(workflow_text))

    return failures


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == WORKFLOW_REL:
            continue
        write_text(root, relative_path, "\n".join(REQUIRED_MARKERS.get(relative_path, ())) + "\n")

    workflow_lines = [
        "name: zigux-bootstrap",
        "",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "",
    ]
    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        workflow_lines.append(f"      - name: {step_name}")
        workflow_lines.append(f"        run: {run_command}")
        workflow_lines.append("")
    write_text(root, WORKFLOW_REL, "\n".join(workflow_lines))


def mutate_remove_text(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1).replace(marker, "", 1), encoding="utf-8")


def mutate_duplicate_text(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, object] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("missing_file", relative_path)))

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", ("duplicate", relative_path, marker)))

    for step_name, run_command in REQUIRED_WORKFLOW_STEPS:
        block = f"      - name: {step_name}\n        run: {run_command}\n"
        cases.append((f"missing_step:{step_name}", ("remove", WORKFLOW_REL, block)))
        cases.append((f"duplicate_step:{step_name}", ("duplicate", WORKFLOW_REL, block)))

    cases.append(
        (
            "out_of_order_chain",
            (
                "replace",
                WORKFLOW_REL,
                "      - name: Self-test current Phase 1 string review checker\n        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\n\n"
                "      - name: Self-test current Phase 1 find-bit review checker\n        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test\n\n"
                "      - name: Check current Phase 1 string review packet\n        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n\n"
                "      - name: Check current Phase 1 find-bit review packet\n        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py\n",
            ),
        )
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-find-bit-review-workflow-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation is not None:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    mutate_remove_text(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    mutate_duplicate_text(root, mutation[1], mutation[2])
                elif kind == "replace":
                    path = root / mutation[1]
                    text = path.read_text(encoding="utf-8")
                    old = (
                        "      - name: Self-test current Phase 1 string review checker\n"
                        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\n\n"
                        "      - name: Check current Phase 1 string review packet\n"
                        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n\n"
                        "      - name: Self-test current Phase 1 find-bit review checker\n"
                        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test\n\n"
                        "      - name: Check current Phase 1 find-bit review packet\n"
                        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py\n"
                    )
                    text = text.replace(old, mutation[2], 1)
                    path.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("phase1-find-bit-review-workflow-packet-self-test:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"phase1-find-bit-review-workflow-packet-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_FIND_BIT_REVIEW_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_REVIEW_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_REVIEW_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_REVIEW_WORKFLOW_PACKET=pass")
    print(f"PHASE1_FIND_BIT_REVIEW_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_FIND_BIT_REVIEW_WORKFLOW_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

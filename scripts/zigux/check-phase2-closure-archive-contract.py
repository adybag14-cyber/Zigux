#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
ARCHIVE_CONTRACT_CHECKER = Path("scripts/zigux/check-phase2-archive-contract-packet.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
DOCS_SHARED_REMINDER_CHECKER = Path("scripts/zigux/check-phase2-docs-shared-reminder.py")
TESTS_README_ALIGNMENT_CHECKER = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")

PAYLOAD = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-archive-contract-packet.py`",
    "`scripts/zigux/check-phase2-closure-archive-contract.py`",
    "`python3 scripts/zigux/check-phase2-archive-contract-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase2-archive-contract-packet.py`",
    "`python3 scripts/zigux/check-phase2-closure-archive-contract.py --self-test`",
    "`python3 scripts/zigux/check-phase2-closure-archive-contract.py`",
    "The current closure-side archive-contract packet now stays explicit through `scripts/zigux/check-phase2-archive-contract-packet.py`, `scripts/zigux/check-phase2-closure-archive-contract.py`, `third_party/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` while `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains the lone current repo-reality gap on `master`.",
    f"`PHASE2_CURRENT_GAP_PACKET={PAYLOAD}`",
)

REQUIRED_VALIDATE_CLOSURE_MARKERS = (
    'CLOSURE_ARCHIVE_CONTRACT_REL = Path("scripts/zigux/check-phase2-closure-archive-contract.py")',
    "CLOSURE_ARCHIVE_CONTRACT_REL,",
    '"`scripts/zigux/check-phase2-closure-archive-contract.py`",',
    '"`python3 scripts/zigux/check-phase2-closure-archive-contract.py --self-test`",',
    '"`python3 scripts/zigux/check-phase2-closure-archive-contract.py`",',
)

REQUIRED_DOCS_SHARED_REMINDER_MARKERS = (
    '"`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`",',
    '"`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`",',
    '"`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",',
    '"The bounded Phase 2 packet still has one current repo-reality gap on `master`: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains absent even though its filename, digest, size, local-first fallback order, and allow-missing replay route stay directly reviewable through `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, and the shipped Lane 05 reminder guards.",',
    '"toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-gap truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness",',
)

REQUIRED_TESTS_ALIGNMENT_MARKERS = (
    '"keep the repo-local pinned archive contract explicit through `third_party/README.md`, the pinned `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` filename plus digest and size contract, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers while the payload itself remains absent on current `master`",',
    '"keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",',
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root, PHASE2_CLOSURE)
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    validate_closure_text = read_text(root, VALIDATE_PHASE2_CLOSURE)
    for marker in REQUIRED_VALIDATE_CLOSURE_MARKERS:
        if marker not in validate_closure_text:
            issues.append(("MISSING_VALIDATE_CLOSURE_MARKER", marker))

    archive_checker_text = read_text(root, ARCHIVE_CONTRACT_CHECKER)
    if PAYLOAD not in archive_checker_text:
        issues.append(("MISSING_ARCHIVE_CONTRACT_PAYLOAD", PAYLOAD))

    docs_shared_reminder_text = read_text(root, DOCS_SHARED_REMINDER_CHECKER)
    for marker in REQUIRED_DOCS_SHARED_REMINDER_MARKERS:
        if marker not in docs_shared_reminder_text:
            issues.append(("MISSING_DOCS_SHARED_REMINDER_MARKER", marker))

    tests_alignment_text = read_text(root, TESTS_README_ALIGNMENT_CHECKER)
    for marker in REQUIRED_TESTS_ALIGNMENT_MARKERS:
        if marker not in tests_alignment_text:
            issues.append(("MISSING_TESTS_ALIGNMENT_MARKER", marker))

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                "- `scripts/zigux/check-phase2-archive-contract-packet.py`",
                "- `scripts/zigux/check-phase2-closure-archive-contract.py`",
                "",
                "The current closure-side archive-contract packet now stays explicit through `scripts/zigux/check-phase2-archive-contract-packet.py`, `scripts/zigux/check-phase2-closure-archive-contract.py`, `third_party/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` while `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains the lone current repo-reality gap on `master`.",
                "",
                "- `PHASE2_CURRENT_GAP_PACKET=third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "",
                "- `python3 scripts/zigux/check-phase2-archive-contract-packet.py --self-test`",
                "- `python3 scripts/zigux/check-phase2-archive-contract-packet.py`",
                "- `python3 scripts/zigux/check-phase2-closure-archive-contract.py --self-test`",
                "- `python3 scripts/zigux/check-phase2-closure-archive-contract.py`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATE_PHASE2_CLOSURE,
        "\n".join(
            (
                'CLOSURE_ARCHIVE_CONTRACT_REL = Path("scripts/zigux/check-phase2-closure-archive-contract.py")',
                "REQUIRED_FILES = (",
                "    CLOSURE_ARCHIVE_CONTRACT_REL,",
                ")",
                "REQUIRED_CLOSURE_MARKERS = (",
                '    "`scripts/zigux/check-phase2-closure-archive-contract.py`",',
                '    "`python3 scripts/zigux/check-phase2-closure-archive-contract.py --self-test`",',
                '    "`python3 scripts/zigux/check-phase2-closure-archive-contract.py`",',
                ")",
            )
        )
        + "\n",
    )
    write_text(
        root,
        ARCHIVE_CONTRACT_CHECKER,
        f'PAYLOAD = "{PAYLOAD}"\n',
    )
    write_text(
        root,
        DOCS_SHARED_REMINDER_CHECKER,
        "\n".join(REQUIRED_DOCS_SHARED_REMINDER_MARKERS) + "\n",
    )
    write_text(
        root,
        TESTS_README_ALIGNMENT_CHECKER,
        "\n".join(REQUIRED_TESTS_ALIGNMENT_MARKERS) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_closure_archive_contract_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        write_text(root, PHASE2_CLOSURE, "# broken\n")
        assert any(code == "MISSING_CLOSURE_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, VALIDATE_PHASE2_CLOSURE, "# broken\n")
        assert any(code == "MISSING_VALIDATE_CLOSURE_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, ARCHIVE_CONTRACT_CHECKER, 'PAYLOAD = "missing"\n')
        assert ("MISSING_ARCHIVE_CONTRACT_PAYLOAD", PAYLOAD) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, DOCS_SHARED_REMINDER_CHECKER, "# broken\n")
        assert any(code == "MISSING_DOCS_SHARED_REMINDER_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, TESTS_README_ALIGNMENT_CHECKER, "# broken\n")
        assert any(code == "MISSING_TESTS_ALIGNMENT_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

    print("PHASE2_CLOSURE_ARCHIVE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_ARCHIVE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 22 closure note explicit about the archive-contract packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_CLOSURE_ARCHIVE_CONTRACT=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_CLOSURE_ARCHIVE_CONTRACT=pass")
    print(f"PHASE2_CLOSURE_ARCHIVE_CONTRACT_GAP={PAYLOAD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

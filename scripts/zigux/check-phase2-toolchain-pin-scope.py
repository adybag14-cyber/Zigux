#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

POLICY_PATH = "scripts/zigux/zig-toolchain-policy.json"
REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    POLICY_PATH,
]

FALLBACK_MARKER = (
    "the repo-local `.zig-toolchain` fallback reused by the Linux-style "
    "`phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, "
    "`phase2-cross`, and `phase2` routes when `ZIG` is unset"
)

DOC_MARKERS = {
    "Documentation/zigux/README.md": [
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "phase2-validate",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2",
    ],
    "Documentation/zigux/review-checklist.md": [
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        FALLBACK_MARKER,
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
    ],
    "scripts/zigux/README.md": [
        "check-phase2-toolchain-pin-scope.py --self-test",
        "check-phase2-toolchain-pin-scope.py",
        "phase2-toolchain",
        FALLBACK_MARKER,
    ],
    "zigux/tests/README.md": [
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        FALLBACK_MARKER,
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ],
    "zigux/Makefile": [
        "phase2-toolchain:",
        "check-phase2-toolchain-pin-scope.py --self-test",
        "check-phase2-toolchain-pin-scope.py",
        "phase2-validate: phase2-toolchain",
        "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
    ],
}

EXACT_COUNTS = {
    "Documentation/zigux/review-checklist.md": {
        "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
        FALLBACK_MARKER: 1,
    },
    "Documentation/zigux/README.md": {
        "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    },
    "scripts/zigux/README.md": {
        "check-phase2-toolchain-pin-scope.py --self-test": 2,
        "check-phase2-toolchain-pin-scope.py": 5,
        FALLBACK_MARKER: 1,
    },
    "zigux/tests/README.md": {
        "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
        FALLBACK_MARKER: 1,
    },
    "zigux/Makefile": {
        "check-phase2-toolchain-pin-scope.py --self-test": 1,
        "check-phase2-toolchain-pin-scope.py": 2,
        "phase2-toolchain:": 1,
    },
}


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_missing_markers(text: str, markers: list[str], *, prefix: str) -> list[str]:
    return [f"{prefix}:missing:{marker}" for marker in markers if marker not in text]


def collect_exact_count_issues(text: str, checks: dict[str, int], *, prefix: str) -> list[str]:
    issues: list[str] = []
    for marker, expected_count in checks.items():
        count = count_occurrences(text, marker)
        if count != expected_count:
            issues.append(f"{prefix}:exact_count:{marker}:count={count}:expected={expected_count}")
    return issues


def validate_policy(root: Path) -> list[str]:
    policy = json.loads((root / POLICY_PATH).read_text(encoding="utf-8"))
    issues: list[str] = []

    if policy.get("phase") != "Phase 2":
        issues.append(f"{POLICY_PATH}:phase:{policy.get('phase')}")
    if policy.get("channel") != "0.17.0-dev.87+9b177a7d2":
        issues.append(f"{POLICY_PATH}:channel:{policy.get('channel')}")
    if policy.get("minimum_version") != "0.17.0-dev.87+9b177a7d2":
        issues.append(f"{POLICY_PATH}:minimum_version:{policy.get('minimum_version')}")

    archive_sha = policy.get("archive_sha256", {})
    if archive_sha.get("x86_64-linux") != "a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858":
        issues.append(f"{POLICY_PATH}:archive_sha256:x86_64-linux")

    approval_policy = policy.get("approval_policy", {})
    for key in (
        "shared_phase2_checklist_ack_required",
        "fresh_bootstrap_runner_evidence_required",
        "separate_cross_target_expansion_approval_required",
    ):
        if approval_policy.get(key) is not True:
            issues.append(f"{POLICY_PATH}:approval_policy:{key}")

    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            issues.append(f"missing_file:{rel_path}")
    if issues:
        return issues

    issues.extend(validate_policy(root))

    for rel_path, markers in DOC_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        issues.extend(collect_missing_markers(text, markers, prefix=rel_path))
        issues.extend(collect_exact_count_issues(text, EXACT_COUNTS.get(rel_path, {}), prefix=rel_path))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "")

    write_text(
        root / "Documentation/zigux/README.md",
        "\n".join(
            [
                "scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "phase2-validate",
                "phase2-tools",
                "phase2-kconfig",
                "phase2-cross",
                "phase2",
            ]
        )
        + "\n",
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(
            [
                "scripts/zigux/check-phase2-toolchain-pin-scope.py",
                FALLBACK_MARKER,
                "make -C zigux phase2-tools",
                "make -C zigux phase2-kconfig",
                "make -C zigux phase2-cross",
            ]
        )
        + "\n",
    )
    write_text(
        root / "scripts/zigux/README.md",
        "\n".join(
            [
                "check-phase2-toolchain-pin-scope.py --self-test",
                "check-phase2-toolchain-pin-scope.py",
                "phase2-toolchain",
                FALLBACK_MARKER,
                "check-phase2-toolchain-pin-scope.py --self-test",
                "check-phase2-toolchain-pin-scope.py",
                "check-phase2-toolchain-pin-scope.py",
            ]
        )
        + "\n",
    )
    write_text(
        root / "zigux/tests/README.md",
        "\n".join(
            [
                "scripts/zigux/check-phase2-toolchain-pin-scope.py",
                FALLBACK_MARKER,
                "make -C zigux phase2-validate",
                "make -C zigux phase2",
            ]
        )
        + "\n",
    )
    write_text(
        root / "zigux/Makefile",
        "\n".join(
            [
                "phase2-toolchain:",
                "check-phase2-toolchain-pin-scope.py --self-test",
                "check-phase2-toolchain-pin-scope.py",
                "phase2-validate: phase2-toolchain",
                "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
            ]
        )
        + "\n",
    )
    write_text(
        root / POLICY_PATH,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "policy_note": "Bounded Phase 2 x86_64-linux bootstrap archive-pin contract.",
                "archive_sha256": {
                    "x86_64-linux": "a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858"
                },
                "approval_policy": {
                    "shared_phase2_checklist_ack_required": True,
                    "fresh_bootstrap_runner_evidence_required": True,
                    "separate_cross_target_expansion_approval_required": True,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_pin_scope_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert validate_root(root) == []
        case_count += 1

        build_self_test_root(root)
        path = root / "Documentation/zigux/review-checklist.md"
        path.write_text(path.read_text(encoding="utf-8").replace(FALLBACK_MARKER, "", 1), encoding="utf-8")
        issues = validate_root(root)
        assert f"Documentation/zigux/review-checklist.md:missing:{FALLBACK_MARKER}" in issues
        case_count += 1

        build_self_test_root(root)
        path = root / "zigux/Makefile"
        path.write_text(path.read_text(encoding="utf-8").replace("phase2-toolchain:\n", "", 1), encoding="utf-8")
        issues = validate_root(root)
        assert "zigux/Makefile:missing:phase2-toolchain:" in issues
        case_count += 1

        build_self_test_root(root)
        path = root / POLICY_PATH
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"]["x86_64-linux"] = "broken"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = validate_root(root)
        assert f"{POLICY_PATH}:archive_sha256:x86_64-linux" in issues
        case_count += 1

        build_self_test_root(root)
        (root / POLICY_PATH).unlink()
        issues = validate_root(root)
        assert f"missing_file:{POLICY_PATH}" in issues
        case_count += 1

    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the bounded Phase 2 toolchain-pin reminder surface.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in coverage without a repo checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
        print("PHASE2_TOOLCHAIN_PIN_SCOPE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_TOOLCHAIN_PIN_SCOPE_ISSUES_END")
        return 1

    print("PHASE2_TOOLCHAIN_PIN_SCOPE=pass")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

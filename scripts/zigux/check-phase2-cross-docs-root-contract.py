#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
DIRECT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
MAKEFILE = ROOT / "zigux" / "Makefile"

ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_TARGETS = (
    ("x86_64-linux", "archive_required"),
    ("aarch64-linux", "route_contract_only"),
)

DOCS_ROOT_MARKERS = (
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet",
    "`zigux/tests/fixtures/phase2_cross_targets.json`, the current kconfig bridge manifests, and the current genksyms bridge fixture roster keeping the same packet aligned across docs-root, scripts-root, and tests-root surfaces.",
)

PHASE2_NOTES_MARKERS = (
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
)

DIRECT_CHECKER_MARKERS = (
    'ROUTE = "make -C zigux phase2-cross"',
    'ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")',
)

ALIGNMENT_CHECKER_MARKERS = (
    'SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")',
    'ROUTE = "make -C zigux phase2-cross"',
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

REQUIRED_PATHS = (
    DOCS_ROOT_README,
    PHASE2_NOTES,
    DIRECT_CHECKER,
    ALIGNMENT_CHECKER,
    TOOLCHAIN_POLICY,
    FIXTURE,
    MAKEFILE,
)


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def load_policy_contract(root: Path) -> tuple[list[str], list[str]]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_make_routes, list) or not required_make_routes:
        raise SystemExit(
            f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    normalized_scope: list[str] = []
    normalized_routes: list[str] = []
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized_scope.append(value.strip())
    for value in required_make_routes:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized_routes.append(value.strip())
    return normalized_scope, normalized_routes


def collect_fixture_issues(payload: object, expected_scope: list[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]
    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != expected_scope:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_targets: list[tuple[str, str]] = []
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if not isinstance(validation_mode, str) or not validation_mode.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        actual_targets.append((target.strip(), validation_mode.strip()))

    if actual_targets != list(EXPECTED_TARGETS):
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_targets)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in REQUIRED_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))))
    if issues:
        return issues

    docs_text = read_text(resolve_path(root, DOCS_ROOT_README))
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    direct_checker_text = read_text(resolve_path(root, DIRECT_CHECKER))
    alignment_checker_text = read_text(resolve_path(root, ALIGNMENT_CHECKER))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    issues.extend(collect_missing_markers(docs_text, DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKER"))
    issues.extend(collect_missing_markers(notes_text, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKER"))
    issues.extend(
        collect_missing_markers(
            direct_checker_text, DIRECT_CHECKER_MARKERS, "MISSING_DIRECT_CHECKER_MARKER"
        )
    )
    issues.extend(
        collect_missing_markers(
            alignment_checker_text, ALIGNMENT_CHECKER_MARKERS, "MISSING_ALIGNMENT_CHECKER_MARKER"
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )

    archive_target_scope, required_make_routes = load_policy_contract(root)
    if archive_target_scope != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_POLICY_ARCHIVE_SCOPE", json.dumps(archive_target_scope)))
    if required_make_routes.count("phase2-cross") != 1:
        issues.append(("INVALID_POLICY_REQUIRED_ROUTE", json.dumps(required_make_routes)))

    fixture_payload = read_json(resolve_path(root, FIXTURE))
    issues.extend(collect_fixture_issues(fixture_payload, archive_target_scope))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_DOCS_ROOT_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, DIRECT_CHECKER), "\n".join(DIRECT_CHECKER_MARKERS) + "\n")
    write_text(resolve_path(root, ALIGNMENT_CHECKER), "\n".join(ALIGNMENT_CHECKER_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": [
                    {
                        "target": EXPECTED_TARGETS[0][0],
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": EXPECTED_TARGETS[0][1],
                        "route": ROUTE,
                    },
                    {
                        "target": EXPECTED_TARGETS[1][0],
                        "review_status": "route contract only",
                        "validation_mode": EXPECTED_TARGETS[1][1],
                        "route": ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(DOCS_ROOT_MARKERS)
        + len(PHASE2_NOTES_MARKERS)
        + len(DIRECT_CHECKER_MARKERS)
        + len(ALIGNMENT_CHECKER_MARKERS)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + len(REQUIRED_PATHS)
        + 6
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_docs_root_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in DOCS_ROOT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_ROOT_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_DOCS_ROOT_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_PHASE2_NOTES_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in DIRECT_CHECKER_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DIRECT_CHECKER)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_DIRECT_CHECKER_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in ALIGNMENT_CHECKER_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, ALIGNMENT_CHECKER)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_ALIGNMENT_CHECKER_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        for path in REQUIRED_PATHS:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_POLICY_ARCHIVE_SCOPE", '["aarch64-linux"]') in issues
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in issues
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_REQUIRED_ROUTE", '["phase2-toolchain", "phase2-validate"]') in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["validation_mode"] = "route_contract_only"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2-toolchain"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "cross_targets") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid policy json did not abort")

    assert checks == expected_case_count
    print("PHASE2_CROSS_DOCS_ROOT_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_DOCS_ROOT_CONTRACT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 cross docs-root reminder packet aligned with the current direct cross-route surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a compact current-like sample root for validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print(f"PHASE2_CROSS_DOCS_ROOT_CONTRACT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_DOCS_ROOT_CONTRACT=pass")
    print(
        "PHASE2_CROSS_DOCS_ROOT_CONTRACT_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(PHASE2_NOTES_MARKERS) + len(DIRECT_CHECKER_MARKERS) + len(ALIGNMENT_CHECKER_MARKERS) + len(MAKEFILE_LINES)}"
    )
    print(f"PHASE2_CROSS_DOCS_ROOT_CONTRACT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CROSS_DOCS_ROOT_CONTRACT_TARGET_COUNT={len(EXPECTED_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
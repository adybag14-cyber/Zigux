#!/usr/bin/env python3
"""Guard the Phase 2 cross packet's third_party archive README contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
ARCHIVE_README = ROOT / "third_party" / "README.md"
ARCHIVE_README_CHECKER = ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py"
ARCHIVE_WORKFLOW_CHECKER = ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
MAKEFILE = ROOT / "zigux" / "Makefile"

ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_TARGET_SCOPE = ["x86_64-linux"]
EXPECTED_CROSS_TARGETS = (
    ("x86_64-linux", "archive_required"),
    ("aarch64-linux", "route_contract_only"),
)
EXPECTED_SELF_TEST_CASE_COUNT = 21


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
    except IsADirectoryError as exc:
        raise SystemExit(f"required path is not a file: {path}") from exc


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


def load_policy_contract(root: Path) -> tuple[str, list[str], dict[str, str], list[str]]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise SystemExit(f"invalid channel in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    channel = channel.strip()

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    normalized_sha256: dict[str, str] = {}
    for key, value in archive_sha256.items():
        if not isinstance(key, str) or not key.strip():
            raise SystemExit(
                f"invalid archive_sha256 target in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_sha256 value in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized_sha256[key.strip()] = value.strip()

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    normalized_scope: list[str] = []
    seen_scope: set[str] = set()
    for entry in archive_target_scope:
        if not isinstance(entry, str) or not entry.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        target = entry.strip()
        if target in seen_scope:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized_scope.append(target)
        seen_scope.add(target)

    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_make_routes, list) or not required_make_routes:
        raise SystemExit(
            f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    normalized_routes: list[str] = []
    seen_routes: set[str] = set()
    for entry in required_make_routes:
        if not isinstance(entry, str) or not entry.strip():
            raise SystemExit(
                f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        route = entry.strip()
        if route in seen_routes:
            raise SystemExit(
                f"duplicate required_make_routes entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized_routes.append(route)
        seen_routes.add(route)

    return channel, normalized_scope, normalized_sha256, normalized_routes


def required_archive_markers(channel: str, archive_sha256: dict[str, str]) -> tuple[str, ...]:
    target = EXPECTED_ARCHIVE_TARGET_SCOPE[0]
    archive_path = f"third_party/zig-{target}-{channel}.tar.xz"
    validation_command = (
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
        f"{archive_path} --archive-target {target}"
    )
    return (
        f"- target: `{target}`",
        f"- channel: `{channel}`",
        f"- file: `{archive_path}`",
        f"- sha256: `{archive_sha256[target]}`",
        f"- `{validation_command}`",
        "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and "
        "`scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
    )


DOCS_ROOT_MARKERS = (
    "* `third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract, the `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay, the local-first `third_party`, mirror, then direct-download bootstrap order, and the two shipped Lane 05 reminder guards explicit from the docs root beside the returned toolchain packet.",
    "* `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "* `python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

PHASE2_NOTES_MARKERS = (
    "- `third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
    "- `zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through should treat the returned cross packet as present evidence instead of a repo-reality gap.",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)


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
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target.strip()))
        actual_targets.append((target.strip(), validation_mode.strip()))

    if actual_targets != list(EXPECTED_CROSS_TARGETS):
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_targets)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    required_paths = (
        DOCS_ROOT_README,
        PHASE2_NOTES,
        ARCHIVE_README,
        ARCHIVE_README_CHECKER,
        ARCHIVE_WORKFLOW_CHECKER,
        TOOLCHAIN_POLICY,
        FIXTURE,
        MAKEFILE,
    )
    for path in required_paths:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_PATH", str(path.relative_to(ROOT))))
    if issues:
        return issues

    channel, archive_target_scope, archive_sha256, required_make_routes = load_policy_contract(root)

    docs_root_text = read_text(resolve_path(root, DOCS_ROOT_README))
    for marker in DOCS_ROOT_MARKERS:
        if marker not in docs_root_text:
            issues.append(("MISSING_DOCS_ROOT_MARKER", marker))

    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    for marker in PHASE2_NOTES_MARKERS:
        if marker not in notes_text:
            issues.append(("MISSING_PHASE2_NOTES_MARKER", marker))

    archive_readme_text = read_text(resolve_path(root, ARCHIVE_README))
    for marker in required_archive_markers(channel, archive_sha256):
        if marker not in archive_readme_text:
            issues.append(("MISSING_ARCHIVE_README_MARKER", marker))

    if archive_target_scope != EXPECTED_ARCHIVE_TARGET_SCOPE:
        issues.append(("INVALID_POLICY_ARCHIVE_SCOPE", json.dumps(archive_target_scope)))
    if required_make_routes.count("phase2-cross") != 1:
        issues.append(("INVALID_POLICY_REQUIRED_ROUTE", json.dumps(required_make_routes)))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    fixture_payload = read_json(resolve_path(root, FIXTURE))
    issues.extend(collect_fixture_issues(fixture_payload, archive_target_scope))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_ARCHIVE_README_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_current_like_root(root: Path) -> None:
    policy_payload = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {
            "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        },
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": EXPECTED_ARCHIVE_TARGET_SCOPE,
            "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
        },
    }
    channel = str(policy_payload["channel"])
    archive_sha256 = dict(policy_payload["archive_sha256"])

    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(
        resolve_path(root, ARCHIVE_README),
        "# Zigux third-party archives\n\n" + "\n".join(required_archive_markers(channel, archive_sha256)) + "\n",
    )
    write_text(
        resolve_path(root, ARCHIVE_README_CHECKER),
        "# present\n",
    )
    write_text(
        resolve_path(root, ARCHIVE_WORKFLOW_CHECKER),
        "# present\n",
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(policy_payload, indent=2) + "\n",
    )
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_TARGET_SCOPE,
                "cross_targets": [
                    {
                        "target": EXPECTED_CROSS_TARGETS[0][0],
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": EXPECTED_CROSS_TARGETS[0][1],
                        "route": ROUTE,
                    },
                    {
                        "target": EXPECTED_CROSS_TARGETS[1][0],
                        "review_status": "route contract only",
                        "validation_mode": EXPECTED_CROSS_TARGETS[1][1],
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
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_archive_readme_") as tmp_dir:
        root = Path(tmp_dir)

        build_current_like_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, ARCHIVE_README)
        marker = required_archive_markers("0.17.0-dev.87+9b177a7d2", {"x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"})[0]
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
        assert ("MISSING_ARCHIVE_README_MARKER", marker) in collect_issues(root)
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, DOCS_ROOT_README)
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), DOCS_ROOT_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_DOCS_ROOT_MARKER", DOCS_ROOT_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, PHASE2_NOTES)
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), PHASE2_NOTES_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_PHASE2_NOTES_MARKER", PHASE2_NOTES_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_POLICY_ARCHIVE_SCOPE", '["aarch64-linux"]') in issues
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in issues
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_REQUIRED_ROUTE", '["phase2-toolchain", "phase2-validate"]') in collect_issues(root)
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["validation_mode"] = "route_contract_only"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2-toolchain"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "cross_targets") in collect_issues(root)
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[0]), encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_current_like_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[1], "# removed"), encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[1]) in collect_issues(root)
        checks += 1

        for required_path in (
            ARCHIVE_README,
            ARCHIVE_README_CHECKER,
            ARCHIVE_WORKFLOW_CHECKER,
            DOCS_ROOT_README,
            PHASE2_NOTES,
            TOOLCHAIN_POLICY,
            FIXTURE,
            MAKEFILE,
        ):
            build_current_like_root(root)
            resolve_path(root, required_path).unlink()
            assert ("MISSING_REQUIRED_PATH", str(required_path.relative_to(ROOT))) in collect_issues(root)
            checks += 1

        build_current_like_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid policy json did not abort")

        build_current_like_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "x86_64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate archive_target_scope entry" in str(exc)
            checks += 1
        else:
            raise AssertionError("duplicate archive target scope did not abort")

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_ARCHIVE_README_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ARCHIVE_README_CONTRACT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def write_sample_root(root: Path) -> int:
    build_current_like_root(root.resolve())
    print(f"PHASE2_CROSS_ARCHIVE_README_CONTRACT_SAMPLE_ROOT={root.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 cross archive README stays aligned with the live direct cross packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a compact current-like root for validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_ARCHIVE_README_CONTRACT=pass")
    print(f"PHASE2_CROSS_ARCHIVE_README_CONTRACT_MARKER_COUNT={len(DOCS_ROOT_MARKERS) + len(PHASE2_NOTES_MARKERS) + len(required_archive_markers('0.17.0-dev.87+9b177a7d2', {'x86_64-linux': '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77'}))}")
    print("PHASE2_CROSS_ARCHIVE_README_CONTRACT_REQUIRED_PATH_COUNT=8")
    print(f"PHASE2_CROSS_ARCHIVE_README_CONTRACT_TARGET_COUNT={len(EXPECTED_CROSS_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

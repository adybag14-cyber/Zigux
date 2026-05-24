#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"

SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-validate",
    "phase2-cross",
)
EXPECTED_REVIEW_STATUS_BY_TARGET = {
    "x86_64-linux": "pinned bootstrap archive",
    "aarch64-linux": "route contract only",
}

REQUIRED_VALIDATE_MARKERS = (
    '    "scripts/zigux/check-phase2-cross.py",',
    '    "scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '    "zigux/tests/fixtures/phase2_cross_targets.json",',
    '    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '    "run: make -C zigux phase2-cross",',
    '    "run: make -C zigux phase2-validate",',
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

REQUIRED_PATHS = (
    VALIDATE,
    WORKFLOW,
    MAKEFILE,
    POLICY,
    FIXTURE,
    CROSS_CHECKER,
    ALIGNMENT_CHECKER,
)


class DuplicateJsonKeyError(ValueError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    except DuplicateJsonKeyError as exc:
        raise SystemExit(f"duplicate json key in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def load_expected_policy_contract(root: Path) -> dict[str, object]:
    policy_path = resolve_path(root, POLICY)
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")

    normalized_scope: list[str] = []
    seen_scope: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value or value != value.strip():
            raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")
        if value in seen_scope:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {policy_path}")
        if value not in SUPPORTED_CROSS_TARGETS:
            raise SystemExit(f"unsupported archive_target_scope target in required file: {policy_path}: {value}")
        normalized_scope.append(value)
        seen_scope.add(value)

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in required file: {policy_path}")

    archive_sha256_targets: list[str] = []
    seen_hash_targets: set[str] = set()
    for key, value in archive_sha256.items():
        if not isinstance(key, str) or not key or key != key.strip():
            raise SystemExit(f"invalid archive_sha256 key in required file: {policy_path}")
        if not isinstance(value, str) or not value or value != value.strip():
            raise SystemExit(f"invalid archive_sha256 value in required file: {policy_path}: {key}")
        if key in seen_hash_targets:
            raise SystemExit(f"duplicate archive_sha256 key in required file: {policy_path}: {key}")
        archive_sha256_targets.append(key)
        seen_hash_targets.add(key)

    if archive_sha256_targets != normalized_scope:
        raise SystemExit(f"archive_sha256 target drift in required file: {policy_path}")

    return {
        "archive_target_scope": normalized_scope,
        "expected_modes": {
            target: ("archive_required" if target in seen_scope else "route_contract_only")
            for target in SUPPORTED_CROSS_TARGETS
        },
    }


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    expected_policy = load_expected_policy_contract(root)
    fixture_path = resolve_path(root, FIXTURE)
    fixture = read_json(fixture_path)

    if not isinstance(fixture, dict):
        return [("INVALID_FIXTURE_SHAPE", type(fixture).__name__)]

    if fixture.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != expected_policy["archive_target_scope"]:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_modes: dict[str, str] = {}
    target_order: list[str] = []
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        route = entry.get("route")
        review_status = entry.get("review_status")
        if not isinstance(target, str) or not target or target != target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        if target not in SUPPORTED_CROSS_TARGETS:
            issues.append(("UNSUPPORTED_CROSS_TARGET", target))
        if not isinstance(mode, str) or not mode or mode != mode.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if review_status != EXPECTED_REVIEW_STATUS_BY_TARGET.get(target):
            issues.append(("INVALID_CROSS_TARGET_REVIEW_STATUS", f"{target}:{review_status}"))
        actual_modes[target] = mode
        target_order.append(target)

    if target_order != list(SUPPORTED_CROSS_TARGETS):
        issues.append(("INVALID_CROSS_TARGET_ORDER", ",".join(target_order)))
    if actual_modes != expected_policy["expected_modes"]:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    validate_text = read_text(resolve_path(root, VALIDATE))
    issues.extend(
        collect_missing_markers(
            validate_text,
            REQUIRED_VALIDATE_MARKERS,
            "MISSING_VALIDATE_MARKER",
        )
    )

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            REQUIRED_WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            REQUIRED_MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )

    issues.extend(collect_fixture_issues(root))
    return issues


def run_contract(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_VALIDATE_CONTRACT_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_VALIDATE_CONTRACT_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_VALIDATE_CONTRACT=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_VALIDATE_MARKER_COUNT={len(REQUIRED_VALIDATE_MARKERS)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_text(
            resolve_path(root, VALIDATE),
            "\n".join(
                [
                    "PHASE2_FILES = [",
                    *REQUIRED_VALIDATE_MARKERS,
                    "]",
                    "",
                ]
            ),
        )
        write_text(
            resolve_path(root, WORKFLOW),
            "\n".join(
                [
                    "name: zigux-bootstrap",
                    "jobs:",
                    "  phase2:",
                    *[f"    - {line}" for line in REQUIRED_WORKFLOW_LINES],
                    "",
                ]
            ),
        )
        write_text(
            resolve_path(root, MAKEFILE),
            "\n".join(
                [
                    "phase2-toolchain:",
                    "\t@true",
                    "phase2-tools:",
                    "\t@true",
                    "phase2-kconfig:",
                    "\t@true",
                    *REQUIRED_MAKEFILE_LINES,
                    "\t@true",
                    "phase2-genksyms:",
                    "\t@true",
                    "phase2-fixdep:",
                    "\t@true",
                    "",
                ]
            ),
        )
        write_text(
            resolve_path(root, POLICY),
            json.dumps(
                {
                    "archive_sha256": {
                        "x86_64-linux": "sha256-x86_64-linux",
                        "aarch64-linux": "sha256-aarch64-linux",
                    },
                    "upgrade_policy": {
                        "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                        "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
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
                    "route": EXPECTED_ROUTE,
                    "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                    "cross_targets": [
                        {
                            "target": "x86_64-linux",
                            "validation_mode": "archive_required",
                            "route": EXPECTED_ROUTE,
                            "review_status": "pinned bootstrap archive",
                        },
                        {
                            "target": "aarch64-linux",
                            "validation_mode": "route_contract_only",
                            "route": EXPECTED_ROUTE,
                            "review_status": "route contract only",
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
        )
        write_text(resolve_path(root, CROSS_CHECKER), "#!/usr/bin/env python3\n")
        write_text(resolve_path(root, ALIGNMENT_CHECKER), "#!/usr/bin/env python3\n")

        passing_code = run_contract(root)
        if passing_code != 0:
            print("PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST_FAIL=expected-pass")
            return 1

        cases = [
            (
                "missing_validate_marker",
                lambda: write_text(resolve_path(root, VALIDATE), "PHASE2_FILES = []\n"),
                "MISSING_VALIDATE_MARKER",
            ),
            (
                "missing_workflow_line",
                lambda: write_text(resolve_path(root, WORKFLOW), "name: zigux-bootstrap\n"),
                "MISSING_WORKFLOW_LINE",
            ),
            (
                "duplicate_workflow_line",
                lambda: write_text(
                    resolve_path(root, WORKFLOW),
                    "\n".join(
                        [
                            "name: zigux-bootstrap",
                            *[f"run: {line.split('run: ', 1)[1]}" for line in REQUIRED_WORKFLOW_LINES],
                            REQUIRED_WORKFLOW_LINES[0],
                            "",
                        ]
                    ),
                ),
                "DUPLICATE_WORKFLOW_LINE",
            ),
            (
                "missing_makefile_line",
                lambda: write_text(resolve_path(root, MAKEFILE), "phase2-toolchain:\n\t@true\n"),
                "MISSING_MAKEFILE_LINE",
            ),
            (
                "duplicate_makefile_line",
                lambda: write_text(
                    resolve_path(root, MAKEFILE),
                    "\n".join([*REQUIRED_MAKEFILE_LINES, REQUIRED_MAKEFILE_LINES[0], ""]),
                ),
                "DUPLICATE_MAKEFILE_LINE",
            ),
            (
                "missing_required_path",
                lambda: resolve_path(root, CROSS_CHECKER).unlink(),
                "MISSING_REQUIRED_PATH",
            ),
            (
                "invalid_fixture_phase",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase X",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_FIXTURE_FIELD",
            ),
            (
                "invalid_fixture_status",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "draft",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_FIXTURE_FIELD",
            ),
            (
                "invalid_fixture_route",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": "make -C zigux phase2-validate",
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_FIXTURE_FIELD",
            ),
            (
                "invalid_archive_scope",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": ["x86_64-linux"],
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_FIXTURE_FIELD",
            ),
            (
                "invalid_cross_targets_shape",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": {},
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_FIXTURE_FIELD",
            ),
            (
                "duplicate_cross_target",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "DUPLICATE_CROSS_TARGET_ENTRY",
            ),
            (
                "unsupported_cross_target",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "armv7-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "UNSUPPORTED_CROSS_TARGET",
            ),
            (
                "invalid_cross_target_route",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": "make -C zigux phase2-validate",
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_ROUTE",
            ),
            (
                "invalid_cross_target_order",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_ORDER",
            ),
            (
                "invalid_cross_target_matrix",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_MATRIX",
            ),
            (
                "invalid_cross_target_review_status",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_REVIEW_STATUS",
            ),
            (
                "duplicate_policy_key",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    '{"archive_sha256": {"x86_64-linux": "one", "x86_64-linux": "two"}, "upgrade_policy": {"archive_target_scope": ["x86_64-linux", "aarch64-linux"], "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"]}}\n',
                ),
                "duplicate json key",
            ),
            (
                "duplicate_fixture_key",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    '{"phase": "Phase 2", "phase": "Phase 2", "status": "active", "route": "make -C zigux phase2-cross", "archive_target_scope": ["x86_64-linux", "aarch64-linux"], "cross_targets": []}\n',
                ),
                "duplicate json key",
            ),
            (
                "invalid_policy_shape",
                lambda: write_text(resolve_path(root, POLICY), "[]\n"),
                "invalid json shape",
            ),
            (
                "invalid_upgrade_policy_shape",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "x86_64-linux": "sha256-x86_64-linux",
                                "aarch64-linux": "sha256-aarch64-linux",
                            },
                            "upgrade_policy": [],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "invalid upgrade_policy",
            ),
            (
                "invalid_archive_scope_shape",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "x86_64-linux": "sha256-x86_64-linux",
                                "aarch64-linux": "sha256-aarch64-linux",
                            },
                            "upgrade_policy": {
                                "archive_target_scope": [],
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "invalid archive_target_scope",
            ),
            (
                "invalid_archive_scope_member",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "x86_64-linux": "sha256-x86_64-linux",
                                "aarch64-linux": "sha256-aarch64-linux",
                            },
                            "upgrade_policy": {
                                "archive_target_scope": ["x86_64-linux", " arm64-linux"],
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "invalid archive_target_scope",
            ),
            (
                "duplicate_archive_scope_member",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "x86_64-linux": "sha256-x86_64-linux",
                                "aarch64-linux": "sha256-aarch64-linux",
                            },
                            "upgrade_policy": {
                                "archive_target_scope": ["x86_64-linux", "x86_64-linux"],
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "duplicate archive_target_scope entry",
            ),
            (
                "unsupported_archive_scope_target",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "x86_64-linux": "sha256-x86_64-linux",
                                "aarch64-linux": "sha256-aarch64-linux",
                            },
                            "upgrade_policy": {
                                "archive_target_scope": ["x86_64-linux", "armv7-linux"],
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "unsupported archive_target_scope target",
            ),
            (
                "invalid_required_make_routes",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "x86_64-linux": "sha256-x86_64-linux",
                                "aarch64-linux": "sha256-aarch64-linux",
                            },
                            "upgrade_policy": {
                                "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                                "required_make_routes": ["phase2-toolchain", "phase2-cross"],
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "invalid required_make_routes",
            ),
            (
                "invalid_archive_sha_shape",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": [],
                            "upgrade_policy": {
                                "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "invalid archive_sha256",
            ),
            (
                "invalid_archive_sha_key",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    '{"archive_sha256": {"x86_64-linux": "one", " x86_64-linux": "two"}, "upgrade_policy": {"archive_target_scope": ["x86_64-linux", "aarch64-linux"], "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"]}}\n',
                ),
                "invalid archive_sha256 key",
            ),
            (
                "invalid_archive_sha_value",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "x86_64-linux": "sha256-x86_64-linux",
                                "aarch64-linux": "",
                            },
                            "upgrade_policy": {
                                "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "invalid archive_sha256 value",
            ),
            (
                "archive_sha_target_drift",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {
                                "aarch64-linux": "sha256-aarch64-linux",
                                "x86_64-linux": "sha256-x86_64-linux",
                            },
                            "upgrade_policy": {
                                "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "archive_sha256 target drift",
            ),
            (
                "invalid_json_policy",
                lambda: write_text(resolve_path(root, POLICY), "{\n"),
                "invalid json",
            ),
            (
                "invalid_json_fixture",
                lambda: write_text(resolve_path(root, FIXTURE), "{\n"),
                "invalid json",
            ),
            (
                "non_dict_cross_target_entry",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": ["x86_64-linux"],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_ENTRY",
            ),
            (
                "invalid_cross_target_name",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": " x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                }
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_ENTRY",
            ),
            (
                "invalid_cross_target_mode",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_ENTRY",
            ),
            (
                "review_status_missing_for_arm64",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": list(SUPPORTED_CROSS_TARGETS),
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": None,
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_REVIEW_STATUS",
            ),
            (
                "missing_alignment_checker",
                lambda: resolve_path(root, ALIGNMENT_CHECKER).unlink(),
                "MISSING_REQUIRED_PATH",
            ),
            (
                "workflow_duplicate_with_trimmed_whitespace",
                lambda: write_text(
                    resolve_path(root, WORKFLOW),
                    "\n".join(
                        [
                            *REQUIRED_WORKFLOW_LINES,
                            f"  {REQUIRED_WORKFLOW_LINES[0]}  ",
                            "",
                        ]
                    ),
                ),
                "DUPLICATE_WORKFLOW_LINE",
            ),
            (
                "makefile_duplicate_with_spacing",
                lambda: write_text(
                    resolve_path(root, MAKEFILE),
                    "\n".join(
                        [
                            *REQUIRED_MAKEFILE_LINES,
                            f"  {REQUIRED_MAKEFILE_LINES[1]}  ",
                            "",
                        ]
                    ),
                ),
                "DUPLICATE_MAKEFILE_LINE",
            ),
        ]

        passing_validate = read_text(resolve_path(root, VALIDATE))
        passing_workflow = read_text(resolve_path(root, WORKFLOW))
        passing_makefile = read_text(resolve_path(root, MAKEFILE))
        passing_policy = read_text(resolve_path(root, POLICY))
        passing_fixture = read_text(resolve_path(root, FIXTURE))
        passing_cross_checker = read_text(resolve_path(root, CROSS_CHECKER))
        passing_alignment_checker = read_text(resolve_path(root, ALIGNMENT_CHECKER))

        case_count = 0
        for name, mutate, expected_fragment in cases:
            write_text(resolve_path(root, VALIDATE), passing_validate)
            write_text(resolve_path(root, WORKFLOW), passing_workflow)
            write_text(resolve_path(root, MAKEFILE), passing_makefile)
            write_text(resolve_path(root, POLICY), passing_policy)
            write_text(resolve_path(root, FIXTURE), passing_fixture)
            write_text(resolve_path(root, CROSS_CHECKER), passing_cross_checker)
            write_text(resolve_path(root, ALIGNMENT_CHECKER), passing_alignment_checker)

            mutate()
            try:
                code = run_contract(root)
                if code == 0:
                    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST_FAIL={name}:expected-failure")
                    return 1
            except SystemExit as exc:
                message = str(exc)
                if expected_fragment not in message:
                    print(
                        "PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST_FAIL="
                        f"{name}:expected={expected_fragment}:actual={message}"
                    )
                    return 1
            else:
                case_count += 1
                continue
            case_count += 1

    print("PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 cross packet contract wired through validate-phase2 and the bootstrap workflow."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to validate (defaults to the current checkout)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the hermetic self-test suite instead of validating the repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    return run_contract(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the shared Phase 2 validator packet from the outside."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase2.py")


def load_validator(root: Path):
    path = root / VALIDATOR_REL
    spec = importlib.util.spec_from_file_location("zigux_validate_phase2", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to load phase2 validator: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as exc:
        raise SystemExit(f"unable to load phase2 validator: {path}") from exc
    return module


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


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def assert_issue(module, root: Path, expected: tuple[str, str]) -> None:
    issues = module.collect_issues(root)
    if expected not in issues:
        raise AssertionError(f"missing expected issue {expected!r}; saw {issues!r}")


def assert_abort(module, root: Path, expected_fragment: str) -> None:
    try:
        module.collect_issues(root)
    except SystemExit as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"missing abort fragment {expected_fragment!r}: {exc}") from exc
    else:
        raise AssertionError(f"expected abort containing {expected_fragment!r}")


def seed_root(module, root: Path, required_make_routes: tuple[str, ...] | None = None) -> None:
    if required_make_routes is None:
        module.build_self_test_root(root)
    else:
        module.build_self_test_root(root, required_make_routes=required_make_routes)


def run_matrix(module) -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validator_packet_") as tmp_dir:
        root = Path(tmp_dir)

        seed_root(module, root)
        assert module.collect_issues(root) == []
        checks_run += 1

        required_make_routes = module.load_required_make_routes(root)
        workflow_route_lines = module.expected_workflow_route_lines(required_make_routes)
        dynamic_makefile_lines = module.expected_makefile_dynamic_lines(required_make_routes)
        phony_line = module.required_phase2_phony_line(required_make_routes)
        protected_rel_paths = {
            Path(module.MAKEFILE),
            Path(module.TOOLCHAIN_POLICY),
            Path(module.KCONFIG_BRIDGE_VALIDATOR_PATH),
        }

        for marker in (*module.STATIC_REQUIRED_WORKFLOW_LINES, *workflow_route_lines):
            seed_root(module, root)
            workflow_path = root / module.WORKFLOW
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_WORKFLOW_LINE", marker))
            checks_run += 1

            seed_root(module, root)
            workflow_path = root / module.WORKFLOW
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert_issue(module, root, ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2"))
            checks_run += 1

        for marker in module.DISALLOWED_WORKFLOW_LINES:
            seed_root(module, root)
            workflow_path = root / module.WORKFLOW
            workflow_path.write_text(workflow_path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert_issue(module, root, ("UNEXPECTED_WORKFLOW_LINE", f"{marker}:count=1"))
            checks_run += 1

        seed_root(module, root)
        makefile_path = root / module.MAKEFILE
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), phony_line, "# removed"),
            encoding="utf-8",
        )
        assert_issue(module, root, ("MISSING_MAKEFILE_LINE", phony_line))
        checks_run += 1

        for marker in (*module.STATIC_REQUIRED_MAKEFILE_LINES, *dynamic_makefile_lines):
            seed_root(module, root)
            makefile_path = root / module.MAKEFILE
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_MAKEFILE_LINE", marker))
            checks_run += 1

            seed_root(module, root)
            makefile_path = root / module.MAKEFILE
            makefile_path.write_text(
                duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert_issue(module, root, ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2"))
            checks_run += 1

        for rel in module.REQUIRED_PATHS:
            rel_path = Path(rel)
            if rel_path in protected_rel_paths:
                continue
            seed_root(module, root)
            (root / rel_path).unlink()
            assert_issue(module, root, ("MISSING_REQUIRED_PATH", rel_path.as_posix()))
            checks_run += 1

        for marker in module.KCONFIG_CONFDATA_REPLAY_MARKERS:
            seed_root(module, root)
            validator_path = root / module.KCONFIG_BRIDGE_VALIDATOR_PATH
            validator_path.write_text(
                replace_exact_line(validator_path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_KCONFIG_CONFDATA_REPLAY_MARKER", marker))
            checks_run += 1

            seed_root(module, root)
            validator_path = root / module.KCONFIG_BRIDGE_VALIDATOR_PATH
            validator_path.write_text(
                duplicate_exact_line(validator_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert_issue(module, root, ("DUPLICATE_KCONFIG_CONFDATA_REPLAY_MARKER", f"{marker}:count=2"))
            checks_run += 1

        for rel in (
            Path(module.WORKFLOW),
            Path(module.MAKEFILE),
            Path(module.KCONFIG_BRIDGE_VALIDATOR_PATH),
            Path(module.TOOLCHAIN_POLICY),
        ):
            seed_root(module, root)
            (root / rel).unlink()
            assert_abort(module, root, str(root / rel))
            checks_run += 1

        seed_root(module, root)
        archive_payload = root / module.ARCHIVE_PAYLOAD_PATH
        archive_parts_manifest = root / module.ARCHIVE_PARTS_MANIFEST_PATH
        archive_payload.unlink()
        archive_parts_manifest.parent.mkdir(parents=True, exist_ok=True)
        archive_parts_manifest.write_text('{"parts": []}\n', encoding="utf-8")
        assert module.collect_issues(root) == []
        checks_run += 1

        seed_root(module, root)
        (root / module.ARCHIVE_PAYLOAD_PATH).unlink()
        assert_issue(
            module,
            root,
            ("MISSING_REQUIRED_ARCHIVE_SUPPORT", " or ".join(module.ARCHIVE_SUPPORT_ALTERNATIVES)),
        )
        checks_run += 1

        seed_root(module, root)
        policy_path = root / module.TOOLCHAIN_POLICY
        policy_path.write_text("{broken\n", encoding="utf-8")
        assert_abort(module, root, "invalid json in required file")
        checks_run += 1

        seed_root(module, root)
        policy_path = root / module.TOOLCHAIN_POLICY
        write_json(policy_path, {"phase": "Phase 2"})
        assert_abort(module, root, "invalid upgrade_policy")
        checks_run += 1

        seed_root(module, root)
        policy_path = root / module.TOOLCHAIN_POLICY
        write_json(policy_path, {"phase": "Phase 2", "upgrade_policy": {"required_make_routes": []}})
        assert_abort(module, root, "invalid required_make_routes")
        checks_run += 1

        seed_root(module, root)
        policy_path = root / module.TOOLCHAIN_POLICY
        duplicated_routes = (*required_make_routes[:-1], required_make_routes[-1], required_make_routes[-1])
        payload = read_json(policy_path)
        assert isinstance(payload, dict)
        payload["upgrade_policy"]["required_make_routes"] = list(duplicated_routes)
        write_json(policy_path, payload)
        assert_abort(module, root, "duplicate required_make_routes entry")
        checks_run += 1

        seed_root(module, root)
        policy_path = root / module.TOOLCHAIN_POLICY
        payload = read_json(policy_path)
        assert isinstance(payload, dict)
        payload["upgrade_policy"]["required_make_routes"] = [required_make_routes[0], "  "]
        write_json(policy_path, payload)
        assert_abort(module, root, "invalid required_make_routes entry")
        checks_run += 1

        seed_root(module, root)
        policy_path = root / module.TOOLCHAIN_POLICY
        payload = read_json(policy_path)
        assert isinstance(payload, dict)
        future_routes = (*required_make_routes, "phase2-future")
        payload["upgrade_policy"]["required_make_routes"] = list(future_routes)
        write_json(policy_path, payload)
        expected_future_makefile_line = module.expected_makefile_dynamic_lines(future_routes)[0]
        issues = module.collect_issues(root)
        if ("MISSING_WORKFLOW_LINE", "run: make -C zigux phase2-future") not in issues:
            raise AssertionError(f"missing dynamic workflow drift issue: {issues!r}")
        if ("MISSING_MAKEFILE_LINE", expected_future_makefile_line) not in issues:
            raise AssertionError(f"missing dynamic makefile drift issue: {issues!r}")
        if ("MISSING_MAKEFILE_LINE", module.required_phase2_phony_line(future_routes)) not in issues:
            raise AssertionError(f"missing dynamic phony drift issue: {issues!r}")
        checks_run += 1

    return checks_run


def run_self_test() -> int:
    fake_validator = """\
from pathlib import Path
import json
import shutil

WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
TOOLCHAIN_POLICY = "scripts/zigux/zig-toolchain-policy.json"
KCONFIG_BRIDGE_VALIDATOR_PATH = "scripts/zigux/check-kconfig-bridge.py"
ARCHIVE_PAYLOAD_PATH = "third_party/pinned.tar.xz"
ARCHIVE_PARTS_MANIFEST_PATH = "third_party/pinned.tar.xz.parts/manifest.json"
ARCHIVE_SUPPORT_ALTERNATIVES = (
    ARCHIVE_PAYLOAD_PATH,
    ARCHIVE_PARTS_MANIFEST_PATH,
)
STATIC_REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
)
DISALLOWED_WORKFLOW_LINES = ()
STATIC_REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
)
KCONFIG_CONFDATA_REPLAY_MARKERS = (
    "repeatable-json-marker",
)
DEFAULT_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-validate",
)
REQUIRED_PATHS = (
    "Documentation/zigux/phase2-closure.md",
    "zigux/Makefile",
    "scripts/zigux/check-kconfig-bridge.py",
)

def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc

def read_json_dict(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload

def load_required_make_routes(root: Path) -> tuple[str, ...]:
    payload = read_json_dict(root / TOOLCHAIN_POLICY)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / TOOLCHAIN_POLICY}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {root / TOOLCHAIN_POLICY}")
    normalized = []
    seen = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"invalid required_make_routes entry in required file: {root / TOOLCHAIN_POLICY}")
        route = route.strip()
        if route in seen:
            raise SystemExit(f"duplicate required_make_routes entry in required file: {root / TOOLCHAIN_POLICY}: {route}")
        normalized.append(route)
        seen.add(route)
    return tuple(normalized)

def expected_workflow_route_lines(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"run: make -C zigux {route}" for route in (*required_make_routes, "phase2"))

def expected_makefile_dynamic_lines(required_make_routes: tuple[str, ...]) -> tuple[str, ...]:
    return (
        f"phase2-validate: {' '.join(required_make_routes)}",
        "phase2: phase2-validate",
    )

def required_phase2_phony_line(required_make_routes: tuple[str, ...]) -> str:
    return ".PHONY: " + " ".join((*required_make_routes, "phase2"))

def phony_targets_present(text: str) -> set[str]:
    targets = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets

def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)

def build_self_test_root(root: Path, required_make_routes: tuple[str, ...] = DEFAULT_REQUIRED_MAKE_ROUTES) -> None:
    for child in root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    (root / Path(WORKFLOW).parent).mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW).write_text(
        "\\n".join(("name: bootstrap", *STATIC_REQUIRED_WORKFLOW_LINES, *expected_workflow_route_lines(required_make_routes))) + "\\n",
        encoding="utf-8",
    )
    (root / Path(MAKEFILE).parent).mkdir(parents=True, exist_ok=True)
    (root / MAKEFILE).write_text(
        "\\n".join(
            (
                required_phase2_phony_line(required_make_routes),
                *STATIC_REQUIRED_MAKEFILE_LINES,
                *expected_makefile_dynamic_lines(required_make_routes),
            )
        ) + "\\n",
        encoding="utf-8",
    )
    for rel in REQUIRED_PATHS:
        if rel == MAKEFILE or rel == TOOLCHAIN_POLICY:
            continue
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("present\\n", encoding="utf-8")
    (root / TOOLCHAIN_POLICY).parent.mkdir(parents=True, exist_ok=True)
    (root / TOOLCHAIN_POLICY).write_text(
        json.dumps(
            {
                "phase": "Phase 2",
                "upgrade_policy": {"required_make_routes": list(required_make_routes)},
            },
            indent=2,
        ) + "\\n",
        encoding="utf-8",
    )
    (root / KCONFIG_BRIDGE_VALIDATOR_PATH).write_text(KCONFIG_CONFDATA_REPLAY_MARKERS[0] + "\\n", encoding="utf-8")
    (root / ARCHIVE_PAYLOAD_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / ARCHIVE_PAYLOAD_PATH).write_text("archive\\n", encoding="utf-8")

def collect_archive_support_issues(root: Path):
    if any((root / rel).exists() for rel in ARCHIVE_SUPPORT_ALTERNATIVES):
        return []
    return [("MISSING_REQUIRED_ARCHIVE_SUPPORT", " or ".join(ARCHIVE_SUPPORT_ALTERNATIVES))]

def collect_issues(root: Path):
    issues = []
    required_make_routes = load_required_make_routes(root)
    workflow_route_lines = expected_workflow_route_lines(required_make_routes)
    dynamic_makefile_lines = expected_makefile_dynamic_lines(required_make_routes)
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)
    for marker in (*STATIC_REQUIRED_WORKFLOW_LINES, *workflow_route_lines):
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
    if not set((*required_make_routes, "phase2")).issubset(phony_targets_present(makefile_text)):
        issues.append(("MISSING_MAKEFILE_LINE", required_phase2_phony_line(required_make_routes)))
    for marker in (*STATIC_REQUIRED_MAKEFILE_LINES, *dynamic_makefile_lines):
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    bridge_text = read_text(root, KCONFIG_BRIDGE_VALIDATOR_PATH)
    for marker in KCONFIG_CONFDATA_REPLAY_MARKERS:
        count = count_exact_lines(bridge_text, marker)
        if count == 0:
            issues.append(("MISSING_KCONFIG_CONFDATA_REPLAY_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_KCONFIG_CONFDATA_REPLAY_MARKER", f"{marker}:count={count}"))
    issues.extend(collect_archive_support_issues(root))
    return issues
"""

    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validator_packet_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        validator_path = root / VALIDATOR_REL
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        validator_path.write_text(fake_validator, encoding="utf-8")
        module = load_validator(root)
        checks_run += run_matrix(module)

        missing_validator_root = root / "missing-validator-root"
        missing_validator_root.mkdir()
        try:
            load_validator(missing_validator_root)
        except SystemExit as exc:
            if "unable to load phase2 validator" not in str(exc):
                raise AssertionError(f"unexpected missing-validator abort: {exc}") from exc
            checks_run += 1
        else:
            raise AssertionError("missing validator root did not abort")

    print("PHASE2_VALIDATOR_ENTRYPOINT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_VALIDATOR_ENTRYPOINT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run an external drift matrix against the shared Phase 2 validator packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root containing scripts/zigux/validate-phase2.py")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker contract tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    module = load_validator(args.root.resolve())
    checks_run = run_matrix(module)
    print("PHASE2_VALIDATOR_ENTRYPOINT_PACKET=pass")
    print(f"PHASE2_VALIDATOR_ENTRYPOINT_PACKET_CASE_COUNT={checks_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

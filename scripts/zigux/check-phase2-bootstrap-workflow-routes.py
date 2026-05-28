#!/usr/bin/env python3
"""Guard the current Phase 2 bootstrap make-route packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()

TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
AGGREGATE_ROUTE = "phase2"
EXPECTED_SELF_TEST_CASE_COUNT = 24


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_exact_lines(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def require_substrings(text: str, label: str, needles: tuple[str, ...]) -> list[str]:
    return [f"{label}:missing:{needle}" for needle in needles if needle not in text]


def require_exact_line_counts(text: str, label: str, needles: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for needle in needles:
        count = count_exact_lines(text, needle)
        if count != 1:
            failures.append(f"{label}:expected_once:actual_count={count}:{needle}")
    return failures


def phony_line(text: str) -> str:
    for line in text.splitlines():
        if line.startswith(".PHONY:"):
            return line
    return ""


def load_required_routes(root: Path) -> tuple[str, ...]:
    policy_path = resolve(root, TOOLCHAIN_POLICY)
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid policy json: {policy_path}: {exc}") from exc

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")

    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError(f"invalid required_make_routes in {policy_path}")

    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise ValueError(f"invalid required_make_routes in {policy_path}")
        normalized_route = route.strip()
        if normalized_route in seen:
            raise ValueError(f"duplicate required_make_routes in {policy_path}: {normalized_route}")
        normalized.append(normalized_route)
        seen.add(normalized_route)
    return tuple(normalized)


def note_markers(routes: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"`make -C zigux {route}`" for route in (*routes, AGGREGATE_ROUTE))


def workflow_lines(routes: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"run: make -C zigux {route}" for route in (*routes, AGGREGATE_ROUTE))


def makefile_rule_lines(routes: tuple[str, ...]) -> tuple[str, ...]:
    return (*(f"{route}:" for route in routes), f"{AGGREGATE_ROUTE}: {routes[-1]}")


def phony_tokens(routes: tuple[str, ...]) -> tuple[str, ...]:
    return (".PHONY:", *routes, AGGREGATE_ROUTE)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (TOOLCHAIN_POLICY, BOOTSTRAP_NOTES, WORKFLOW, MAKEFILE):
        if not resolve(root, rel).is_file():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    try:
        routes = load_required_routes(root)
    except ValueError as exc:
        return [f"invalid_policy:{exc}"]

    note_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))

    failures.extend(require_substrings(note_text, BOOTSTRAP_NOTES.as_posix(), note_markers(routes)))
    failures.extend(require_exact_line_counts(workflow_text, WORKFLOW.as_posix(), workflow_lines(routes)))
    failures.extend(require_exact_line_counts(makefile_text, MAKEFILE.as_posix(), makefile_rule_lines(routes)))
    failures.extend(require_substrings(phony_line(makefile_text), f"{MAKEFILE.as_posix()}:phony", phony_tokens(routes)))
    return failures


def build_policy(routes: tuple[str, ...]) -> str:
    return (
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(routes),
                },
            },
            indent=2,
        )
        + "\n"
    )


def build_sample_root(root: Path, routes: tuple[str, ...]) -> None:
    markers = note_markers(routes)
    workflow_route_lines = workflow_lines(routes)
    make_rules = makefile_rule_lines(routes)
    phony = phony_tokens(routes)
    note_lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        "## Current direct packet",
        "",
        "The rematerialized make-wrapper packet is directly readable on current `master` through "
        + ", ".join(markers[:-1])
        + f", and {markers[-1]}, so keep those routes in the present packet instead of the repo-reality-gap list.",
        "",
    ]
    workflow_lines_text = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        *(
            line
            for route_line in workflow_route_lines
            for line in ("      - name: route", f"        {route_line}")
        ),
        "",
    ]
    makefile_lines_text = [
        ".PHONY: " + " ".join(phony[1:]),
        "",
        *(f"{route}:\n\t@echo {route}" for route in routes),
        "",
        make_rules[-1],
        f"\t@echo {AGGREGATE_ROUTE}",
        "",
    ]

    write_text(resolve(root, TOOLCHAIN_POLICY), build_policy(routes))
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(note_lines))
    write_text(resolve(root, WORKFLOW), "\n".join(workflow_lines_text))
    write_text(resolve(root, MAKEFILE), "\n".join(makefile_lines_text))


def remove_first(text: str, needle: str) -> str:
    if needle not in text:
        raise AssertionError(f"missing needle for mutation: {needle}")
    return text.replace(needle, "", 1)


def current_routes() -> tuple[str, ...]:
    return (
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    )


def pick_index(values: tuple[str, ...], preferred: int) -> int:
    return min(preferred, len(values) - 1)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_workflow_routes_") as tmpdir:
        root = Path(tmpdir)
        routes = current_routes()

        build_sample_root(root, routes)
        assert collect_failures(root) == []
        checks += 1

        markers = note_markers(routes)
        route_workflow_lines = workflow_lines(routes)
        rule_lines = makefile_rule_lines(routes)

        note_path = resolve(root, BOOTSTRAP_NOTES)
        workflow_path = resolve(root, WORKFLOW)
        makefile_path = resolve(root, MAKEFILE)
        policy_path = resolve(root, TOOLCHAIN_POLICY)

        build_sample_root(root, routes)
        note_path.write_text(remove_first(note_path.read_text(encoding="utf-8"), markers[1]), encoding="utf-8")
        assert any(markers[1] in failure for failure in collect_failures(root))
        checks += 1

        for workflow_line in (route_workflow_lines[0], route_workflow_lines[-1]):
            build_sample_root(root, routes)
            workflow_path.write_text(remove_first(workflow_path.read_text(encoding="utf-8"), workflow_line), encoding="utf-8")
            assert any(workflow_line in failure for failure in collect_failures(root))
            checks += 1

        build_sample_root(root, routes)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text + "      - name: duplicate-route\n" + f"        {route_workflow_lines[2]}\n",
            encoding="utf-8",
        )
        assert any(route_workflow_lines[2] in failure for failure in collect_failures(root))
        checks += 1

        for makefile_line in (rule_lines[0], rule_lines[-1]):
            build_sample_root(root, routes)
            makefile_path.write_text(remove_first(makefile_path.read_text(encoding="utf-8"), makefile_line), encoding="utf-8")
            assert any(makefile_line in failure for failure in collect_failures(root))
            checks += 1

        build_sample_root(root, routes)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(
                ".PHONY: " + " ".join(routes + (AGGREGATE_ROUTE,)),
                ".PHONY: " + " ".join(route for route in routes + (AGGREGATE_ROUTE,) if route != "phase2-genksyms"),
                1,
            ),
            encoding="utf-8",
        )
        assert any("phony" in failure for failure in collect_failures(root))
        checks += 1

        for rel in (TOOLCHAIN_POLICY, BOOTSTRAP_NOTES, WORKFLOW, MAKEFILE):
            build_sample_root(root, routes)
            resolve(root, rel).unlink()
            assert f"missing_file:{rel.as_posix()}" in collect_failures(root)
            checks += 1

        for marker in (
            markers[0],
            markers[pick_index(markers, 3)],
            markers[-1],
        ):
            build_sample_root(root, routes)
            note_path.write_text(remove_first(note_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert any(marker in failure for failure in collect_failures(root))
            checks += 1

        for workflow_line in (
            route_workflow_lines[pick_index(route_workflow_lines, 1)],
            route_workflow_lines[pick_index(route_workflow_lines, 4)],
            route_workflow_lines[-1],
        ):
            build_sample_root(root, routes)
            workflow_path.write_text(remove_first(workflow_path.read_text(encoding="utf-8"), workflow_line), encoding="utf-8")
            assert any(workflow_line in failure for failure in collect_failures(root))
            checks += 1

        build_sample_root(root, routes)
        makefile_path.write_text(remove_first(makefile_path.read_text(encoding="utf-8"), rule_lines[3]), encoding="utf-8")
        assert any(rule_lines[3] in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root, routes)
        makefile_path.write_text(remove_first(makefile_path.read_text(encoding="utf-8"), "phase2-cross"), encoding="utf-8")
        assert any("phase2-cross" in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root, routes)
        note_path.write_text(note_path.read_text(encoding="utf-8").replace("phase2-tools", "phase2-tools-drift", 1), encoding="utf-8")
        assert any("phase2-tools" in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root, routes)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        assert any(failure.startswith("invalid_policy:invalid policy json:") for failure in collect_failures(root))
        checks += 1

        build_sample_root(root, routes)
        policy_path.write_text(build_policy(tuple()), encoding="utf-8")
        assert any("invalid required_make_routes" in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root, routes)
        expanded_routes = routes + ("phase2-future",)
        policy_path.write_text(build_policy(expanded_routes), encoding="utf-8")
        failures = collect_failures(root)
        assert any("phase2-future" in failure for failure in failures)
        assert any(f"`make -C zigux phase2-future`" in failure for failure in failures)
        assert any(f"run: make -C zigux phase2-future" in failure for failure in failures)
        assert any("phase2-future:" in failure for failure in failures)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root, current_routes())
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    routes = load_required_routes(args.root)
    print("PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_POLICY_PATH={resolve(args.root, TOOLCHAIN_POLICY)}")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_REQUIRED_ROUTE_COUNT={len(routes)}")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_WORKFLOW_LINE_COUNT={len(workflow_lines(routes))}")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_MAKEFILE_LINE_COUNT={len(makefile_rule_lines(routes))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

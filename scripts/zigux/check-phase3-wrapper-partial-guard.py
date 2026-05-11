#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import tempfile
from pathlib import Path


IMPORT_MARKER = "from phase3_check_lib import run_from_wrapper"
CALL_MARKER = "run_from_wrapper(__file__)"


def classify_wrapper_text(
    path: Path,
    current: str,
    expected: str | None,
    expected_variants: tuple[str, ...],
) -> str | None:
    import_marker = IMPORT_MARKER in current
    call_marker = CALL_MARKER in current

    if expected is not None:
        if current == expected:
            return None
        return "expected-wrapper-drift"

    if current in expected_variants:
        return "stale-generated-wrapper"

    if import_marker and call_marker:
        return "stale-generated-wrapper"
    if import_marker:
        return "partial-wrapper-missing-call"
    if call_marker:
        return "partial-wrapper-missing-import"
    return None


def load_wrapper_generator(scripts_dir: Path):
    generator_path = scripts_dir / "generate-phase3-check-wrappers.py"
    spec = importlib.util.spec_from_file_location("phase3_wrapper_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load wrapper generator from {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit_wrapper_partial_shapes(scripts_dir: Path | None = None) -> int:
    from phase3_catalog import ROOT, discover_phase3_slices

    current_script = Path(__file__).resolve()
    repo_root = ROOT
    if scripts_dir is None:
        scripts_dir = repo_root / "scripts/zigux"
    else:
        scripts_dir = scripts_dir.resolve()
        repo_root = scripts_dir.parents[1]

    generator = load_wrapper_generator(scripts_dir)
    expected_wrapper = generator.render_wrapper_stub()
    entries = discover_phase3_slices(repo_root)
    expected_by_path = {entry.check_script.resolve(): expected_wrapper for entry in entries}
    expected_variants = (expected_wrapper,)

    findings: list[tuple[str, str]] = []
    for path in sorted(scripts_dir.glob("check-phase3-*.py")):
        if path.resolve() == current_script:
            continue
        current = path.read_text(encoding="utf-8")
        category = classify_wrapper_text(
            path,
            current,
            expected_by_path.get(path.resolve()),
            expected_variants,
        )
        if category is not None:
            findings.append((path.as_posix(), category))

    if findings:
        print("PHASE3_WRAPPER_PARTIAL_GUARD=fail")
        for path, category in findings:
            print(f"{category}:{path}")
        return 1

    print("PHASE3_WRAPPER_PARTIAL_GUARD=pass")
    return 0


def run_self_test() -> int:
    expected = "#!/usr/bin/env python3\nprint('expected')\n"
    shared_runner_wrapper = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "from phase3_check_lib import run_from_wrapper",
            "",
            'if __name__ == "__main__":',
            "    raise SystemExit(run_from_wrapper(__file__))",
            "",
        ]
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_wrapper_partial_guard_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        cases = [
            (tmp_dir / "check-phase3-alpha.py", expected, expected, (expected,), None),
            (
                tmp_dir / "check-phase3-stale.py",
                shared_runner_wrapper,
                None,
                (expected,),
                "stale-generated-wrapper",
            ),
            (
                tmp_dir / "check-phase3-missing-call.py",
                "#!/usr/bin/env python3\nfrom phase3_check_lib import run_from_wrapper\n",
                None,
                (expected,),
                "partial-wrapper-missing-call",
            ),
            (
                tmp_dir / "check-phase3-missing-import.py",
                "#!/usr/bin/env python3\nraise SystemExit(run_from_wrapper(__file__))\n",
                None,
                (expected,),
                "partial-wrapper-missing-import",
            ),
            (
                tmp_dir / "check-phase3-drift.py",
                "#!/usr/bin/env python3\nprint('drift')\n",
                expected,
                (expected,),
                "expected-wrapper-drift",
            ),
        ]
        for path, current, expected_text, expected_variants, wanted in cases:
            got = classify_wrapper_text(path, current, expected_text, expected_variants)
            assert got == wanted, (path.name, got, wanted)

    print("PHASE3_WRAPPER_PARTIAL_GUARD_SELF_TEST=pass")
    print("PHASE3_WRAPPER_PARTIAL_GUARD_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on partial Phase 3 wrapper shapes that evade stale-wrapper cleanup."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated classification coverage without reading the repository tree.",
    )
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    return audit_wrapper_partial_shapes()


if __name__ == "__main__":
    raise SystemExit(main())

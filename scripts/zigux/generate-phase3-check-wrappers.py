#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from phase3_check_lib import render_wrapper_stub

ROOT = Path(__file__).resolve().parents[2]
RUN_FROM_WRAPPER_IMPORT = "from phase3_check_lib import run_from_wrapper"
RUN_FROM_WRAPPER_CALL = "run_from_wrapper(__file__)"


def wrapper_state(text: str) -> str:
    if text == render_wrapper_stub():
        return "generated"
    if RUN_FROM_WRAPPER_IMPORT in text and RUN_FROM_WRAPPER_CALL in text:
        return "stale"
    return "foreign"


def audit_wrapper_templates(root: Path = ROOT) -> tuple[list[str], int]:
    issues: list[str] = []
    generated_count = 0
    wrappers_root = root / "scripts" / "zigux"
    if not wrappers_root.exists():
        return issues, generated_count
    for path in sorted(wrappers_root.glob("check-phase3-*.py")):
        state = wrapper_state(path.read_text(encoding="utf-8"))
        rel_path = path.relative_to(root).as_posix()
        if state == "generated":
            generated_count += 1
            continue
        if state == "stale":
            issues.append(f"stale_wrapper:{rel_path}")
    return issues, generated_count


def run_self_test() -> int:
    expected = render_wrapper_stub()
    stale = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from phase3_check_lib import run_from_wrapper",
            "",
            "print('stale')",
            "raise SystemExit(run_from_wrapper(__file__))",
            "",
        ]
    )
    foreign = "#!/usr/bin/env python3\nprint('hand-maintained')\n"
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_wrapper_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        wrappers_dir = tmp_dir / "scripts" / "zigux"
        wrappers_dir.mkdir(parents=True, exist_ok=True)

        expected_wrapper = wrappers_dir / "check-phase3-expected.py"
        expected_wrapper.write_text(expected, encoding="utf-8")
        stale_wrapper = wrappers_dir / "check-phase3-stale.py"
        stale_wrapper.write_text(stale, encoding="utf-8")
        foreign_wrapper = wrappers_dir / "check-phase3-foreign.py"
        foreign_wrapper.write_text(foreign, encoding="utf-8")

        assert wrapper_state(expected_wrapper.read_text(encoding="utf-8")) == "generated"
        assert wrapper_state(stale_wrapper.read_text(encoding="utf-8")) == "stale"
        assert wrapper_state(foreign_wrapper.read_text(encoding="utf-8")) == "foreign"

        issues, generated_count = audit_wrapper_templates(tmp_dir)
        assert issues == ["stale_wrapper:scripts/zigux/check-phase3-stale.py"]
        assert generated_count == 1

        stale_wrapper.write_text(expected, encoding="utf-8")
        issues, generated_count = audit_wrapper_templates(tmp_dir)
        assert issues == []
        assert generated_count == 2
    print("PHASE3_WRAPPER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Phase 3 wrapper template availability.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    if args.check:
        issues, generated_count = audit_wrapper_templates()
        if issues:
            print("PHASE3_WRAPPER_TEMPLATES=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE3_WRAPPER_TEMPLATES=pass")
        print(f"PHASE3_WRAPPER_TEMPLATE_COUNT={generated_count}")
        return 0
    print("PHASE3_WRAPPER_TEMPLATES=updated:0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

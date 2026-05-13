#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")
ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")

EXPECTED_SELF_TEST_OUTPUT = json.loads(
    r"""
{"find_bit":{"bits_per_long":64,"first":5,"next_after_6":67,"next_after_word":135,"first_zero":3,"next_zero":68,"first_and":9,"next_and":66,"last":135,"inclusive_boundary_next":63,"inclusive_boundary_zero":63,"inclusive_boundary_and":63,"tail_inclusive_boundary_next":68,"tail_inclusive_boundary_zero":68,"tail_inclusive_boundary_and":68,"past_nbits_next":7,"past_nbits_zero":7,"past_nbits_and":7,"tail_clamped_first":69,"tail_clamped_next":69,"tail_zero_clamped_first":69,"tail_zero_clamped_next":69,"tail_and_clamped_first":69,"tail_and_clamped_next":69,"tail_clamped_last":67,"tail_clamped_empty_last":69},"bitmap":{"weight":3,"scnprintf":"1-3,7,10-11","truncated_scnprintf_len":7,"truncated_scnprintf":"1-3,7,1","terminator_only_scnprintf_len":0,"terminator_only_nul":0,"zero_length_scnprintf_len":0,"alloc_words":2,"zalloc_words":2,"zalloc_values":[0,0],"and_result":true,"and_values":[10,0],"andnot_result":true,"andnot_values":[4,0],"or_values":[14,0],"xor_values":[4,0],"partial_xor_nbits":4,"partial_xor_masked_values":[14],"equal":true,"intersects":true,"subset":true,"range_after_set":[14,12,0],"range_after_clear":[0,0,0],"full_after_fill":true,"empty_after_zero":true},"string":{"strtobool_y":true,"strtobool_on":true,"strtobool_zero":false,"strtobool_off":false,"strtobool_invalid":-22,"strlcpy_len":5,"strlcpy_buffer":"hel","skip_spaces":"hello","trim_spaces":"hi","remove_spaces":"abc","replace_char":"a_b","replace_char_end":3,"replace_char_cstr_end":2,"replace_char_cstr_bytes":[97,95,0,45,122],"memchr_inv_index":4,"memchr_inv_none":true},"rbtree":{"empty_root":true,"insert_order":[5,10,15,20,25],"reverse_order":[25,20,15,10,5],"replace_order":[5,10,15,25],"erase_init_order":[5,15,25],"postorder_count":3,"erase_init_node_empty":true,"cleared_node_empty":true,"find_found_key":15,"find_missing":true,"find_first_serial":0,"next_match_serials":[0,2,4],"next_match_terminal_null":true},"argv_split":{"argc":3,"argv":["alpha","beta","gamma"],"blank_argc":0},"cmdline":{"decimal_k":{"value":65536,"rest":" rest"},"hex_m":{"value":33554432,"rest":""},"octal_k":{"value":8192,"rest":""},"invalid":{"value":0,"rest":"xyz"}},"ctype":{"mask_A":65,"mask_a":66,"mask_space":160,"isalnum_A":true,"isalpha_z":true,"isdigit_7":true,"isspace_tab":true,"isxdigit_f":true,"ispunct_bang":true,"tolower_A":97,"toupper_z":90,"isodigit_7":true,"isodigit_8":false},"hweight":{"w8":4,"w16":8,"w32":16,"w64":32,"wlong":8},"list_sort":{"tri_sorted_keys":[1,1,2,3,3],"tri_sorted_ordinals":[1,3,0,2,4],"bool_sorted_keys":[1,1,2,3,3],"bool_sorted_ordinals":[1,3,0,2,4]},"zalloc":{"zeroed":true,"freed_is_null":true,"value_zeroed":true,"value_freed_is_null":true},"str_error_r":{"enoent":"No such file or directory","unknown":"INTERNAL ERROR: strerror_r(4096, [buf], 64)=22"},"slab":{"null_without_reclaim":true,"alloc_count_after_kmalloc":1,"zero_after_kmalloc":true,"alloc_count_after_kmalloc_free":0,"array_zeroed":true,"alloc_count_after_kmalloc_array":1,"alloc_count_after_kmalloc_array_free":0,"slab_is_available":true},"vsprintf":{"scnprintf_text":"zigux:7","scnprintf_len":7,"pad_text":"id=7    ","pad_len":7}}
"""
)

EXPECTED_OUTPUT_STRUCTURE = {
    section: tuple(value.keys()) for section, value in EXPECTED_SELF_TEST_OUTPUT.items()
}

SOURCE_RELS = [
    HARNESS_REL,
    Path("tools/lib/argv_split.c"),
    Path("tools/lib/bitmap.c"),
    Path("tools/lib/cmdline.c"),
    Path("tools/lib/ctype.c"),
    Path("tools/lib/find_bit.c"),
    Path("tools/lib/hweight.c"),
    Path("tools/lib/list_sort.c"),
    Path("tools/lib/slab.c"),
    Path("tools/lib/str_error_r.c"),
    Path("tools/lib/string.c"),
    Path("tools/lib/rbtree.c"),
    Path("tools/lib/vsprintf.c"),
    Path("tools/lib/zalloc.c"),
]

REQUIRED_PARITY_KEYS = {
    "find_bit": (
        "bits_per_long",
        "first",
        "next_after_6",
        "next_after_word",
        "first_zero",
        "next_zero",
        "first_and",
        "next_and",
        "last",
        "inclusive_boundary_next",
        "inclusive_boundary_zero",
        "inclusive_boundary_and",
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
        "past_nbits_next",
        "past_nbits_zero",
        "past_nbits_and",
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last",
    ),
    "bitmap": (
        "weight",
        "scnprintf",
        "truncated_scnprintf_len",
        "truncated_scnprintf",
        "terminator_only_scnprintf_len",
        "terminator_only_nul",
        "zero_length_scnprintf_len",
        "alloc_words",
        "zalloc_words",
        "zalloc_values",
        "and_result",
        "and_values",
        "andnot_result",
        "andnot_values",
        "or_values",
        "xor_values",
        "partial_xor_nbits",
        "partial_xor_masked_values",
        "equal",
        "intersects",
        "subset",
        "range_after_set",
        "range_after_clear",
        "full_after_fill",
        "empty_after_zero",
    ),
    "string": (
        "strtobool_y",
        "strtobool_on",
        "strtobool_zero",
        "strtobool_off",
        "strtobool_invalid",
        "strlcpy_len",
        "strlcpy_buffer",
        "skip_spaces",
        "trim_spaces",
        "remove_spaces",
        "replace_char",
        "replace_char_end",
        "replace_char_cstr_end",
        "replace_char_cstr_bytes",
        "memchr_inv_index",
        "memchr_inv_none",
    ),
    "rbtree": (
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "next_match_terminal_null",
    ),
    "argv_split": (
        "argc",
        "argv",
        "blank_argc",
    ),
    "cmdline": (
        "decimal_k",
        "hex_m",
        "octal_k",
        "invalid",
    ),
    "ctype": (
        "mask_A",
        "mask_a",
        "mask_space",
        "isalnum_A",
        "isalpha_z",
        "isdigit_7",
        "isspace_tab",
        "isxdigit_f",
        "ispunct_bang",
        "tolower_A",
        "toupper_z",
        "isodigit_7",
        "isodigit_8",
    ),
    "hweight": (
        "w8",
        "w16",
        "w32",
        "w64",
        "wlong",
    ),
    "list_sort": (
        "tri_sorted_keys",
        "tri_sorted_ordinals",
        "bool_sorted_keys",
        "bool_sorted_ordinals",
    ),
    "zalloc": (
        "zeroed",
        "freed_is_null",
        "value_zeroed",
        "value_freed_is_null",
    ),
    "str_error_r": (
        "enoent",
        "unknown",
    ),
    "slab": (
        "null_without_reclaim",
        "alloc_count_after_kmalloc",
        "zero_after_kmalloc",
        "alloc_count_after_kmalloc_free",
        "array_zeroed",
        "alloc_count_after_kmalloc_array",
        "alloc_count_after_kmalloc_array_free",
        "slab_is_available",
    ),
    "vsprintf": (
        "scnprintf_text",
        "scnprintf_len",
        "pad_text",
        "pad_len",
    ),
}


def fixture_path(root: Path) -> Path:
    return root / FIXTURE_REL


def harness_path(root: Path) -> Path:
    return root / HARNESS_REL


def artifact_diff_path(root: Path) -> Path:
    return root / ARTIFACT_DIFF_REL


def source_paths(root: Path) -> list[Path]:
    return [root / rel for rel in SOURCE_RELS]


def collect_input_issues(root: Path, source_rels: list[Path] | None = None) -> list[str]:
    rels = source_rels or SOURCE_RELS
    missing: list[str] = []
    seen: set[Path] = set()
    duplicates: list[Path] = []

    required_paths = [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL]
    for rel in required_paths:
        if not (root / rel).exists():
            missing.append(f"missing:{rel.as_posix()}")

    for rel in rels:
        if rel in seen and rel not in duplicates:
            duplicates.append(rel)
        seen.add(rel)
        if not (root / rel).exists():
            missing.append(f"missing:{rel.as_posix()}")

    for rel in duplicates:
        missing.append(f"duplicate_source:{rel.as_posix()}")

    return missing


def collect_output_issues(actual: Path) -> list[str]:
    try:
        payload = json.loads(actual.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(payload, dict):
        return ["payload:json_object"]

    issues: list[str] = []
    expected_sections = set(EXPECTED_OUTPUT_STRUCTURE.keys())
    actual_sections = set(payload.keys())

    for section in sorted(expected_sections - actual_sections):
        issues.append(f"missing_section:{section}")
    for section in sorted(actual_sections - expected_sections):
        issues.append(f"unexpected_section:{section}")

    for section_name, expected_keys in EXPECTED_OUTPUT_STRUCTURE.items():
        section = payload.get(section_name)
        if not isinstance(section, dict):
            if section_name in payload:
                issues.append(f"invalid_section:{section_name}")
            continue
        expected_key_set = set(expected_keys)
        actual_key_set = set(section.keys())
        for key in expected_key_set - actual_key_set:
            issues.append(f"missing:{section_name}.{key}")
        for key in actual_key_set - expected_key_set:
            issues.append(f"unexpected:{section_name}.{key}")
    return issues


def collect_parity_key_issues(actual: Path) -> list[str]:
    payload = json.loads(actual.read_text(encoding="utf-8"))
    issues: list[str] = []
    for section_name, required_keys in REQUIRED_PARITY_KEYS.items():
        section = payload.get(section_name)
        if not isinstance(section, dict):
            issues.append(f"invalid_parity_section:{section_name}")
            continue
        for key in required_keys:
            if key not in section:
                issues.append(f"missing_parity_key:{section_name}.{key}")
    return issues


def make_self_test_root(root: Path) -> None:
    for rel in [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL, *SOURCE_RELS]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ("gcc", "cc", "clang"):
        path = shutil.which(candidate)
        if path:
            return path
    raise FileNotFoundError("no C compiler found on PATH")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def write_host_shims(root: Path) -> None:
    asm_dir = root / "asm"
    linux_dir = root / "linux"
    urcu_dir = root / "urcu"
    asm_dir.mkdir(parents=True, exist_ok=True)
    linux_dir.mkdir(parents=True, exist_ok=True)
    urcu_dir.mkdir(parents=True, exist_ok=True)
    (asm_dir / "types.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_ASM_TYPES_H__",
                "#define __ZIGUX_HOST_ASM_TYPES_H__",
                "typedef signed char __s8;",
                "typedef unsigned char __u8;",
                "typedef signed short __s16;",
                "typedef unsigned short __u16;",
                "typedef signed int __s32;",
                "typedef unsigned int __u32;",
                "typedef signed long long __s64;",
                "typedef unsigned long long __u64;",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (asm_dir / "posix_types.h").write_text(
        '#include <asm-generic/posix_types.h>\n', encoding="utf-8"
    )
    (asm_dir / "bitsperlong.h").write_text(
        '#define __BITS_PER_LONG (__CHAR_BIT__ * __SIZEOF_LONG__)\n', encoding="utf-8"
    )
    (linux_dir / "slab.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_LINUX_SLAB_H__",
                "#define __ZIGUX_HOST_LINUX_SLAB_H__",
                "#include <linux/types.h>",
                "#include <linux/gfp.h>",
                "void *kmalloc(size_t size, gfp_t gfp);",
                "void kfree(void *p);",
                "void *kmalloc_array(size_t n, size_t size, gfp_t gfp);",
                "extern int kmalloc_nr_allocated;",
                "extern int kmalloc_verbose;",
                "static inline bool slab_is_available(void) { return true; }",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (urcu_dir / "uatomic.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_URCU_UATOMIC_H__",
                "#define __ZIGUX_HOST_URCU_UATOMIC_H__",
                "#define uatomic_inc(ptr) (++(*(ptr)))",
                "#define uatomic_dec(ptr) (--(*(ptr)))",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )


def include_flags(shim_dir: Path) -> list[str]:
    return [
        "-I",
        str(shim_dir),
        "-I",
        str(ROOT / "tools" / "include"),
        "-I",
        str(ROOT / "tools" / "include" / "uapi"),
    ]


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{tail}"


def run_windows_wsl_compile(
    tmp_dir: Path,
    exe: Path,
    actual: Path,
    compiler: str,
    flags: list[str],
    sources: list[Path],
) -> None:
    script_path = tmp_dir / "run_phase1_parity.sh"
    script_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
    ]

    quoted = [
        shlex.quote(compiler),
        "-std=gnu11",
        "-Wall",
        "-Wextra",
        "-Wno-type-limits",
        "-Wno-int-to-pointer-cast",
        "-Wno-pointer-to-int-cast",
        "-o",
        shlex.quote(windows_to_wsl(exe)),
    ]
    index = 0
    while index < len(flags):
        item = flags[index]
        quoted.append(shlex.quote(item))
        if item == "-I":
            index += 1
            quoted.append(shlex.quote(windows_to_wsl(Path(flags[index]))))
        index += 1
    quoted.extend(shlex.quote(windows_to_wsl(path)) for path in sources)
    script_lines.append(" ".join(quoted))
    script_lines.append(
        f'{shlex.quote(windows_to_wsl(exe))} > {shlex.quote(windows_to_wsl(actual))}'
    )
    with script_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(script_lines) + "\n")
    run(["wsl", "bash", windows_to_wsl(script_path)], cwd=str(ROOT))


def compile_and_run(
    tmp_dir: Path,
    exe: Path,
    actual: Path,
    compiler: str,
    flags: list[str],
    sources: list[Path],
) -> None:
    if os.name == "nt" and shutil.which("wsl"):
        run_windows_wsl_compile(tmp_dir, exe, actual, compiler, flags, sources)
        return

    compile_cmd = [
        compiler,
        "-std=gnu11",
        "-Wall",
        "-Wextra",
        "-Wno-type-limits",
        "-Wno-int-to-pointer-cast",
        "-Wno-pointer-to-int-cast",
        "-o",
        str(exe),
    ]
    compile_cmd.extend(flags)
    compile_cmd.extend(str(path) for path in sources)
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_selftest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_self_test_root(tmp_root)

        assert collect_input_issues(tmp_root) == []

        (tmp_root / FIXTURE_REL).unlink()
        assert collect_input_issues(tmp_root) == [f"missing:{FIXTURE_REL.as_posix()}"]
        make_self_test_root(tmp_root)

        (tmp_root / HARNESS_REL).unlink()
        missing_harness = collect_input_issues(tmp_root)
        assert f"missing:{HARNESS_REL.as_posix()}" in missing_harness
        make_self_test_root(tmp_root)

        (tmp_root / ARTIFACT_DIFF_REL).unlink()
        missing_artifact_diff = collect_input_issues(tmp_root)
        assert f"missing:{ARTIFACT_DIFF_REL.as_posix()}" in missing_artifact_diff
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/bitmap.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert "missing:tools/lib/bitmap.c" in missing_source
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/find_bit.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert "missing:tools/lib/find_bit.c" in missing_source
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/string.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert "missing:tools/lib/string.c" in missing_source
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/rbtree.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert "missing:tools/lib/rbtree.c" in missing_source
        make_self_test_root(tmp_root)

        duplicate_sources = SOURCE_RELS + [Path("tools/lib/string.c")]
        duplicate_issues = collect_input_issues(tmp_root, duplicate_sources)
        assert "duplicate_source:tools/lib/string.c" in duplicate_issues

        actual = tmp_root / "phase1_helpers.actual.json"
        actual.write_text(json.dumps(EXPECTED_SELF_TEST_OUTPUT), encoding="utf-8")
        assert collect_output_issues(actual) == []
        assert collect_parity_key_issues(actual) == []

        missing_string_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_string_output["string"]["replace_char_cstr_bytes"]
        actual.write_text(json.dumps(missing_string_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:string.replace_char_cstr_bytes" in missing_output

        missing_string_bool_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_string_bool_output["string"]["strtobool_y"]
        actual.write_text(json.dumps(missing_string_bool_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:string.strtobool_y" in missing_output
        parity_key_output = collect_parity_key_issues(actual)
        assert "missing_parity_key:string.strtobool_y" in parity_key_output

        missing_find_bit_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_find_bit_output["find_bit"]["tail_clamped_empty_last"]
        actual.write_text(json.dumps(missing_find_bit_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:find_bit.tail_clamped_empty_last" in missing_output
        parity_key_output = collect_parity_key_issues(actual)
        assert "missing_parity_key:find_bit.tail_clamped_empty_last" in parity_key_output

        missing_find_bit_boundary_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_find_bit_boundary_output["find_bit"]["inclusive_boundary_and"]
        actual.write_text(json.dumps(missing_find_bit_boundary_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:find_bit.inclusive_boundary_and" in missing_output
        parity_key_output = collect_parity_key_issues(actual)
        assert "missing_parity_key:find_bit.inclusive_boundary_and" in parity_key_output

        missing_find_bit_tail_boundary_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_find_bit_tail_boundary_output["find_bit"]["tail_inclusive_boundary_and"]
        actual.write_text(json.dumps(missing_find_bit_tail_boundary_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:find_bit.tail_inclusive_boundary_and" in missing_output
        parity_key_output = collect_parity_key_issues(actual)
        assert "missing_parity_key:find_bit.tail_inclusive_boundary_and" in parity_key_output

        missing_find_bit_tail_clamp_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_find_bit_tail_clamp_output["find_bit"]["tail_zero_clamped_next"]
        actual.write_text(json.dumps(missing_find_bit_tail_clamp_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:find_bit.tail_zero_clamped_next" in missing_output
        parity_key_output = collect_parity_key_issues(actual)
        assert "missing_parity_key:find_bit.tail_zero_clamped_next" in parity_key_output

        missing_bitmap_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_bitmap_output["bitmap"]["partial_xor_masked_values"]
        actual.write_text(json.dumps(missing_bitmap_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:bitmap.partial_xor_masked_values" in missing_output
        parity_key_output = collect_parity_key_issues(actual)
        assert "missing_parity_key:bitmap.partial_xor_masked_values" in parity_key_output

        missing_rbtree_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        del missing_rbtree_output["rbtree"]["next_match_serials"]
        actual.write_text(json.dumps(missing_rbtree_output), encoding="utf-8")
        missing_output = collect_output_issues(actual)
        assert "missing:rbtree.next_match_serials" in missing_output
        parity_key_output = collect_parity_key_issues(actual)
        assert "missing_parity_key:rbtree.next_match_serials" in parity_key_output

        unexpected_section_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        unexpected_section_output["extra_helper"] = {"value": 1}
        actual.write_text(json.dumps(unexpected_section_output), encoding="utf-8")
        unexpected_output = collect_output_issues(actual)
        assert "unexpected_section:extra_helper" in unexpected_output

        unexpected_key_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        unexpected_key_output["find_bit"]["unexpected_clump_key"] = 99
        actual.write_text(json.dumps(unexpected_key_output), encoding="utf-8")
        unexpected_output = collect_output_issues(actual)
        assert "unexpected:find_bit.unexpected_clump_key" in unexpected_output

        invalid_section_output = copy.deepcopy(EXPECTED_SELF_TEST_OUTPUT)
        invalid_section_output["bitmap"] = []
        actual.write_text(json.dumps(invalid_section_output), encoding="utf-8")
        invalid_output = collect_output_issues(actual)
        assert "invalid_section:bitmap" in invalid_output

        actual.write_text('{"find_bit":', encoding="utf-8")
        decode_issues = collect_output_issues(actual)
        assert len(decode_issues) == 1
        assert decode_issues[0].startswith("json_decode_error:")

    print("PHASE1_PARITY_SELF_TEST=pass")
    print("PHASE1_PARITY_SELF_TEST_CASE_COUNT=22")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and check Phase 1 helper parity fixtures."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh the committed JSON fixture from current C outputs.",
    )
    parser.add_argument("--cc", help="Explicit C compiler path to use.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without compiling the live helper packet.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    input_issues = collect_input_issues(ROOT)
    if input_issues:
        print("PHASE1_PARITY=fail")
        print("PHASE1_PARITY_INPUT_ISSUES_START")
        for issue in input_issues:
            print(issue)
        print("PHASE1_PARITY_INPUT_ISSUES_END")
        return 1

    compiler = args.cc or os.environ.get("CC") or (
        "gcc" if os.name == "nt" and shutil.which("wsl") else find_compiler(None)
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)

        exe = tmp_dir / (
            "phase1_helpers_c_harness.exe"
            if os.name == "nt"
            else "phase1_helpers_c_harness"
        )
        actual = tmp_dir / "phase1_helpers.actual.json"

        compile_and_run(tmp_dir, exe, actual, compiler, include_flags(shim_dir), source_paths(ROOT))

        output_issues = collect_output_issues(actual)
        if output_issues:
            print("PHASE1_PARITY=fail")
            print("PHASE1_PARITY_OUTPUT_ISSUES_START")
            for issue in output_issues:
                print(issue)
            print("PHASE1_PARITY_OUTPUT_ISSUES_END")
            return 1

        parity_key_issues = collect_parity_key_issues(actual)
        if parity_key_issues:
            print("PHASE1_PARITY=fail")
            print("PHASE1_PARITY_KEY_ISSUES_START")
            for issue in parity_key_issues:
                print(issue)
            print("PHASE1_PARITY_KEY_ISSUES_END")
            return 1

        if args.refresh:
            fixture_path(ROOT).write_text(actual.read_text(encoding="utf-8"), encoding="utf-8")
            print("PHASE1_PARITY_REFRESH=pass")
            print(f"FIXTURE={fixture_path(ROOT)}")
            return 0

        diff_cmd = [
            sys.executable,
            str(artifact_diff_path(ROOT)),
            "--mode",
            "json",
            str(fixture_path(ROOT)),
            str(actual),
        ]
        run(diff_cmd, cwd=str(ROOT))
        print("PHASE1_PARITY=pass")
        print(f"FIXTURE={fixture_path(ROOT)}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

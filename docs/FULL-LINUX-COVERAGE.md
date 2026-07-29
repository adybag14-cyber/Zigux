# Full Linux source coverage campaign

The weekly workflow remains the fast, release-oriented cold build for x86_64, i686, ARM64, ARMv7 and RISC-V using defconfig and allmodconfig profiles.

The full source-coverage campaign is a separate monthly/manual workflow intended to answer a different question:

> Which buildable Linux source files produced an object in at least one reproducible architecture, configuration or toolchain row?

It does not attempt to create one impossible “everything kernel”. Linux contains mutually exclusive architectures, word sizes, endianness choices, Kconfig choices, compiler paths and hardening modes. Instead, the campaign compiles a bounded matrix against one exact `rolling-linux-sync` commit and aggregates the observed source-to-object relationships.

## Schedule and manual scopes

Workflow: `.github/workflows/full-linux-source-coverage.yml`

- Scheduled on the first day of each month at 02:41 UTC.
- Manual scopes: `smoke`, `architecture`, `llvm`, `rust`, `hardening`, `dtbs`, `auxiliary` and `full`.
- The source branch, tag or commit is resolved once. Every row receives the same immutable SHA.
- The campaign has no push trigger, so changing its implementation does not accidentally launch the full matrix.

The recommended rollout after changing the campaign is:

1. Run `smoke`.
2. Run the changed section only.
3. Run `full` after the section-specific result is understood.

## Full matrix

With the default two deterministic randconfig seeds, a full campaign contains 179 rows:

| Section | Rows | Coverage intent |
|---|---:|---|
| Architecture/Kconfig | 105 | 21 architecture directories × defconfig, allmodconfig, allyesconfig and two seeded randconfig profiles |
| LLVM/Clang | 22 | defconfig and allmodconfig for the 11 architecture trees maintained by the kernel LLVM build path |
| Rust | 7 | Rust-enabled builds for maintained Rust architecture targets, with architecture-specific constraints |
| Hardening and GCC plugins | 13 | Dedicated mutually incompatible compiler, sanitizer, tracing and hardening configurations |
| Device trees | 21 | `dtbs` attempt for every architecture, with unsupported trees recorded as not applicable |
| Tools, tests and documentation | 11 | UAPI headers, samples, selftests, KUnit, perf, bpftool, objtool, HTML docs, rusttest, rustdoc and rust-analyzer |

The 21 architecture-directory entries are:

`alpha`, `arc`, `arm`, `arm64`, `csky`, `hexagon`, `loongarch`, `m68k`, `microblaze`, `mips`, `nios2`, `openrisc`, `parisc`, `powerpc`, `riscv`, `s390`, `sh`, `sparc`, `um`, `x86` and `xtensa`.

## Toolchain policy

The campaign pins immutable upstream toolchain archives and verifies their SHA-256 entries before extraction:

- kernel.org GCC nolibc cross-toolchains for GCC-supported architecture rows;
- kernel.org LLVM for Clang/LLVM and Hexagon rows;
- kernel.org’s combined LLVM and Rust bundle for Rust rows;
- Ubuntu’s native GCC plus matching plugin-development headers for native GCC-plugin profiles.

Cold build means no compiler cache, no restored object tree and a new source/output directory for every row. Reusing a pinned toolchain version would not invalidate a cold source build, but the present implementation also downloads and verifies it independently in each row for isolation.

## Broad Kconfig profiles

The architecture rows run:

- the architecture’s selected defconfig;
- `allmodconfig`;
- `allyesconfig`;
- deterministic `randconfig` using each requested `KCONFIG_SEED`.

Broad profiles deliberately disable features covered by dedicated rows when those features would make the general cross-toolchain profile misleading or mutually incompatible: Rust, GCC plugins, selected sanitizer/debug modes and warning-as-error policy. The exact resulting `.config` and all adjustments are retained in the row record.

`make -k` is used for coverage rows. This preserves objects successfully compiled before a later source file fails. A failed row remains failed in GitHub Actions, but its partial source-to-object evidence is still aggregated.

## Dedicated Rust coverage

Rust is tested separately on its maintained architecture targets. Each row:

1. installs the pinned LLVM+Rust bundle;
2. runs `make LLVM=1 rustavailable`;
3. requests `CONFIG_RUST=y` and modules;
4. applies required architecture constraints, such as disabling EXPOLINE for s390;
5. requests available in-tree Rust samples;
6. fails if Kconfig does not actually retain `CONFIG_RUST=y`.

Rust developer targets are also built separately: `rusttest`, `rustdoc` and `rust-analyzer`.

## Dedicated hardening and compiler paths

The campaign includes independent rows for:

- GCC RANDSTRUCT;
- GCC latent entropy;
- Clang CFI;
- Clang ThinLTO;
- generic KASAN;
- ARM64 software-tag KASAN;
- KCSAN;
- UBSAN;
- BTF debug information;
- PREEMPT_RT;
- lockdep/prove locking;
- GCOV;
- KCOV.

Requested Kconfig symbols are verified after `olddefconfig`. A profile fails rather than silently pretending to test an option that Kconfig rejected.

## Source-to-object evidence

Every row scans generated Kbuild `.cmd` files and object paths. It emits a compressed mapping with:

- build ID;
- architecture;
- profile;
- toolchain;
- generated object;
- source file.

The aggregate job uses an on-disk SQLite index so millions of potential mapping rows do not need to remain in memory. The consolidated artifact contains:

- `SUMMARY.md`;
- `summary.json`;
- `build-status.tsv`;
- `source-to-object.tsv.zst`;
- `source-coverage-summary.tsv.zst`;
- `uncompiled-sources.tsv.zst`.

An “uncompiled” entry means no generated object was observed in this campaign. The report gives a conservative explanation, but it does not claim to prove an exact Kconfig dependency chain.

## Storage policy

Full kernel output trees and binaries are intentionally not uploaded by this campaign. Uploading hundreds of complete allmodconfig/allyesconfig trees would create excessive storage and make aggregation impractical. The weekly workflow remains responsible for usable kernel packages on the principal five architectures.

Each full-campaign row uploads only compact evidence:

- manifest and row definition;
- exact final `.config` where applicable;
- compressed source-to-object mapping;
- selected output inventory;
- a bounded build-log excerpt.

The complete command stream remains available in the GitHub Actions job log.

## Meaning of the percentage

The aggregate percentage is **observed compile coverage**:

```text
source files mapped to at least one generated object
----------------------------------------------------
all .c, .S, .s and .rs files in the exact source tree
```

It is not proof that every object linked, that every kernel booted, that device-tree blobs match hardware, or that runtime tests passed. Those are separate validation layers.

## Rust toolchain policy

Rust rows use the pinned Rust 1.96.1 toolchain installed through Ubuntu's `rustup` package, the pinned `bindgen-0.71` package, and the same verified kernel.org LLVM archive used by LLVM rows. This satisfies the rolling source's s390 minimum while keeping `rust-src`, `rustfmt`, and Clippy available for Rust developer targets.

KUnit is built from `tools/testing/kunit/configs/default.config`, and the perf row installs its required traceevent, tracefs, Capstone, libpfm, and Babeltrace 2 development libraries.

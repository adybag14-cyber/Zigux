# Full Linux campaign 30451881719 diagnostic snapshot

Snapshot sequence: 2
Generated: 2026-07-29T13:06:33Z

## Job-state totals

| State | Count |
|---|---:|
| failure | 11 |
| in_progress | 19 |
| queued | 16 |
| success | 39 |

## Failed jobs

### Rust-enabled architecture coverage (arm, multi_v7_defconfig, RUST, MODULES, libclang-dev, arm-lin... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575692768

```text
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:30:47.5281587Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:30:47.5282193Z   runner_type: kernel
2026-07-29T12:30:47.5282637Z   scope: full
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:30:50.5072983Z   RUNNER_TYPE: kernel
2026-07-29T12:30:50.5073242Z ##[endgroup]
2026-07-29T12:30:50.5447060Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:46:09.1606977Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:46:09.1607272Z   RUNNER_TYPE: kernel
2026-07-29T12:46:09.1607498Z ##[endgroup]
2026-07-29T12:50:23.0828611Z ##[error]rust-arm: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-rust-arm/toolchains/rust-llvm
2026-07-29T12:50:23.0836899Z {"build_id": "rust-arm", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T12:50:23.0932004Z ##[error]Process completed with exit code 1.
2026-07-29T12:50:23.1023284Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:50:23.1023587Z with:
```

### Rust-enabled architecture coverage (loongarch, defconfig, RUST, MODULES, libclang-dev, loongarch6... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575692798

```text
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:30:53.0946289Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:30:53.0947064Z   runner_type: kernel
2026-07-29T12:30:53.0947671Z   scope: full
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:30:56.0328723Z   RUNNER_TYPE: kernel
2026-07-29T12:30:56.0328980Z ##[endgroup]
2026-07-29T12:30:56.0673647Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:31:55.4501807Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:31:55.4502455Z   RUNNER_TYPE: kernel
2026-07-29T12:31:55.4502669Z ##[endgroup]
2026-07-29T12:34:55.6203830Z ##[error]rust-loongarch: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-rust-loongarch/toolchains/rust-llvm
2026-07-29T12:34:55.6216364Z {"build_id": "rust-loongarch", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T12:34:55.6309429Z ##[error]Process completed with exit code 1.
2026-07-29T12:34:55.6409345Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:34:55.6409634Z with:
```

### Rust-enabled architecture coverage (s390, defconfig, EXPOLINE, RUST, MODULES, libclang-dev, s390-... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575692857

```text
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:30:46.4489042Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:30:46.4489842Z   runner_type: kernel
2026-07-29T12:30:46.4490295Z   scope: full
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:30:49.0452878Z   RUNNER_TYPE: kernel
2026-07-29T12:30:49.0453901Z ##[endgroup]
2026-07-29T12:30:49.0904941Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:32:03.5626539Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:32:03.5626846Z   RUNNER_TYPE: kernel
2026-07-29T12:32:03.5627083Z ##[endgroup]
2026-07-29T12:35:36.0590426Z ##[error]rust-s390: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-rust-s390/toolchains/rust-llvm
2026-07-29T12:35:36.0598446Z {"build_id": "rust-s390", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T12:35:36.0733428Z ##[error]Process completed with exit code 1.
2026-07-29T12:35:36.0826600Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:35:36.0826901Z with:
```

### Tools, samples, tests and documentation (libbabeltrace-dev, libcap-dev, libdw-dev, libiberty-dev,... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575693323

```text
2026-07-29T12:32:54.5541329Z Makefile.config:1044: No babeltrace2 found, disables 'perf data' CTF format support, please install libbabeltrace2-dev[el]
2026-07-29T12:32:54.5542569Z Makefile.config:1060: No libcapstone found, disables disasm engine support for 'perf script', please install libcapstone-dev/capstone-devel
2026-07-29T12:32:54.5543818Z Makefile.config:1109: libpfm4 not found, disables libpfm4 support. Please install libpfm-devel or libpfm4-dev
2026-07-29T12:32:54.5545398Z Makefile.config:1127: *** ERROR: libtraceevent is missing. Please install libtraceevent-dev/libtraceevent-devel and/or set LIBTRACEEVENT_DIR or build with NO_LIBTRACEEVENT=1.  Stop.
2026-07-29T12:32:54.5546821Z make[1]: *** [Makefile.perf:288: sub-make] Error 2
2026-07-29T12:32:54.5547264Z make: *** [Makefile:76: all] Error 2
2026-07-29T12:32:54.5547878Z make: Leaving directory '/home/runner/work/_temp/full-linux-aux-perf/source/tools/perf'
2026-07-29T12:32:54.5548727Z {"build_id": "aux-perf", "mapped_source_count": 0, "object_count": 0, "status": "build_failed"}
2026-07-29T12:32:54.5702551Z ##[error]Process completed with exit code 1.
2026-07-29T12:32:54.5799778Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:32:54.5800067Z with:
2026-07-29T12:32:54.5800315Z   name: coverage-record-aux-perf-30451881719-1
```

### Tools, samples, tests and documentation (kunit, auxiliary, KUnit build, kunit, kunit) / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575693339

```text
2026-07-29T12:32:49.6484420Z     with open(dst, 'wb') as fdst:
2026-07-29T12:32:49.6484668Z          ^^^^^^^^^^^^^^^
2026-07-29T12:32:49.6485211Z FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/Zigux/Zigux/out-full-linux/aux-kunit/kunit/.kunitconfig'
2026-07-29T12:32:49.6486172Z {"build_id": "aux-kunit", "mapped_source_count": 0, "object_count": 0, "status": "build_failed"}
2026-07-29T12:32:49.6635317Z ##[error]Process completed with exit code 1.
2026-07-29T12:32:49.6732721Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:32:49.6733022Z with:
2026-07-29T12:32:49.6733269Z   name: coverage-record-aux-kunit-30451881719-1
```

### Rust-enabled architecture coverage (x86, x86_64_defconfig, RUST, MODULES, libclang-dev, x86_64-li... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575693699

```text
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:40:21.9819036Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:40:21.9819647Z   runner_type: kernel
2026-07-29T12:40:21.9820096Z   scope: full
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:40:24.6317952Z   RUNNER_TYPE: kernel
2026-07-29T12:40:24.6318220Z ##[endgroup]
2026-07-29T12:40:24.6707711Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:40:59.3345911Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:40:59.3346225Z   RUNNER_TYPE: kernel
2026-07-29T12:40:59.3346451Z ##[endgroup]
2026-07-29T12:42:22.3771235Z ##[error]rust-x86: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-rust-x86/toolchains/rust-llvm
2026-07-29T12:42:22.3780012Z {"build_id": "rust-x86", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T12:42:22.3899391Z ##[error]Process completed with exit code 1.
2026-07-29T12:42:22.3997439Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:42:22.3997758Z with:
```

### Rust-enabled architecture coverage (riscv, defconfig, RUST, MODULES, libclang-dev, riscv64-linux,... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575693798

```text
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:35:59.7836426Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:35:59.7837066Z   runner_type: kernel
2026-07-29T12:35:59.7837516Z   scope: full
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:36:02.0697260Z   RUNNER_TYPE: kernel
2026-07-29T12:36:02.0698291Z ##[endgroup]
2026-07-29T12:36:02.1159143Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:37:33.1198107Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:37:33.1198408Z   RUNNER_TYPE: kernel
2026-07-29T12:37:33.1198631Z ##[endgroup]
2026-07-29T12:40:03.0394426Z ##[error]rust-riscv: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-rust-riscv/toolchains/rust-llvm
2026-07-29T12:40:03.0403882Z {"build_id": "rust-riscv", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T12:40:03.0510100Z ##[error]Process completed with exit code 1.
2026-07-29T12:40:03.0610651Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:40:03.0610973Z with:
```

### Rust-enabled architecture coverage (um, defconfig, RUST, MODULES, libclang-dev, rust-um, um, rust... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575693845

```text
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:38:58.2807061Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:38:58.2807956Z   runner_type: kernel
2026-07-29T12:38:58.2808526Z   scope: full
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:39:00.9526850Z   RUNNER_TYPE: kernel
2026-07-29T12:39:00.9527163Z ##[endgroup]
2026-07-29T12:39:00.9997545Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:42:59.6571236Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:42:59.6571517Z   RUNNER_TYPE: kernel
2026-07-29T12:42:59.6571741Z ##[endgroup]
2026-07-29T12:43:48.3605769Z ##[error]rust-um: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-rust-um/toolchains/rust-llvm
2026-07-29T12:43:48.3612588Z {"build_id": "rust-um", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T12:43:48.3722912Z ##[error]Process completed with exit code 1.
2026-07-29T12:43:48.3799389Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:43:48.3799680Z with:
```

### Rust-enabled architecture coverage (arm64, defconfig, RUST, MODULES, libclang-dev, aarch64-linux,... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575693980

```text
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:40:17.9121456Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:40:17.9122456Z   runner_type: kernel
2026-07-29T12:40:17.9123183Z   scope: full
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:40:21.0632558Z   RUNNER_TYPE: kernel
2026-07-29T12:40:21.0632792Z ##[endgroup]
2026-07-29T12:40:21.0995795Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "rust"
}
2026-07-29T12:41:33.0283781Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T12:41:33.0284080Z   RUNNER_TYPE: kernel
2026-07-29T12:41:33.0284301Z ##[endgroup]
2026-07-29T12:43:48.1515655Z ##[error]rust-arm64: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-rust-arm64/toolchains/rust-llvm
2026-07-29T12:43:48.1524305Z {"build_id": "rust-arm64", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T12:43:48.1635733Z ##[error]Process completed with exit code 1.
2026-07-29T12:43:48.1731811Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:43:48.1732120Z with:
```

### Tools, samples, tests and documentation (libcap-dev, libmount-dev, libnuma-dev, liburing-dev, sel... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575694575

```text
2026-07-29T12:48:09.0070518Z make[1]: Leaving directory '/home/runner/work/_temp/full-linux-aux-selftests/source/tools/testing/selftests/acct'
2026-07-29T12:48:09.0071326Z make[1]: Entering directory '/home/runner/work/_temp/full-linux-aux-selftests/source/tools/testing/selftests/alsa'
2026-07-29T12:48:09.0073981Z Makefile:4: *** Package alsa not found, please install alsa development package or add directory containing `alsa.pc` in PKG_CONFIG_PATH.  Stop.
2026-07-29T12:48:09.0075338Z make[1]: Leaving directory '/home/runner/work/_temp/full-linux-aux-selftests/source/tools/testing/selftests/alsa'
2026-07-29T12:48:09.0076283Z make: *** [Makefile:218: all] Error 2
2026-07-29T12:48:09.0077086Z make: Leaving directory '/home/runner/work/_temp/full-linux-aux-selftests/source/tools/testing/selftests'
2026-07-29T12:48:09.0078232Z {"build_id": "aux-selftests", "mapped_source_count": 0, "object_count": 0, "status": "build_failed"}
2026-07-29T12:48:09.0263767Z ##[error]Process completed with exit code 1.
2026-07-29T12:48:09.0369107Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:48:09.0369433Z with:
2026-07-29T12:48:09.0369703Z   name: coverage-record-aux-selftests-30451881719-1
```

### Tools, samples, tests and documentation (libcap-dev, binutils-dev, bpftool, auxiliary, bpftool, b... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90575694824

```text
2026-07-29T12:50:43.0974071Z   CLANG   pid_iter.bpf.o
2026-07-29T12:50:43.0974283Z   CLANG   profiler.bpf.o
2026-07-29T12:50:43.0974512Z make: llvm-strip: No such file or directory
2026-07-29T12:50:43.0974807Z make: *** [Makefile:263: profiler.bpf.o] Error 127
2026-07-29T12:50:43.0975115Z make: llvm-strip: No such file or directory
2026-07-29T12:50:43.0975413Z make: *** [Makefile:263: pid_iter.bpf.o] Error 127
2026-07-29T12:50:43.0975716Z make: Target 'all' not remade because of errors.
2026-07-29T12:50:43.0976181Z make: Leaving directory '/home/runner/work/_temp/full-linux-aux-bpftool/source/tools/bpf/bpftool'
2026-07-29T12:50:43.0976790Z {"build_id": "aux-bpftool", "mapped_source_count": 1, "object_count": 79, "status": "build_failed"}
2026-07-29T12:50:43.1085922Z ##[error]Process completed with exit code 1.
2026-07-29T12:50:43.1184637Z ##[group]Run actions/upload-artifact@v7
2026-07-29T12:50:43.1184942Z with:
2026-07-29T12:50:43.1185183Z   name: coverage-record-aux-bpftool-30451881719-1
```

## In-progress or queued jobs at snapshot time

- GCC plugin and incompatible hardening coverage (arm64, defconfig, WERROR, RUST, GCC_PLUGINS, KASA... / build: in_progress
- LLVM/Clang coverage (arm, allmodconfig, arm-linux-gnueabi, llvm-arm-allmodconfig, arm, llvm, ARMv... / build: in_progress
- LLVM/Clang coverage (loongarch, allmodconfig, loongarch64-linux, llvm-loongarch-allmodconfig, loo... / build: in_progress
- LLVM/Clang coverage (mips, allmodconfig, mips-linux, llvm-mips-allmodconfig, mips, llvm, MIPS, tr... / build: in_progress
- Architecture/Kconfig coverage (arc, allyesconfig, arc-linux, arch-arc-allyesconfig, arc, architec... / build: in_progress
- Architecture/Kconfig coverage (alpha, allyesconfig, alpha-linux, arch-alpha-allyesconfig, alpha, ... / build: in_progress
- Architecture/Kconfig coverage (arc, allmodconfig, arc-linux, arch-arc-allmodconfig, arc, architec... / build: in_progress
- LLVM/Clang coverage (arm64, defconfig, aarch64-linux, llvm-arm64-defconfig, arm64, llvm, ARM64, t... / build: in_progress
- LLVM/Clang coverage (arm64, allmodconfig, aarch64-linux, llvm-arm64-allmodconfig, arm64, llvm, AR... / build: in_progress
- LLVM/Clang coverage (hexagon, allmodconfig, llvm-hexagon-allmodconfig, hexagon, llvm, Hexagon, tr... / build: in_progress
- Architecture/Kconfig coverage (alpha, allmodconfig, alpha-linux, arch-alpha-allmodconfig, alpha, ... / build: in_progress
- Architecture/Kconfig coverage (arm, allmodconfig, arm-linux-gnueabi, arch-arm-allmodconfig, arm, ... / build: in_progress
- LLVM/Clang coverage (loongarch, defconfig, loongarch64-linux, llvm-loongarch-defconfig, loongarch... / build: in_progress
- Tools, samples, tests and documentation (libclang-dev, rusttest, auxiliary, Rust tests, rusttest,... / build: in_progress
- Device-tree coverage (true, sh, shx3_defconfig, u-boot-tools, sh4-linux, dtbs-sh, sh, dtbs, Super... / build: in_progress
- Device-tree coverage (true, um, defconfig, u-boot-tools, dtbs-um, um, dtbs, User Mode Linux devic... / build: in_progress
- Architecture/Kconfig coverage (arm, allyesconfig, arm-linux-gnueabi, arch-arm-allyesconfig, arm, ... / build: in_progress
- Architecture/Kconfig coverage (arm, randconfig, arm-linux-gnueabi, arch-arm-randconfig-0xC0FFEE, ... / build: in_progress
- Architecture/Kconfig coverage (arm, randconfig, arm-linux-gnueabi, arch-arm-randconfig-0x5EED, ar... / build: in_progress
- GCC plugin and incompatible hardening coverage (x86, x86_64_defconfig, WERROR, RUST, GCC_PLUGINS,... / build: queued
- Device-tree coverage (true, x86, x86_64_defconfig, u-boot-tools, x86_64-linux, dtbs-x86, x86, dtb... / build: queued
- Tools, samples, tests and documentation (libclang-dev, rustdoc, auxiliary, Rust documentation, ru... / build: queued
- GCC plugin and incompatible hardening coverage (x86, x86_64_defconfig, WERROR, RUST, GCC_PLUGINS,... / build: queued
- LLVM/Clang coverage (powerpc, ppc64_defconfig, powerpc64-linux, llvm-powerpc-defconfig, powerpc, ... / build: queued
- Device-tree coverage (true, xtensa, defconfig, u-boot-tools, xtensa-linux, dtbs-xtensa, xtensa, d... / build: queued
- GCC plugin and incompatible hardening coverage (x86, x86_64_defconfig, WERROR, RUST, GCC_PLUGINS,... / build: queued
- LLVM/Clang coverage (powerpc, allmodconfig, powerpc64-linux, llvm-powerpc-allmodconfig, powerpc, ... / build: queued
- Tools, samples, tests and documentation (libclang-dev, rust-analyzer, auxiliary, Rust analyzer me... / build: queued
- GCC plugin and incompatible hardening coverage (x86, x86_64_defconfig, WERROR, RUST, GCC_PLUGINS,... / build: queued
- Architecture/Kconfig coverage (arm64, defconfig, aarch64-linux, arch-arm64-defconfig, arm64, arch... / build: queued
- GCC plugin and incompatible hardening coverage (x86, x86_64_defconfig, WERROR, RUST, GCC_PLUGINS,... / build: queued
- Architecture/Kconfig coverage (arm64, allmodconfig, aarch64-linux, arch-arm64-allmodconfig, arm64... / build: queued
- Architecture/Kconfig coverage (arm64, allyesconfig, aarch64-linux, arch-arm64-allyesconfig, arm64... / build: queued
- LLVM/Clang coverage (riscv, defconfig, riscv64-linux, llvm-riscv-defconfig, riscv, llvm, RISC-V 6... / build: queued
- Architecture/Kconfig coverage (arm64, randconfig, aarch64-linux, arch-arm64-randconfig-0xC0FFEE, ... / build: queued

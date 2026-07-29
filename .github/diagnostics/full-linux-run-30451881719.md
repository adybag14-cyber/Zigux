# Full Linux campaign 30451881719 diagnostic snapshot

Snapshot sequence: 2
Generated: 2026-07-29T13:27:11Z

## Job-state totals

| State | Count |
|---|---:|
| cancelled | 23 |
| failure | 16 |
| queued | 1 |
| success | 48 |

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

### Tools, samples, tests and documentation (libclang-dev, rusttest, auxiliary, Rust tests, rusttest,... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90576347444

```text
  "profile": "rusttest",
  "task": "rusttest",
  "toolchain": "rust"
}
2026-07-29T13:00:57.1781656Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:00:57.1781995Z   runner_type: auxiliary
2026-07-29T13:00:57.1782259Z   scope: full
--
  "profile": "rusttest",
  "task": "rusttest",
  "toolchain": "rust"
}
2026-07-29T13:00:59.8660891Z   RUNNER_TYPE: auxiliary
2026-07-29T13:00:59.8661113Z ##[endgroup]
2026-07-29T13:00:59.8917446Z ##[group]Run set -euo pipefail
--
  "profile": "rusttest",
  "task": "rusttest",
  "toolchain": "rust"
}
2026-07-29T13:06:43.5293105Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:06:43.5293381Z   RUNNER_TYPE: auxiliary
2026-07-29T13:06:43.5293634Z ##[endgroup]
2026-07-29T13:07:33.0489536Z ##[error]aux-rusttest: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-aux-rusttest/toolchains/rust-llvm
2026-07-29T13:07:33.0495856Z {"build_id": "aux-rusttest", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T13:07:33.0603904Z ##[error]Process completed with exit code 1.
2026-07-29T13:07:33.0761280Z ##[group]Run actions/upload-artifact@v7
2026-07-29T13:07:33.0761536Z with:
```

### GCC plugin and incompatible hardening coverage (x86, x86_64_defconfig, WERROR, RUST, GCC_PLUGINS,... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90578391755

```text
  "enable": [
    "DEBUG_INFO",
    "DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT",
    "DEBUG_INFO_BTF"
  ],
  "gcc_triple": "x86_64-linux",
  "id": "btf",
--
    "modules"
  ],
  "toolchain": "native-gcc"
}
2026-07-29T13:06:56.3405337Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:06:56.3405945Z   runner_type: kernel
2026-07-29T13:06:56.3406396Z   scope: full
--
  "enable": [
    "DEBUG_INFO",
    "DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT",
    "DEBUG_INFO_BTF"
  ],
  "gcc_triple": "x86_64-linux",
  "id": "btf",
--
    "modules"
  ],
  "toolchain": "native-gcc"
}
2026-07-29T13:06:59.2827226Z   RUNNER_TYPE: kernel
2026-07-29T13:06:59.2827481Z ##[endgroup]
2026-07-29T13:06:59.3186138Z ##[group]Run set -euo pipefail
--
  "enable": [
    "DEBUG_INFO",
    "DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT",
    "DEBUG_INFO_BTF"
  ],
  "gcc_triple": "x86_64-linux",
  "id": "btf",
--
    "modules"
  ],
  "toolchain": "native-gcc"
}
2026-07-29T13:07:36.9493497Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:07:36.9493791Z   RUNNER_TYPE: kernel
2026-07-29T13:07:36.9494001Z ##[endgroup]
```

### Tools, samples, tests and documentation (libclang-dev, rustdoc, auxiliary, Rust documentation, ru... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90578841711

```text
  "profile": "rustdoc",
  "task": "rustdoc",
  "toolchain": "rust"
}
2026-07-29T13:06:57.1219392Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:06:57.1220032Z   runner_type: auxiliary
2026-07-29T13:06:57.1220620Z   scope: full
--
  "profile": "rustdoc",
  "task": "rustdoc",
  "toolchain": "rust"
}
2026-07-29T13:06:59.1453322Z   RUNNER_TYPE: auxiliary
2026-07-29T13:06:59.1453763Z ##[endgroup]
2026-07-29T13:06:59.1839015Z ##[group]Run set -euo pipefail
--
  "profile": "rustdoc",
  "task": "rustdoc",
  "toolchain": "rust"
}
2026-07-29T13:08:02.7366439Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:08:02.7366741Z   RUNNER_TYPE: auxiliary
2026-07-29T13:08:02.7366959Z ##[endgroup]
2026-07-29T13:09:17.9990161Z ##[error]aux-rustdoc: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-aux-rustdoc/toolchains/rust-llvm
2026-07-29T13:09:17.9997452Z {"build_id": "aux-rustdoc", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T13:09:18.0119167Z ##[error]Process completed with exit code 1.
2026-07-29T13:09:18.0214346Z ##[group]Run actions/upload-artifact@v7
2026-07-29T13:09:18.0214650Z with:
```

### GCC plugin and incompatible hardening coverage (x86, x86_64_defconfig, WERROR, RUST, GCC_PLUGINS,... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90579027641

```text
    "modules"
  ],
  "toolchain": "native-gcc"
}
2026-07-29T13:07:48.4156981Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:07:48.4157740Z   runner_type: kernel
2026-07-29T13:07:48.4158246Z   scope: full
--
    "modules"
  ],
  "toolchain": "native-gcc"
}
2026-07-29T13:07:51.1761528Z   RUNNER_TYPE: kernel
2026-07-29T13:07:51.1761880Z ##[endgroup]
2026-07-29T13:07:51.2215435Z ##[group]Run set -euo pipefail
--
    "modules"
  ],
  "toolchain": "native-gcc"
}
2026-07-29T13:09:14.5892246Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:09:14.5892679Z   RUNNER_TYPE: kernel
2026-07-29T13:09:14.5892971Z ##[endgroup]
```

### Tools, samples, tests and documentation (libclang-dev, rust-analyzer, auxiliary, Rust analyzer me... / build

Job: https://github.com/adybag14-cyber/Zigux/actions/runs/30451881719/job/90579909433

```text
  "profile": "rust-analyzer",
  "task": "rust-analyzer",
  "toolchain": "rust"
}
2026-07-29T13:10:37.8808253Z   source_sha: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:10:37.8808889Z   runner_type: auxiliary
2026-07-29T13:10:37.8809378Z   scope: full
--
  "profile": "rust-analyzer",
  "task": "rust-analyzer",
  "toolchain": "rust"
}
2026-07-29T13:10:40.5341276Z   RUNNER_TYPE: auxiliary
2026-07-29T13:10:40.5341563Z ##[endgroup]
2026-07-29T13:10:40.5723818Z ##[group]Run set -euo pipefail
--
  "profile": "rust-analyzer",
  "task": "rust-analyzer",
  "toolchain": "rust"
}
2026-07-29T13:12:01.0141574Z   SOURCE_SHA: 62cc90241548d5570ee68e01aaba6506964e9811
2026-07-29T13:12:01.0141883Z   RUNNER_TYPE: auxiliary
2026-07-29T13:12:01.0142110Z ##[endgroup]
2026-07-29T13:14:51.7424441Z ##[error]aux-rust-analyzer: FileNotFoundError: bindgen was not found below /home/runner/work/_temp/full-linux-aux-rust-analyzer/toolchains/rust-llvm
2026-07-29T13:14:51.7435714Z {"build_id": "aux-rust-analyzer", "mapped_source_count": null, "object_count": null, "status": "infrastructure_error"}
2026-07-29T13:14:51.7553734Z ##[error]Process completed with exit code 1.
2026-07-29T13:14:51.7934891Z ##[group]Run actions/upload-artifact@v7
2026-07-29T13:14:51.7935224Z with:
```

## In-progress or queued jobs at snapshot time

- Aggregate source-to-object coverage report: queued

PHONY += phase2-validate phase2-tools phase2-kconfig phase2-cross phase2
PHONY += phase3-validate phase3-abi phase3-interop phase3

PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

phase2-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py

phase2-tools:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig

phase2-kconfig:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
	cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig

phase2-cross:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py

phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross

phase3-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3.py

phase3-abi:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py
	cd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig

phase3-interop:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-bitmap-cpumask.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-list-hlist.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-errptr-xarray.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-xarray-slot.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-idr-slot.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-ida-bitmap.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-ida-alloc.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-ida-range.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-ida-range-set.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-ida-policy.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-minor-alloc.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-dev-region.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-cdev-add.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-cdev-lookup.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-open.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-fops.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-route.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-io.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-xfer.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-resume.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-retry.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-requeue.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-complete.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-policy.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-budget.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-policy.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-budget.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window-policy.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window.py

phase3: phase3-validate phase3-abi phase3-interop

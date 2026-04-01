# Zigux Documentation

This directory is the product documentation root for Zigux.

Scope
- product charter
- review rules
- freeze map
- phase closure records
- phase policy
- future porting guides
- validation and artifact-diff policy

Rules
- keep product commitments here, not in ad hoc issue threads
- keep deep-core freeze decisions explicit
- require validation and rollback language for every new active port target
- align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

Current closure records
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`

Active slice records
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `Documentation/zigux/phase3-list-hlist-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `Documentation/zigux/phase3-idr-slot-slice.md`
- `Documentation/zigux/phase3-ida-bitmap-slice.md`
- `Documentation/zigux/phase3-ida-alloc-slice.md`
- `Documentation/zigux/phase3-ida-range-slice.md`
- `Documentation/zigux/phase3-ida-range-set-slice.md`
- `Documentation/zigux/phase3-ida-policy-slice.md`
- `Documentation/zigux/phase3-minor-alloc-slice.md`
- `Documentation/zigux/phase3-dev-region-slice.md`
- `Documentation/zigux/phase3-cdev-add-slice.md`
- `Documentation/zigux/phase3-cdev-lookup-slice.md`
- `Documentation/zigux/phase3-chrdev-open-slice.md`
- `Documentation/zigux/phase3-chrdev-fops-slice.md`
- `Documentation/zigux/phase3-chrdev-route-slice.md`
- `Documentation/zigux/phase3-chrdev-io-slice.md`
- `Documentation/zigux/phase3-chrdev-xfer-slice.md`
- `Documentation/zigux/phase3-chrdev-resume-slice.md`
- `Documentation/zigux/phase3-chrdev-retry-slice.md`
- `Documentation/zigux/phase3-chrdev-requeue-slice.md`
- `Documentation/zigux/phase3-chrdev-complete-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-policy-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-budget-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-policy-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-budget-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-slice.md`
- `Documentation/zigux/phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-slice.md`

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
- [phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-slice.md](Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-slice.md)
- [phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-slice.md](Documentation/zigux/phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-slice.md)

- `chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window`
- `chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget`

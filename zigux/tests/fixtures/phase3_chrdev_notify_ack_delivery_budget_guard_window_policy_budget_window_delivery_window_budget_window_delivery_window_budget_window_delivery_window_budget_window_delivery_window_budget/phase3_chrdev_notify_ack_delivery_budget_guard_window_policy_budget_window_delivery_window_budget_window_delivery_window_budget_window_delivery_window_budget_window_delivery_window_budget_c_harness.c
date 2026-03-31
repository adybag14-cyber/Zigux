#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summary *summary)
{
	printf("{\"parent_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status\":%u,"
	       "\"delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags\":%u,"
	       "\"delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before\":%u,"
	       "\"delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after\":%u,"
	       "\"deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before\":%u,"
	       "\"deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after\":%u,"
	       "\"delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status\":%u,"
	       "\"acked_count\":%u,"
	       "\"deferred_count\":%u,"
	       "\"suppressed_count\":%u,"
	       "\"coalesced_count\":%u,"
	       "\"dropped_count\":%u,"
	       "\"skipped_count\":%u,"
	       "\"held_count\":%u}",
	       summary->parent.delivery_window_budget_window_delivery_window_budget_window_delivery_window_status,
	       summary->delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags,
	       summary->delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before,
	       summary->delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after,
	       summary->deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before,
	       summary->deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after,
	       summary->delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status,
	       summary->acked_count,
	       summary->deferred_count,
	       summary->suppressed_count,
	       summary->coalesced_count,
	       summary->dropped_count,
	       summary->skipped_count,
	       summary->held_count);
}

static struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view make_parent_acked(const unsigned long *words)
{
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1);
}

static struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view make_parent_coalesced(const unsigned long *words)
{
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0, 3, 0, 1, 0, 2, 1, 1, 0, 1, 0, 1, 0, 3, 0, 0, 0);
}

static struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view make_parent_dropped(const unsigned long *words)
{
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0);
}

static struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view make_parent_skipped(const unsigned long *words)
{
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ, ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1);
}

static struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_view make_delivery_parent(
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_bits,
	zigux_u32 primary_guard, zigux_u32 deferred_guard,
	zigux_u32 primary_window, zigux_u32 deferred_window, zigux_u32 window_floor,
	zigux_u32 policy_flags,
	zigux_u32 primary_budget, zigux_u32 deferred_budget,
	zigux_u32 budget_window, zigux_u32 budget_window_floor,
	zigux_u32 primary_delivery_budget, zigux_u32 deferred_delivery_budget)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_bits, primary_guard, deferred_guard);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, primary_window, deferred_window, window_floor);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, policy_flags);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, primary_budget, deferred_budget);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view budget_window_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, budget_window, budget_window_floor);
	return zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_view_from_parent(&budget_window_view, primary_delivery_budget, deferred_delivery_budget);
}

static struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view make_current_parent(
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_view delivery_parent,
	zigux_u32 delivery_window, zigux_u32 delivery_window_floor,
	zigux_u32 delivery_window_budget, zigux_u32 deferred_delivery_window_budget,
	zigux_u32 delivery_window_budget_window, zigux_u32 delivery_window_budget_window_floor,
	zigux_u32 delivery_window_budget_window_delivery_budget, zigux_u32 deferred_delivery_window_budget_window_delivery_budget,
	zigux_u32 delivery_window_budget_window_delivery_window, zigux_u32 delivery_window_budget_window_delivery_window_floor)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_view delivery_window_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_view_from_parent(&delivery_parent, delivery_window, delivery_window_floor);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_view delivery_window_budget_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_view_from_parent(&delivery_window_view, delivery_window_budget, deferred_delivery_window_budget);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_view delivery_window_budget_window_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_view_from_parent(&delivery_window_budget_view, delivery_window_budget_window, delivery_window_budget_window_floor);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_view delivery_window_budget_window_delivery_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_parent(&delivery_window_budget_window_view, delivery_window_budget_window_delivery_budget, deferred_delivery_window_budget_window_delivery_budget);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_view delivery_window_budget_window_delivery_window_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&delivery_window_budget_window_delivery_view, delivery_window_budget_window_delivery_window, delivery_window_budget_window_delivery_window_floor);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view current_parent_budget_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&delivery_window_budget_window_delivery_window_view, 3, 0);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_view current_parent_budget_window_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_view_from_parent(&current_parent_budget_view, delivery_window_budget_window, delivery_window_budget_window_floor);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view current_parent_delivery_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&current_parent_budget_window_view, 1, 0);

	return zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&current_parent_delivery_view, delivery_window_budget_window_delivery_window, delivery_window_budget_window_delivery_window_floor);
}

static struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_view make_parent(
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view current_parent,
	zigux_u32 delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget,
	zigux_u32 deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget,
	zigux_u32 delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window,
	zigux_u32 delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_floor)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view current_budget_view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&current_parent, delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget, deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget);

	return zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_view_from_parent(&current_budget_view, delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window, delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_floor);
}

int main(void)
{
	const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
	const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_view delivery_parent;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_view parent_base;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view parent_delivery;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view parent;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view view;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summary summary;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view empty = {0};

	printf("{\"constants\":{"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flag_budget_applied\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flag_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_used\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flag_deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_used\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flag_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_exhausted\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flag_deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_exhausted\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_none\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_acked\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_deferred\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_suppressed\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_coalesced\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_dropped\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_skipped\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status_held\":%u}",
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_USED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_USED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_HELD);

	printf(",\"acked\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_acked(words), 1, 0, 2, 1, 0, 0, 1, 1, 2, 0, 1, 0);
	parent_base = make_parent(make_current_parent(delivery_parent, 3, 0, 3, 0, 2, 0, 1, 0, 3, 0), 3, 0, 3, 0);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 3, 0);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 3, 0);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 3, 0);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"fallback_deferred\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_acked(words), 1, 0, 2, 1, 0, 0, 1, 1, 2, 0, 1, 0);
	parent_base = make_parent(make_current_parent(delivery_parent, 3, 0, 3, 0, 2, 0, 1, 0, 3, 0), 3, 0, 3, 0);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 3, 0);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 3, 0);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 0, 1);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"policy_deferred\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_acked(words), 1, 0, 2, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED, 1, 1, 2, 0, 1, 1);
	parent_base = make_parent(make_current_parent(delivery_parent, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1), 1, 1, 3, 0);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 1, 1);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 1, 1);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 1, 1);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"coalesced\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_coalesced(words), 1, 0, 2, 1, 0, 0, 1, 0, 2, 0, 1, 0);
	parent_base = make_parent(make_current_parent(delivery_parent, 3, 0, 3, 0, 2, 0, 1, 0, 3, 0), 3, 0, 3, 0);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 3, 0);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 3, 0);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 3, 0);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"held\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_acked(words), 1, 0, 1, 1, 1, 0, 1, 1, 2, 0, 1, 1);
	parent_base = make_parent(make_current_parent(delivery_parent, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 1, 1, 1, 1);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 1, 1);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 1, 1);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 1, 1);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"suppressed_held\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_acked(words), 1, 0, 1, 1, 1, ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD, 1, 1, 2, 0, 1, 1);
	parent_base = make_parent(make_current_parent(delivery_parent, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 1, 1, 1, 1);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 1, 1);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 1, 1);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 1, 1);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"dropped\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_dropped(words), 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0);
	parent_base = make_parent(make_current_parent(delivery_parent, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), 0, 0, 0, 0);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 0, 0);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 0, 0);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 0, 0);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"skipped\":{\"summary\":");
	delivery_parent = make_delivery_parent(make_parent_skipped(exhausted_words), 1, 1, 2, 2, 1, 0, 1, 1, 2, 0, 1, 1);
	parent_base = make_parent(make_current_parent(delivery_parent, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 1, 1, 1, 1);
	parent_delivery = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_view_from_parent(&parent_base, 1, 1);
	parent = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_view_from_parent(&parent_delivery, 1, 1);
	view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_parent(&parent, 1, 1);
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view);
	print_summary(&summary);
	printf("}");

	printf(",\"empty\":{\"is_valid\":%s,\"summary\":", zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_view_valid(&empty) ? "true" : "false");
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&empty);
	print_summary(&summary);
	printf("}}\n");
	return 0;
}

#include <stdint.h>
#include <stdio.h>

#include "../../../../include/zigux/list_hlist.h"

static int zigux_list_is_empty(const struct zigux_list_head *head)
{
    uintptr_t addr = (uintptr_t)head;
    return head->next == addr && head->prev == addr;
}

static size_t zigux_list_len(const struct zigux_list_head *head)
{
    size_t count = 0;
    const struct zigux_list_head *node;

    if (zigux_list_is_empty(head))
        return 0;

    node = (const struct zigux_list_head *)(uintptr_t)head->next;
    while (node != head) {
        count++;
        node = (const struct zigux_list_head *)(uintptr_t)node->next;
    }
    return count;
}

static int zigux_list_is_circular(const struct zigux_list_head *head)
{
    const struct zigux_list_head *first;
    const struct zigux_list_head *node;

    if (head->next == (uintptr_t)0 || head->prev == (uintptr_t)0)
        return 0;
    if (zigux_list_is_empty(head))
        return 1;

    first = (const struct zigux_list_head *)(uintptr_t)head->next;
    node = first;
    while (1) {
        const struct zigux_list_head *next =
            (const struct zigux_list_head *)(uintptr_t)node->next;
        const struct zigux_list_head *prev =
            (const struct zigux_list_head *)(uintptr_t)node->prev;
        if (!next || !prev)
            return 0;
        if (next->prev != (uintptr_t)node)
            return 0;
        if (prev->next != (uintptr_t)node)
            return 0;
        if (next == head)
            return head->prev == (uintptr_t)node &&
                   head->next == (uintptr_t)first;
        node = next;
    }
}

static int zigux_hlist_is_empty(const struct zigux_hlist_head *head)
{
    return head->first == (uintptr_t)0;
}

static size_t zigux_hlist_len(const struct zigux_hlist_head *head)
{
    size_t count = 0;
    const struct zigux_hlist_node *node =
        (const struct zigux_hlist_node *)(uintptr_t)head->first;

    while (node) {
        count++;
        node = (const struct zigux_hlist_node *)(uintptr_t)node->next;
    }
    return count;
}

static int zigux_hlist_head_links_match(const struct zigux_hlist_head *head)
{
    const struct zigux_hlist_node *node;
    uintptr_t expected_pprev;

    if (zigux_hlist_is_empty(head))
        return 1;

    expected_pprev = (uintptr_t)&head->first;
    node = (const struct zigux_hlist_node *)(uintptr_t)head->first;
    while (node) {
        if (node->pprev != expected_pprev)
            return 0;
        expected_pprev = (uintptr_t)&node->next;
        node = (const struct zigux_hlist_node *)(uintptr_t)node->next;
    }
    return 1;
}

static int zigux_hlist_tail_next_null(const struct zigux_hlist_head *head)
{
    const struct zigux_hlist_node *node =
        (const struct zigux_hlist_node *)(uintptr_t)head->first;

    if (!node)
        return 1;
    while (node->next != (uintptr_t)0)
        node = (const struct zigux_hlist_node *)(uintptr_t)node->next;
    return node->next == (uintptr_t)0;
}

int main(void)
{
    struct zigux_list_head empty_list_head = zigux_list_head_empty();
    struct zigux_list_head list_head = zigux_list_head_empty();
    struct zigux_list_head list_first = zigux_list_head_empty();
    struct zigux_list_head list_second = zigux_list_head_empty();
    struct zigux_hlist_head empty_hlist_head = zigux_hlist_head_empty();
    struct zigux_hlist_head hlist_head = zigux_hlist_head_empty();
    struct zigux_hlist_node hlist_first = zigux_hlist_node_empty();
    struct zigux_hlist_node hlist_second = zigux_hlist_node_empty();

    empty_list_head.next = (uintptr_t)&empty_list_head;
    empty_list_head.prev = (uintptr_t)&empty_list_head;

    list_head.next = (uintptr_t)&list_first;
    list_head.prev = (uintptr_t)&list_second;
    list_first.next = (uintptr_t)&list_second;
    list_first.prev = (uintptr_t)&list_head;
    list_second.next = (uintptr_t)&list_head;
    list_second.prev = (uintptr_t)&list_first;

    hlist_head.first = (uintptr_t)&hlist_first;
    hlist_first.next = (uintptr_t)&hlist_second;
    hlist_first.pprev = (uintptr_t)&hlist_head.first;
    hlist_second.next = (uintptr_t)0;
    hlist_second.pprev = (uintptr_t)&hlist_first.next;

    printf(
        "{"
        "\"list_empty\":{\"empty\":%s,\"len\":%zu,\"circular\":%s,\"head_links_match\":%s},"
        "\"list_pair\":{\"empty\":%s,\"len\":%zu,\"circular\":%s,\"head_links_match\":%s},"
        "\"hlist_empty\":{\"empty\":%s,\"len\":%zu,\"head_links_match\":%s,\"tail_next_null\":%s},"
        "\"hlist_pair\":{\"empty\":%s,\"len\":%zu,\"head_links_match\":%s,\"tail_next_null\":%s}"
        "}\n",
        zigux_list_is_empty(&empty_list_head) ? "true" : "false",
        zigux_list_len(&empty_list_head),
        zigux_list_is_circular(&empty_list_head) ? "true" : "false",
        (empty_list_head.next == (uintptr_t)&empty_list_head &&
         empty_list_head.prev == (uintptr_t)&empty_list_head) ? "true" : "false",
        zigux_list_is_empty(&list_head) ? "true" : "false",
        zigux_list_len(&list_head),
        zigux_list_is_circular(&list_head) ? "true" : "false",
        (list_head.next == (uintptr_t)&list_first &&
         list_head.prev == (uintptr_t)&list_second) ? "true" : "false",
        zigux_hlist_is_empty(&empty_hlist_head) ? "true" : "false",
        zigux_hlist_len(&empty_hlist_head),
        zigux_hlist_head_links_match(&empty_hlist_head) ? "true" : "false",
        zigux_hlist_tail_next_null(&empty_hlist_head) ? "true" : "false",
        zigux_hlist_is_empty(&hlist_head) ? "true" : "false",
        zigux_hlist_len(&hlist_head),
        zigux_hlist_head_links_match(&hlist_head) ? "true" : "false",
        zigux_hlist_tail_next_null(&hlist_head) ? "true" : "false");
    return 0;
}

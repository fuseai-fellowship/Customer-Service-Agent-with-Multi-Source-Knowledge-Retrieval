import json
from collections import defaultdict

def compact_menu_summary(tool_content, max_items_shown=7):
    """
    Summarize menu_tool JSON output:
    - If <= max_items_shown, return raw content.
    - If > max_items_shown, group by category and list names.
    Returns (summary_text, overflow_flag)
    """
    try:
        items = json.loads(tool_content)
    except Exception:
        return tool_content, False  # fallback

    total_items = len(items)
    
    if total_items <= max_items_shown:
        return tool_content, False  # small, keep as-is

    # group by category
    grouped = defaultdict(list)
    for item in items:
        cat = item.get("category_name") or "Other"
        grouped[cat].append(item.get("name", "item"))

    summary_lines = [f"{cat}: {', '.join(names)}" for cat, names in grouped.items()]
    summary_lines.append("Above is the data received from menu_tool call applying user's preferences.")
    return "\n".join(summary_lines), True

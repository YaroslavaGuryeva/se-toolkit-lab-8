"""Pure formatting functions for LMS data — no I/O, no async."""

from lms_common.models import HealthResult, Item, PassRate


def format_health(result: HealthResult) -> str:
    if result.status == "healthy":
        return f"✅ Backend is healthy. {result.item_count} items available."
    return f"❌ Backend error: {result.error or 'Unknown'}"


def format_labs(items: list[Item]) -> str:
    labs = sorted(
        [i for i in items if i.type == "lab"],
        key=lambda x: str(x.id),
    )
    if not labs:
        return "📭 No labs available."
    text = "📚 Available labs:\n\n"
    text += "\n".join(f"• {lab.title}" for lab in labs)
    return text


def format_scores(lab: str, rates: list[PassRate]) -> str:
    if not rates:
        return f"📭 No scores found for {lab}."
    text = f"📊 Pass rates for {lab}:\n\n"
    text += "\n".join(
        f"• {r.task}: {r.avg_score:.1f}% ({r.attempts} attempts)" for r in rates
    )
    return text

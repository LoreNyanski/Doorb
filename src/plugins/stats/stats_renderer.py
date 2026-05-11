import asyncio

from .stats_fetcher import StatResult, LeaderboardResult


async def render_leaderboard(entries: LeaderboardResult, get_user):
    return await leaderboard_plaintext(entries, get_user) # TODO replace later with embed

async def render_stats(entries: StatResult, subject):
    return await stats_plaintext(entries, subject) # TODO replace later with embed




async def leaderboard_plaintext(data: LeaderboardResult, get_user) -> str:
    user_cache = await asyncio.gather(*(get_user(entry.dumbass_id) for entry in data.entries))
    formatted_value_cache = [entry.formatted for entry in data.entries]

    counter_len = len(str(len(data.entries)))
    left_len = max(len(x) for x in user_cache)
    right_len = max(len(x) for x in formatted_value_cache)

    lines = []
    for i in range(len(data.entries)):
        lines.append(f"#{(i+1):<{counter_len}}  {user_cache[i]:<{left_len}}  {formatted_value_cache[i]:>{right_len}}")
    textbox = f"```\n{'\n'.join(lines)}\n```"
    label = f"Ranking for {data.label} (and bisches):\n"
    return f"{label}{textbox}"


async def stats_plaintext(data: StatResult, subject):
    left_len = 0
    right_len = 0
    for group in data.groups:
        for item in group.items:
            left_len = max(left_len, len(item.label))
            right_len = max(right_len, len(item.formatted))

    pages = []
    for group in data.groups:
        group_header = f"{group.label}:"
        lines = [group_header]
        for item in group.items:
            label = f'{item.label}:'
            lines.append(f"  {label:<{left_len+1}}  {item.formatted:>{right_len}}")
        pages.append("\n".join(lines))
    textbox = f"```\n{'\n\n'.join(pages)}\n```"
    label = f"{subject}'s stats (point at them and laugh):"
    return f"{label}{textbox}"
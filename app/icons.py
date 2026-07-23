from markupsafe import Markup, escape

from app import wiki_icons

SKILL_ICONS = {
    "Overall": "🏆",
    "Attack": "⚔️",
    "Defence": "🛡️",
    "Strength": "💪",
    "Constitution": "❤️",
    "Hitpoints": "❤️",
    "Ranged": "🏹",
    "Prayer": "✨",
    "Magic": "🔮",
    "Cooking": "🍳",
    "Woodcutting": "🪓",
    "Fletching": "🪶",
    "Fishing": "🎣",
    "Firemaking": "🔥",
    "Crafting": "🧵",
    "Smithing": "🔨",
    "Mining": "⛏️",
    "Herblore": "🧪",
    "Agility": "🏃",
    "Thieving": "🗝️",
    "Slayer": "💀",
    "Farming": "🌾",
    "Runecrafting": "🔯",
    "Runecraft": "🔯",
    "Hunter": "🐾",
    "Construction": "🏰",
    "Summoning": "🐉",
    "Dungeoneering": "🕸️",
    "Divination": "🌟",
    "Invention": "⚙️",
    "Archaeology": "🏺",
    "Necromancy": "☠️",
}

DEFAULT_SKILL_ICON = "🔸"

# Wiki file naming is a solid, verified convention for skills: "<Skill> icon highscores.png",
# except Overall which lives under a different name.
SKILL_ICON_OVERRIDES = {
    "Overall": ["Stats Overall icon highscores.png"],
    # the live hiscores API uses RS3's current skill names, but the wiki still files
    # these two icons under the older names
    "Hitpoints": ["Constitution icon highscores.png"],
    "Runecraft": ["Runecrafting icon highscores.png"],
}


def skill_icon_candidates(name: str) -> list[str]:
    return SKILL_ICON_OVERRIDES.get(name, [f"{name} icon highscores.png"])


def _img(url: str, alt: str) -> Markup:
    return Markup(f'<img class="icon" src="{escape(url)}" alt="{escape(alt)}">')


def skill_icon(name: str):
    url = wiki_icons.get_cached("skill", name)
    if url:
        return _img(url, name)
    return SKILL_ICONS.get(name, DEFAULT_SKILL_ICON)


FEED_ICONS = {
    "drop": "💰",
    "boss_kill": "⚔️",
    "quest": "📯",
    "xp_milestone": "📈",
    "other": "📝",
}


def feed_icon(event_type: str) -> str:
    return FEED_ICONS.get(event_type, "📝")


TASK_ICONS = {
    "daily challenges": "✅",
    "pof": "🌾",
    "player owned farm": "🌾",
    "player owned ports": "⚓",
    "old man potato cactus": "🥔",
    "shop run: meat": "🥩",
    "shop run: runes": "🔮",
    "tears of guthix": "💧",
    "herby werby": "🧪",
    "pineapple runs": "🍍",
    "managing misc": "🏰",
    "managing miscellania": "🏰",
}

DEFAULT_TASK_ICON = {"daily": "📅", "weekly": "🗓️"}

# Hand-picked, verified wiki filenames for the seeded tasks — only added where a
# confident exact match was checked. Everything else just tries the generic pattern
# and falls back to emoji rather than risk showing a wrong/misleading icon.
# (Daily Challenges intentionally excluded: the real wiki icon is a round badge that
# sits too close visually to the round toggle button next to it — the emoji reads better.)
TASK_ICON_OVERRIDES = {}


def task_icon_candidates(name: str) -> list[str]:
    lowered = name.lower()
    for key, candidates in TASK_ICON_OVERRIDES.items():
        if key in lowered:
            return candidates
    return [f"{name} icon.png"]


def task_icon(name: str, category: str = "weekly"):
    url = wiki_icons.get_cached("task", name)
    if url:
        return _img(url, name)
    lowered = name.lower()
    for key, icon in TASK_ICONS.items():
        if key in lowered:
            return icon
    return DEFAULT_TASK_ICON.get(category, "🔸")


def activity_icon_candidates(name: str) -> list[str]:
    return [f"{name} icon.png", f"{name} icon highscores.png"]


def activity_icon(name: str):
    url = wiki_icons.get_cached("activity", name)
    if url:
        return _img(url, name)
    lowered = name.lower()
    if "clue" in lowered:
        return "📜"
    if "runescore" in lowered:
        return "⭐"
    if "bounty" in lowered or "duel" in lowered or "pvp" in lowered:
        return "⚔️"
    return "💀"

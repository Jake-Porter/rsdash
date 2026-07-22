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


def skill_icon(name: str) -> str:
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


def task_icon(name: str, category: str = "weekly") -> str:
    lowered = name.lower()
    for key, icon in TASK_ICONS.items():
        if key in lowered:
            return icon
    return DEFAULT_TASK_ICON.get(category, "🔸")


def activity_icon(name: str) -> str:
    lowered = name.lower()
    if "clue" in lowered:
        return "📜"
    if "runescore" in lowered:
        return "⭐"
    if "bounty" in lowered or "duel" in lowered or "pvp" in lowered:
        return "⚔️"
    return "💀"

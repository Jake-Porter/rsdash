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


def activity_icon(name: str) -> str:
    lowered = name.lower()
    if "clue" in lowered:
        return "📜"
    if "runescore" in lowered:
        return "⭐"
    if "bounty" in lowered or "duel" in lowered or "pvp" in lowered:
        return "⚔️"
    return "💀"

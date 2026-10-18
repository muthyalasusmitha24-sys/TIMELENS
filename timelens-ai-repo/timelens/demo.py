"""Offline demo data so the app is fully explorable without an API key."""
DEMO_ANALYSIS = {
    "identified": True,
    "name": "Chola Bronze Nataraja (Shiva as Lord of the Dance)",
    "category": "sculpture",
    "confidence": 0.9,
    "period": {"label": "Chola period", "start_year": 900, "end_year": 1200},
    "civilization": "Chola dynasty, Tamil South India",
    "origin": {"place": "Thanjavur region, Tamil Nadu", "country": "India", "lat": 10.787, "lon": 79.139},
    "material": "Bronze, lost-wax (cire perdue) casting",
    "style": "Chola bronze tradition",
    "significance": "Iconic synthesis of Shaiva philosophy: cosmic creation, preservation and destruction in a single dancing form.",
    "narrative": "This is the Nataraja, Shiva dancing the cosmic dance within a ring of flames. Cast by hereditary sthapati artisans using the lost-wax method, such bronzes were made as processional images carried out of temples at festivals under Chola patronage. The raised drum stands for creation, the flame for destruction, the lowered hand for refuge, and the figure tramples the dwarf of ignorance.",
    "evidence": [
        "Four-armed dancing posture with one leg raised (ananda tandava)",
        "Circular flaming aureole (prabha mandala) around the figure",
        "Matted locks flaring outward, with Ganga figure in the hair",
        "Dwarf Apasmara beneath the right foot",
        "Smooth, elongated modelling typical of Chola bronzes",
    ],
    "inscription": {"present": False, "script": "", "transcription": "", "translation": "", "notes": "No legible inscription visible."},
    "timeline": [
        {"year": 300, "event": "Early Chola kings mentioned in Sangam literature", "kind": "dynasty"},
        {"year": 850, "event": "Vijayalaya Chola captures Thanjavur; Imperial Chola rise", "kind": "dynasty"},
        {"year": 1010, "event": "Brihadisvara Temple completed under Rajaraja I", "kind": "architecture"},
        {"year": 1050, "event": "Peak of Chola bronze casting", "kind": "object"},
        {"year": 1070, "event": "Chola maritime expeditions to Southeast Asia", "kind": "trade"},
        {"year": 1279, "event": "End of Chola power", "kind": "dynasty"},
    ],
    "map_points": [
        {"name": "Thanjavur", "lat": 10.787, "lon": 79.139, "role": "Chola capital / likely origin"},
        {"name": "Chidambaram", "lat": 11.399, "lon": 79.693, "role": "Famed Nataraja temple"},
        {"name": "Srivijaya (Sumatra)", "lat": -2.99, "lon": 104.76, "role": "Trade and naval contact"},
        {"name": "Angkor", "lat": 13.436, "lon": 103.86, "role": "Shaiva cultural exchange"},
    ],
    "graph": {
        "nodes": [
            {"id": "Nataraja bronze", "group": "object"}, {"id": "Chola dynasty", "group": "dynasty"},
            {"id": "Shaivism", "group": "religion"}, {"id": "Brihadisvara Temple", "group": "architecture"},
            {"id": "Lost-wax casting", "group": "technique"}, {"id": "Srivijaya trade", "group": "trade"},
            {"id": "Rajaraja I", "group": "person"},
        ],
        "edges": [
            {"source": "Chola dynasty", "target": "Nataraja bronze", "label": "patronised"},
            {"source": "Nataraja bronze", "target": "Shaivism", "label": "embodies"},
            {"source": "Rajaraja I", "target": "Brihadisvara Temple", "label": "built"},
            {"source": "Brihadisvara Temple", "target": "Nataraja bronze", "label": "housed bronzes like"},
            {"source": "Nataraja bronze", "target": "Lost-wax casting", "label": "made by"},
            {"source": "Chola dynasty", "target": "Srivijaya trade", "label": "maritime links"},
        ],
    },
    "connections": [
        "Bronze icons spread Chola religious imagery across Southeast Asia via maritime trade.",
        "The Nataraja motif links Tamil bhakti poetry to temple sculpture.",
    ],
    "search_terms": ["Nataraja", "Shiva bronze", "Chola"],
    "uncertainties": ["DEMO MODE: this is sample data, not an analysis of your uploaded image."],
}

DEMO_CHAT = ("(Demo mode) I'm answering from built-in sample data about the Chola Nataraja. "
             "Add an Anthropic API key in the sidebar to get real, image-grounded answers.")

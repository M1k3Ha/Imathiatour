import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "seed.json"

TEAM_MEMBERS = [
    {"full_name": "ΤΟ ΟΝΟΜΑ ΣΟΥ", "am": "ΤΟ ΑΜ ΣΟΥ"},
]

with open(SEED_PATH, "r", encoding="utf-8") as f:
    seed = json.load(f)

# Κατηγορίες
CATEGORIES = [
    {"id": c["id"], "title": c["name"]}
    for c in seed["categories"]
]

# Λεξικό POIs από το seed (key = poiId)
SEED_POIS = seed["pois"]

# POIs ανά κατηγορία (κρατάμε ΜΟΝΟ τα πρώτα 5 όπως απαιτεί η εκφώνηση)
# POIS[category_id] = [{"id": "...", "wikidata": "Q..."}]
POIS = {}
for cat in seed["categories"]:
    cid = cat["id"]
    POIS[cid] = []
    for poi_key in cat["poiIds"][:5]:
        poi = SEED_POIS.get(poi_key)
        if not poi:
            continue
        POIS[cid].append({
            "id": poi["id"],
            "name": poi.get("name"),
            "wikidata": poi.get("wikidataQid"),
        })

# (προαιρετικά) extra εικόνες ώστε να έχεις >=3 στο details πάντα
EXTRA_IMAGES = [
    "https://picsum.photos/seed/poi1/1000/700",
    "https://picsum.photos/seed/poi2/1000/700",
    "https://picsum.photos/seed/poi3/1000/700",
]

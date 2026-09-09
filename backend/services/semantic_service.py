import re
from services.db_service import search_change_records

VALID_LOCALITIES = [
    "narela", "alipur", "civil lines", "rohini", "model town",
    "chandni chowk", "karol bagh", "connaught place", "punjabi bagh",
    "paschim vihar", "janakpuri", "dwarka", "najafgarh", "saket",
    "vasant kunj", "mehrauli", "hauz khas", "defence colony",
    "kalkaji", "okhla", "sarita vihar", "mayur vihar", "shahdara",
    "yamuna vihar"
]

CATEGORY_MAPPINGS = {
    "building": "New Buildings",
    "buildings": "New Buildings",
    "construction": "New Buildings",
    "road": "New Roads",
    "roads": "New Roads",
    "infrastructure": "New Roads",
    "vegetation": "Vegetation Change",
    "green": "Vegetation Change",
    "tree": "Vegetation Change",
    "trees": "Vegetation Change",
    "water": "Water Body Change",
    "lake": "Water Body Change",
    "river": "Water Body Change",
    "agricultural": "Agricultural / Land-use Change",
    "agriculture": "Agricultural / Land-use Change",
    "farm": "Agricultural / Land-use Change",
    "farming": "Agricultural / Land-use Change"
}

_semantic_model = None
_model_attempted = False


def ensure_semantic_model_loaded():
    global _semantic_model, _model_attempted
    if _model_attempted:
        return _semantic_model
    _model_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        print(f"MiniLM model lazy load status: {e}")
        _semantic_model = None
    return _semantic_model


def parse_query_entities(query: str):
    q_lower = query.lower()
    
    # 1. Place extraction
    detected_place = "Delhi"
    for loc in VALID_LOCALITIES:
        if loc in q_lower:
            detected_place = loc.title()
            break
            
    # 2. Year range extraction
    years = [int(y) for y in re.findall(r"\b(202[0-6])\b", query)]
    year_from = None
    year_to = None
    if len(years) >= 2:
        year_from = min(years)
        year_to = max(years)
    elif len(years) == 1:
        year_from = years[0]
        year_to = 2026

    # 3. Category extraction
    detected_category = None
    for kw, cat in CATEGORY_MAPPINGS.items():
        if kw in q_lower:
            detected_category = cat
            break

    return detected_place, year_from, year_to, detected_category


def semantic_search(query: str, top_k: int = 50):
    place, year_from, year_to, category = parse_query_entities(query)
    
    res = search_change_records(
        place=place,
        year_from=year_from,
        year_to=year_to,
        category=category,
        limit=top_k
    )

    # Optional MiniLM score ranking enhancement
    model = ensure_semantic_model_loaded()
    features = res.get("features", [])
    
    if model and features:
        try:
            query_emb = model.encode(query, convert_to_numpy=True)
            for f in features:
                props = f["properties"]
                desc = f"{props.get('category')} in {props.get('locality')} from {props.get('year_from')} to {props.get('year_to')}"
                desc_emb = model.encode(desc, convert_to_numpy=True)
                score = float(np.dot(query_emb, desc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(desc_emb) + 1e-6))
                props["similarity_score"] = round(score, 3)
        except Exception:
            pass

    return {
        "status": res.get("status", "success"),
        "query": query,
        "parsed_intent": {
            "place": place,
            "year_from": year_from,
            "year_to": year_to,
            "category": category
        },
        "count": res.get("count", 0),
        "total_area_km2": res.get("total_area_km2", 0.0),
        "results": features[:top_k]
    }


def search_real_satellite_data(query: str):
    return semantic_search(query=query, top_k=20)
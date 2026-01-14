from fastapi import FastAPI, Header, HTTPException
from typing import Optional

from .models import (
    AboutMember, LoginRequest, RefreshRequest, TokenResponse,
    CategoryOut, PoiListItem, PoiDetails
)
from .data import TEAM_MEMBERS, CATEGORIES, POIS, EXTRA_IMAGES
from .auth import (
    verify_user, create_access_token, create_refresh_token,
    decode_token, require_access_token,
)
from .wikidata import fetch_wikidata_entity, parse_poi_from_wikidata

app = FastAPI(title="Imathiatour API", version="1.0.0")


# ---------------- About ----------------
@app.get("/about", response_model=list[AboutMember])
def about():
    return TEAM_MEMBERS


# ---------------- Auth ----------------
@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    if not verify_user(payload.email, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(payload.email)
    refresh = create_refresh_token(payload.email)
    return TokenResponse(access_token=access, refresh_token=refresh)


@app.post("/api/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")
    sub = data.get("sub")
    access = create_access_token(sub)
    new_refresh = create_refresh_token(sub)
    return TokenResponse(access_token=access, refresh_token=new_refresh)


# ---------------- POIs ----------------
def _require_auth(authorization: Optional[str]) -> str:
    return require_access_token(authorization)


def _category_title(cid: str) -> str:
    for c in CATEGORIES:
        if c["id"] == cid:
            return c["title"]
    return cid


@app.get("/pois/categories", response_model=list[CategoryOut])
def list_categories(authorization: Optional[str] = Header(default=None)):
    _require_auth(authorization)
    out = []
    for c in CATEGORIES:
        cid = c["id"]
        count = len(POIS.get(cid, []))
        out.append(CategoryOut(id=cid, title=c["title"], count=count))
    return out


@app.get("/pois/categories/{id}", response_model=list[PoiListItem])
def list_pois_for_category(id: str, authorization: Optional[str] = Header(default=None)):
    _require_auth(authorization)
    if id not in POIS:
        raise HTTPException(status_code=404, detail="Category not found")

    items = []
    for p in POIS[id]:
        qid = p.get("wikidata")
        if not qid:
            continue
        raw = fetch_wikidata_entity(qid)
        parsed = parse_poi_from_wikidata(qid, raw)
        items.append(PoiListItem(
            id=p["id"],
            title=parsed["title"],
            lat=parsed["lat"],
            lon=parsed["lon"],
            image=parsed["image"],
            short=parsed["short"],
        ))
    return items


@app.get("/pois/{id}", response_model=PoiDetails)
def get_poi(id: str, authorization: Optional[str] = Header(default=None)):
    _require_auth(authorization)

    # Find poi in any category
    found = None
    found_cat = None
    for cid, arr in POIS.items():
        for p in arr:
            if p["id"] == id:
                found = p
                found_cat = cid
                break
        if found:
            break

    if not found or not found_cat:
        raise HTTPException(status_code=404, detail="POI not found")

    qid = found.get("wikidata")
    if not qid:
        raise HTTPException(status_code=400, detail="POI missing wikidataQid")

    raw = fetch_wikidata_entity(qid)
    parsed = parse_poi_from_wikidata(qid, raw)

    # images: 1st from P18, then extras so we always have >=3
    images = []
    if parsed["image"]:
        images.append(parsed["image"])
    images.extend(EXTRA_IMAGES)
    images = images[:3]  # κρατάμε 3 για αρχή

    return PoiDetails(
        id=id,
        category_id=found_cat,
        category_title=_category_title(found_cat),
        title=parsed["title"],
        short=parsed["short"],
        lat=parsed["lat"],
        lon=parsed["lon"],
        wikipedia_url=parsed["wikipedia_url"],
        images=images,
        description=None,
    )

import time
from threading import Thread

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.base import keyword_index_collection, things_collection
from backend.config import FRONTEND_DIR, FRONTEND_ORIGINS, HOME_PAGE
from backend.routers.main_auth import auth_router, extract_bearer_token, get_role_from_token
from backend.routers.main_borrow import borrow_router
from backend.routers.main_crud import crud_router
from backend.routers.main_devices import devices_router
from backend.routers.main_localisation import canonical_room_name, coords_from_room, localisation_router
from backend.routers.main_notifications import notifications_router
from backend.routers.main_recherche import recherche_router
from backend.routers.main_stats import stats_router
from backend.routers.main_wot import wot_router


app = FastAPI(title="IntelliBuild")
cleanup_thread: Thread | None = None
ADMIN_FRONTEND_PAGES = {
    "index.html",
    "ajouter-objet.html",
    "objets.html",
    "localisations.html",
    "parametres.html",
    "admin-users.html",
    "notifications-admin.html",
}


def _cleanup_orphan_keywords_on_startup() -> None:
    """Nettoie automatiquement les mots-cles orphelins au demarrage."""
    try:
        all_keyword_thing_ids = list(keyword_index_collection.distinct("thingId"))
        orphan_thing_ids = []

        for thing_id in all_keyword_thing_ids:
            thing_id_clean = str(thing_id).strip()
            if not things_collection.find_one({"id": thing_id_clean}):
                orphan_thing_ids.append(thing_id_clean)

        if orphan_thing_ids:
            result = keyword_index_collection.delete_many({"thingId": {"$in": orphan_thing_ids}})
            print(f"Startup cleanup: {result.deleted_count} orphan keywords removed")
    except Exception as exc:
        print(f"Startup cleanup failed: {exc}")


def _initialize_view_counts_on_startup() -> None:
    """Initialise les compteurs de vues pour tous les objets."""
    try:
        result = things_collection.update_many(
            {"view_count": {"$exists": False}},
            {"$set": {"view_count": 0}},
        )
        if result.modified_count > 0:
            print(f"Startup init: {result.modified_count} objects received view_count")
    except Exception as exc:
        print(f"View count init failed: {exc}")


def _normalize_rooms_on_startup() -> None:
    """Harmonise les noms de salles existants dans la base (room/name + coords)."""
    try:
        rows = list(things_collection.find({}))
        updated = 0

        for row in rows:
            loc = row.get("location") if isinstance(row.get("location"), dict) else {}
            raw_room = str(loc.get("room") or loc.get("name") or "").strip()
            if not raw_room:
                continue

            canonical = canonical_room_name(raw_room)
            coords = coords_from_room(canonical)
            needs_update = (
                str(loc.get("room") or "").strip() != canonical
                or str(loc.get("name") or "").strip() != canonical
                or float(loc.get("x", 0.0) or 0.0) != float(coords["x"])
                or float(loc.get("y", 0.0) or 0.0) != float(coords["y"])
                or float(loc.get("z", 0.0) or 0.0) != float(coords["z"])
            )

            if not needs_update:
                continue

            new_loc = dict(loc)
            new_loc["room"] = canonical
            new_loc["name"] = canonical
            if (coords["x"], coords["y"], coords["z"]) != (0.0, 0.0, 0.0):
                new_loc["x"] = coords["x"]
                new_loc["y"] = coords["y"]
                new_loc["z"] = coords["z"]

            things_collection.update_one(
                {"_id": row.get("_id")},
                {"$set": {"location": new_loc}},
            )
            updated += 1

        if updated > 0:
            print(f"Startup room normalization: {updated} objects updated")
    except Exception as exc:
        print(f"Room normalization failed: {exc}")


def _background_cleanup_task() -> None:
    """Nettoie les mots-cles orphelins periodiquement."""
    while True:
        try:
            time.sleep(300)
            all_keyword_thing_ids = list(keyword_index_collection.distinct("thingId"))
            orphan_thing_ids = []

            for thing_id in all_keyword_thing_ids:
                thing_id_clean = str(thing_id).strip()
                if not things_collection.find_one({"id": thing_id_clean}):
                    orphan_thing_ids.append(thing_id_clean)

            if orphan_thing_ids:
                result = keyword_index_collection.delete_many({"thingId": {"$in": orphan_thing_ids}})
                print(f"Background cleanup: {result.deleted_count} orphan keywords removed")
        except Exception as exc:
            print(f"Background cleanup failed: {exc}")


def _start_cleanup_thread() -> None:
    global cleanup_thread
    if cleanup_thread is not None and cleanup_thread.is_alive():
        return

    cleanup_thread = Thread(target=_background_cleanup_task, daemon=True, name="keyword-cleanup")
    cleanup_thread.start()


def _serve_admin_page(request: Request, filename: str):
    token = extract_bearer_token(request)
    if not token:
        return RedirectResponse(url="/login.html", status_code=302)

    try:
        role = get_role_from_token(token).strip().lower()
    except HTTPException:
        return RedirectResponse(url="/login.html", status_code=302)

    if role != "admin":
        return RedirectResponse(url="/user.html", status_code=302)

    file_path = FRONTEND_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page introuvable")


app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(localisation_router)
app.include_router(recherche_router)
app.include_router(auth_router)
app.include_router(borrow_router)
app.include_router(crud_router)
app.include_router(notifications_router)
app.include_router(devices_router)
app.include_router(stats_router)
app.include_router(wot_router)


@app.on_event("startup")
def on_startup() -> None:
    _cleanup_orphan_keywords_on_startup()
    _initialize_view_counts_on_startup()
    _normalize_rooms_on_startup()
    _start_cleanup_thread()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "intellibuild"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    favicon_path = FRONTEND_DIR / "intellibuild-mark.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Favicon introuvable")


@app.get("/index.html", include_in_schema=False)
def admin_index_page(request: Request):
    return _serve_admin_page(request, "index.html")


@app.get("/ajouter-objet.html", include_in_schema=False)
def admin_add_object_page(request: Request):
    return _serve_admin_page(request, "ajouter-objet.html")


@app.get("/objets.html", include_in_schema=False)
def admin_objects_page(request: Request):
    return _serve_admin_page(request, "objets.html")


@app.get("/localisations.html", include_in_schema=False)
def admin_localisations_page(request: Request):
    return _serve_admin_page(request, "localisations.html")


@app.get("/parametres.html", include_in_schema=False)
def admin_settings_page(request: Request):
    return _serve_admin_page(request, "parametres.html")


@app.get("/admin-users.html", include_in_schema=False)
def admin_users_page(request: Request):
    return _serve_admin_page(request, "admin-users.html")


@app.get("/notifications-admin.html", include_in_schema=False)
def admin_notifications_page(request: Request):
    return _serve_admin_page(request, "notifications-admin.html")


@app.get("/", include_in_schema=False)
def frontend_home():
    if HOME_PAGE.exists():
        return FileResponse(HOME_PAGE)
    return {"message": "API is running"}


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

from pymongo import MongoClient

MONGO_URI = "mongodb+srv://admin:hadjer2005@smart-building.9v6qqdu.mongodb.net/?appName=smart-building"

client = MongoClient(MONGO_URI)
db = client["smart_building"]

things = db["things"]

TARGET_POS = {"x": 60, "y": 50, "z": 8}


# =========================
# 1. DELETE Archives E2
# =========================

delete_result = things.delete_many({
    "location.Archives E2": TARGET_POS
})

print(f"🗑️ Archives E2 supprimés: {delete_result.deleted_count}")


# =========================
# 2. UPDATE Bureau Com
# =========================

update_result = things.update_many(
    {"location.room": "Bureau Com"},
    {
        "$set": {
            "location.x": 60,
            "location.y": 50,
            "location.z": 8
        }
    }
)

print(f"✏️ Bureau Com modifiés: {update_result.modified_count}")
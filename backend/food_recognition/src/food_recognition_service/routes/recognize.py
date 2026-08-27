from fastapi import APIRouter, UploadFile, File, HTTPException, Form
try:
    from ..schemas import RecognitionResponse
    from ..vision_engine import analyze_image
except Exception:
    from food_recognition_service.schemas import RecognitionResponse
    from food_recognition_service.vision_engine import analyze_image

router = APIRouter()


@router.post("/analyze", response_model=RecognitionResponse)
async def analyze_food_photo(
    file: UploadFile = File(..., description="Food image to analyze (JPEG/PNG)"),
    user_region: str = Form(default="india", description="User's region for cuisine context"),
    auto_log: bool = Form(default=False, description="Automatically log to daily diary"),
):
    """
    Upload a food photo → AI identifies items → returns nutritional breakdown.
    
    - Uses local **llava** vision model via Ollama (no cloud API calls)
    - Enriched with IFCT/NIN data for Indian foods
    - FSSAI / ICMR-NIN compliance warnings included
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, or WebP images are supported.")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Image too large. Maximum size is 10MB.")

    result = await analyze_image(image_bytes, user_region=user_region)
    result.logged_to_diary = auto_log

    return result


@router.get("/foods/search")
async def search_food_database(q: str, limit: int = 10):
    """
    Text-search the food database (for manual food logging as an alternative to photo).
    """
    from ..vision_engine import FOOD_DB
    query = q.lower()
    matches = [
        item.model_dump() for key, item in FOOD_DB.items()
        if query in key or query in item.name.lower()
    ]
    return {"results": matches[:limit], "total": len(matches)}

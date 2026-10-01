from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/v1/stub")
def stub() -> dict[str, str]:
    return {"status": "scaffold"}

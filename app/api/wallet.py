from fastapi import APIRouter

router = APIRouter(
    prefix="/wallets",
    tags=["wallets"]
)

@router.post("/transfer")
async def transfer():
    return {
        "message": "Transfer funds"
    }
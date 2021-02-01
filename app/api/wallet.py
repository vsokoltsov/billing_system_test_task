from fastapi import APIRouter, HTTPException, status

from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import UserResponse
from app.schemas.wallet import WalletTransferParams

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("/transfer", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def transfer(params: WalletTransferParams):
    """ Handler for routing of funds from one wallet to another. """

    wallet_id = await Wallet.transfer(
        params.wallet_from, params.wallet_to, params.amount
    )
    user = await User.get_by_wallet_id(wallet_id)
    if not user:
        raise HTTPException(404, detail="User does not exists")
    return UserResponse(**user).dict()

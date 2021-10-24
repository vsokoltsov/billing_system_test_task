from fastapi import APIRouter, HTTPException, Request, status

from app.entities.user import User, UserDoesNotExist
from app.entities.wallet import WalletDoesNotExist, WalletTransferParams
from app.usecases.wallet import WalletUsecase

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("/transfer", response_model=User, status_code=status.HTTP_200_OK)
async def transfer(request: Request, params: WalletTransferParams):
    """Handler for routing of funds from one wallet to another."""

    try:
        usecase: WalletUsecase = request.app.state.wallet_usecase
        user = await usecase.transfer(
            source_wallet_id=params.wallet_from,
            destination_wallet_id=params.wallet_to,
            amount=params.amount,
        )
        return user
    except UserDoesNotExist as user_not_exist:
        raise HTTPException(
            status_code=404,
            detail=f"User does not exists. Full error: {user_not_exist}",
        ) from user_not_exist
    except WalletDoesNotExist as wallet_not_exist:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet does not exists. Full error: {wallet_not_exist}",
        ) from wallet_not_exist
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

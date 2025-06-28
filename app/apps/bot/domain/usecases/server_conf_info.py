from typing import Optional

from apps.core.domain.usecases.base import BaseUseCaseInputDTO


class ServerConfInfoInputDTO(BaseUseCaseInputDTO):
    name: Optional[str]
    address: Optional[str]
    end_point: Optional[str]
    publickey: Optional[str]
    privatekey: Optional[str]
    is_active: bool
    is_test: bool

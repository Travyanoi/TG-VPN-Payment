from pydantic import BaseModel

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TYPE_CHECKING, TypeVar

import structlog

if TYPE_CHECKING:
    from apps.bot.models import UserInfo

logger = structlog.get_logger(__name__)


class BaseUseCaseInputDTO(BaseModel):
    ...


class BaseUseCaseOutputDTO(BaseModel):
    ...


TInput = TypeVar('TInput', bound=BaseUseCaseInputDTO)
TOutput = TypeVar('TOutput', bound=BaseUseCaseOutputDTO)


class BaseUseCase(Generic[TInput, TOutput], ABC):
    def __init__(self, user: Optional['UserInfo'] = None):
        self._user = user

    def _get_context_vars(self) -> dict[str, Any]:
        _contextvars = {
            'usecase': self.__class__.__name__,
        }
        if self._user is not None:
            _contextvars['user_id'] = self._user.id

        return _contextvars

    @abstractmethod
    def _execute(self, input_dto: Optional[TInput]) -> TOutput:
        raise NotImplementedError

    def execute(self, input_dto: Optional[TInput]) -> TOutput:
        with (
            structlog.contextvars.bound_contextvars(
                **self._get_context_vars(),
            )
        ):
            try:
                return self._execute(input_dto)
            except Exception as e:
                self._handle_exception(e=e, input_dto=input_dto)
                logger.exception(
                    f"{self.__class__.__name__} unexpected exception",
                    exc=e,
                    user=self._user,
                )
                raise e

    def _handle_exception(self, e: Exception, input_dto: Optional[TInput]) -> None:
        if self._user:
            self._user.log(
                text=(
                    f'{self.__class__.__name__} unexpected exception:='
                    f'{str(e)} '
                ),
                level=1,
            )

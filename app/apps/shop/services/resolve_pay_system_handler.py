from typing import Callable


class ResolvePaySystemHandlerService:

    @classmethod
    def resolve_paysystem_handler(cls, class_name: str) -> Callable:
        from apps.shop.pay_system import classes
        return getattr(classes, class_name)

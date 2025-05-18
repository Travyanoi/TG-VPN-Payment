from typing import Optional

from apps.bot.domain.server_conf_info import ServerConfInfoEntity
from apps.bot.models import ServerConfInfo
from apps.bot.repositories.base import BaseRepository


class ServerConfInfoRepository(BaseRepository[ServerConfInfo]):
    def get_by_id(self, pk: int) -> Optional[ServerConfInfoEntity]:
        instance = ServerConfInfo.objects.get(pk=pk)
        return ServerConfInfoEntity.from_model(instance) if instance else None

    def create(self, **kwargs) -> ServerConfInfoEntity:
        instance = ServerConfInfo.objects.create(**kwargs)
        return ServerConfInfoEntity.from_model(instance)

    def save(self, entity: 'ServerConfInfoEntity') -> ServerConfInfoEntity:
        instance, _ = ServerConfInfo.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "name": entity.name,
                "address": entity.address,
                "end_point": entity.end_point,
                "publickey": entity.publickey,
                "privatekey": entity.privatekey,
                "is_active": entity.is_active,
                "is_test": entity.is_test,
            }
        )
        return ServerConfInfoEntity.from_model(instance)

    def delete(self, entity: 'ServerConfInfoEntity') -> None:
        ServerConfInfo.objects.filter(pk=entity.pk).delete()

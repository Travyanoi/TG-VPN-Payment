from typing import Optional, List

from apps.bot.domain.server_conf_info import ServerConfInfoEntity
from apps.bot.models import ServerConfInfo
from apps.bot.repositories.base import BaseRepository


class ServerConfInfoRepository(BaseRepository[ServerConfInfo]):
    def get_by_id(self, pk: int) -> Optional[ServerConfInfoEntity]:
        try:
            instance = ServerConfInfo.objects.get(pk=pk)
            return ServerConfInfoEntity.from_model(instance)
        except ServerConfInfo.DoesNotExist:
            return None

    def get_by_product_id(self, product_id: int) -> Optional[List[ServerConfInfoEntity]]:
        instances = ServerConfInfo.objects.filter(product_id=product_id)
        return [ServerConfInfoEntity.from_model(instance) for instance in instances]

    def create(self, **kwargs) -> ServerConfInfoEntity:
        instance = ServerConfInfo.objects.create(**kwargs)
        return ServerConfInfoEntity.from_model(instance)

    def save(self, entity: ServerConfInfoEntity) -> ServerConfInfoEntity:
        instance, _ = ServerConfInfo.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "name": entity.name,
                "product_id": entity.product_id,
                "address": entity.address,
                "end_point": entity.end_point,
                "publickey": entity.publickey,
                "privatekey": entity.privatekey,
                "is_active": entity.is_active,
                "is_test": entity.is_test,
                "extra_conf": entity.extra_conf,
            }
        )
        return ServerConfInfoEntity.from_model(instance)

    def delete(self, entity: 'ServerConfInfoEntity') -> None:
        ServerConfInfo.objects.filter(pk=entity.pk).delete()

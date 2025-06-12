from typing import Optional, List

from apps.bot.domain.info_for_conf_file import InfoForConfFileEntity
from apps.bot.models.info_for_conf_file import InfoForConfFile
from apps.bot.repositories.base import BaseRepository


class InfoForConfFileRepository(BaseRepository[InfoForConfFileEntity]):
    def get_by_user_server_id(self, chat_id: str, server_id: int) -> Optional[InfoForConfFileEntity]:
        if not chat_id or not server_id:
            return None
        try:
            instance = InfoForConfFile.objects.get(user=chat_id, server=server_id)
            return InfoForConfFileEntity.from_model(instance)
        except InfoForConfFile.DoesNotExist:
            return None

    def get_by_server_id(self, server_id: int) -> List[InfoForConfFileEntity]:
        instances = InfoForConfFile.objects.filter(server_id=server_id)
        return [InfoForConfFileEntity.from_model(instance) for instance in instances]

    def create(self, **kwargs) -> InfoForConfFileEntity:
        instance = InfoForConfFile.objects.create(**kwargs)
        return InfoForConfFileEntity.from_model(instance)

    def save(self, entity: InfoForConfFileEntity) -> InfoForConfFileEntity:
        if entity.pk is not None:
            instance, _ = InfoForConfFile.objects.update_or_create(
                pk=entity.pk,
                defaults={
                    "user_id": entity.user,
                    "server_id": entity.server,
                    "address": entity.address,
                    "publickey": entity.publickey,
                    "privatekey": entity.privatekey,
                    "enable": entity.enable,
                }
            )
        else:
            instance, _ = InfoForConfFile.objects.update_or_create(
                user_id=entity.user,
                server_id=entity.server,
                defaults={
                    "address": entity.address,
                    "publickey": entity.publickey,
                    "privatekey": entity.privatekey,
                    "enable": entity.enable,
                }
            )
        return InfoForConfFileEntity.from_model(instance)

    def delete(self, entity: InfoForConfFileEntity) -> None:
        InfoForConfFile.objects.filter(pk=entity.pk).delete()

from typing import Optional

from apps.bot.domain.info_for_conf_file import InfoForConfFileEntity
from apps.bot.models.info_for_conf_file import InfoForConfFile
from apps.bot.repositories.base import BaseRepository


class InfoForConfFileRepository(BaseRepository[InfoForConfFileEntity]):
    def get_by_user_id(self, chat_id: str, server_id: int) -> Optional[InfoForConfFileEntity]:
        try:
            instance = InfoForConfFile.objects.get(user=chat_id, server=server_id)
            return InfoForConfFileEntity.from_model(instance)
        except InfoForConfFile.DoesNotExist:
            return None

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

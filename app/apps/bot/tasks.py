import structlog
from celery import shared_task
import subprocess

from apps.bot.repositories.info_for_conf_file import InfoForConfFileRepository
from apps.bot.repositories.user_info import UserInfoRepository

logger = structlog.getLogger("bot.tasks")

@shared_task(bind=True)
def add_user_to_wireguard(self, dto: dict):
    """
    Задача выполняется на воркере stockholm.
    Обновляет конфигурационный файл awg0 и применяет изменения через ssh на хосте.
    """
    try:
        server_id = dto["server_id"]
        ssh_endpoint = dto["ssh_endpoint"]
        ssh_user = "root"
        ssh_key_path = "/opt/ssh/worker_key"

        template_path = "/etc/amnezia/amneziawg/awg0-template.conf"
        config_path = "/etc/amnezia/amneziawg/awg0.conf"

        # 1. Генерируем конфиг на основе шаблона и записываем его
        with open(template_path, "r") as f:
            config_base = f.read()

        repo = InfoForConfFileRepository()
        users = repo.get_enabled_by_server_id(server_id)

        peer_blocks = ""
        for user in users:
            user_repo = UserInfoRepository()
            user_info = user_repo.get_by_chat_id(user.user_id)
            peer_blocks += (
                f"\n[Peer]\n"
                f"# {user.user_id} --- {user_info.username}\n"
                f"PublicKey = {user.publickey}\n"
                f"AllowedIPs = {user.address}/32\n"
            )

        full_config = config_base.strip() + "\n" + peer_blocks

        with open(config_path, "w") as f:
            f.write(full_config)

        ssh_command = (
            f"ssh -i {ssh_key_path} {ssh_user}@{ssh_endpoint} "
            f"&& awg-quick down awg0 && awg-quick up awg0"
        )

        subprocess.run(ssh_command, shell=True, check=True)

        logger.info(f"Конфигурация обновлена и интерфейс перезапущен на {ssh_endpoint}")
        return {"status": "success", "server_id": server_id, "user_count": len(users)}

    except Exception as e:
        logger.exception("Ошибка при обновлении конфигурации WireGuard")
        return {"status": "error", "error": str(e), "server_id": dto.get("server_id")}


@shared_task(bind=True)
def notify_user_addition_status(self, result: dict):
    """
    Задача выполняется на мастере. Принимает результат от предыдущей задачи.
    Может отправить уведомление в бота или в лог.
    """
    username = result.get("username", "<unknown>")
    status = result.get("status")

    if status == "success":
        logger.info(f"Пользователь {username} успешно добавлен в AmnesiaWG.")
    else:
        logger.error(f"Ошибка при добавлении {username}: {result.get('error')}")
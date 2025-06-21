import structlog
from celery import shared_task
import subprocess

from apps.bot.repositories.info_for_conf_file import InfoForConfFileRepository
from apps.bot.repositories.server_conf_info import ServerConfInfoRepository
from apps.bot.repositories.user_info import UserInfoRepository

logger = structlog.getLogger("bot.tasks")


@shared_task(bind=True)
def add_user_to_wireguard(self, server_id: int, chat_id: str):
    """
    Добавляет нового пользователя в awg0.conf, если он ещё не добавлен.
    """
    try:
        server_repo = ServerConfInfoRepository()
        server = server_repo.get_by_id(server_id)
        if not server:
            raise ValueError(f"Server {server_id} not found")

        user_conf_repo = InfoForConfFileRepository()
        user_conf = user_conf_repo.get_by_user_server_id(chat_id, server_id)
        if not user_conf:
            raise ValueError(f"User config for chat_id={chat_id} on server_id={server_id} not found")

        user_repo = UserInfoRepository()
        user_info = user_repo.get_by_chat_id(chat_id)
        username = user_info.username if user_info else "unknown"

        ssh_user = "root"
        ssh_key_path = "/root/.ssh/worker_key"
        ssh_endpoint = server.end_point.split(":")[0]

        config_path = "/etc/amnezia/amneziawg/awg0.conf"

        with open(config_path, "r") as f:
            config_content = f.read()

        if f"# {chat_id}" in config_content:
            logger.info(f"Пользователь {chat_id} уже присутствует в awg0.conf")
            return {"status": "skipped", "reason": "already_present", "chat_id": chat_id, "server_id": server_id}

        peer_block = (
            f"\n[Peer]\n"
            f"# {chat_id} --- {username}\n"
            f"PublicKey = {user_conf.publickey}\n"
            f"AllowedIPs = {user_conf.address}\n"
        )

        config_content = config_content.rstrip() + peer_block + "\n"

        with open(config_path, "w") as f:
            f.write(config_content)

        ssh_command = (
            f"ssh -i {ssh_key_path} {ssh_user}@{ssh_endpoint} "
            f"'awg-quick down awg0 && awg-quick up awg0'"
        )
        subprocess.run(ssh_command, shell=True, check=True)

        logger.info(f"Пользователь {chat_id} добавлен на сервер {server_id}")
        return {"status": "success", "chat_id": chat_id, "server_id": server_id}

    except Exception as e:
        logger.exception("Ошибка при добавлении пользователя в WireGuard")
        return {"status": "error", "error": str(e), "chat_id": chat_id, "server_id": server_id}


@shared_task(bind=True)
def notify_user_addition_status(self, result: dict):
    """
    Если пользователь добавлен успешно — отправляет ему WireGuard-конфигурационный файл
    по Telegram, используя Telegram-бота.
    """

    chat_id = result.get("chat_id")
    status = result.get("status")
    server_id = result.get("server_id")

    if not chat_id or not server_id:
        logger.warning("Нет chat_id или server_id для отправки конфигурации")
        return

    if status not in ["success", "skipped"]:
        logger.error(f"Ошибка при добавлении пользователя {chat_id}: {result.get('error')}")
        return

    try:
        # Получение данных пользователя и сервера
        info_repo = InfoForConfFileRepository()
        server_repo = ServerConfInfoRepository()

        user_info = info_repo.get_by_user_server_id(chat_id, server_id)
        server_info = server_repo.get_by_id(server_id)

        if not user_info or not server_info:
            raise ValueError("Не удалось получить необходимые данные для формирования конфигурации")

        extra = server_info.extra_conf

        allowed_ips = ("0.0.0.0/5, 8.0.0.0/7, 11.0.0.0/8, 12.0.0.0/6, 16.0.0.0/4, 32.0.0.0/3, 64.0.0.0/2, 128.0.0.0/3, "
                       "160.0.0.0/5, 168.0.0.0/6, 172.0.0.0/12, 172.32.0.0/11, 172.64.0.0/10, 172.128.0.0/9, "
                       "173.0.0.0/8, 174.0.0.0/7, 176.0.0.0/4, 192.0.0.0/9, 192.128.0.0/11, 192.160.0.0/13, "
                       "192.169.0.0/16, 192.170.0.0/15, 192.172.0.0/14, 192.176.0.0/12, 192.192.0.0/10, "
                       "193.0.0.0/8, 194.0.0.0/7, 196.0.0.0/6, 200.0.0.0/5, 208.0.0.0/4, 8.8.8.8/32"
                       )

        file = (
            "[Interface]\n"
            f"PrivateKey = {user_info.privatekey}\n"
            f"Jc = {extra.get('jc')}\n"
            f"Jmin = {extra.get('jmin')}\n"
            f"Jmax = {extra.get('jmax')}\n"
            f"S1 = {extra.get('s1')}\n"
            f"S2 = {extra.get('s2')}\n"
            f"H1 = {extra.get('h1')}\n"
            f"H2 = {extra.get('h2')}\n"
            f"H3 = {extra.get('h3')}\n"
            f"H4 = {extra.get('h4')}\n"
            f"Address = {user_info.address}\n"
            "DNS = 8.8.8.8\n"
            "MTU = 1420\n\n"
            "[Peer]\n"
            f"PublicKey = {server_info.publickey}\n"
            f"AllowedIPs = {allowed_ips}\n"
            f"Endpoint = {user_info.address}\n"
            "PersistentKeepalive = 60"
        ).encode("utf-8")

        from apps.bot.bot import send_conf_file
        send_conf_file(chat_id, file)

        logger.info(f"Файл конфигурации успешно отправлен пользователю {chat_id}")

    except Exception as e:
        logger.exception(f"Ошибка при генерации или отправке конфигурационного файла: {str(e)}")

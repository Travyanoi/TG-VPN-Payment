from celery import shared_task
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def add_user_to_wireguard(self, dto: dict):
    """
    Задача выполняется на воркере stockholm. Добавляет пользователя в конфигурацию WireGuard.
    """
    try:
        username = dto["username"]
        pubkey = dto["public_key"]
        ip = dto["ip_address"]

        config_path = "/etc/wireguard/wg1.conf"

        peer_config = f"\n[Peer]\n# {username}\nPublicKey = {pubkey}\nAllowedIPs = {ip}/32\n"
        with open(config_path, "a") as f:
            f.write(peer_config)

        # Применяем изменения
        # subprocess.run(["wg-quick", "save", "wg0"], check=True)
        # subprocess.run(["wg", "addconf", "wg0", config_path], check=True)
        print(f"\nTASK COMPLETED\n")
        return {"status": "success", "username": username}

    except Exception as e:
        logger.exception("Ошибка при добавлении пользователя в WireGuard")
        return {"status": "error", "error": str(e), "username": dto.get("username")}


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
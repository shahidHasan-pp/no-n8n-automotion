
import requests
from app.core.config import settings
from .base import MessagingStrategy
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DiscordStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None, extra_data: dict = None) -> bool:
        # 'to' is expected to be the dm_channel_id OR user_id if we want to create DM
        # But per logic in Service, we should pass the right ID. 
        # If 'to' looks like a channel ID (snowflake), we send.
        
        logger.info(f"[Discord] Sending to {to}")
        
        if not settings.DISCORD_BOT_TOKEN:
            logger.warning("[Discord] Token not set, skipping API call.")
            return True
        
        headers = {
            "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (https://purplepatch.notifications, 1.0)"
        }
        
        # Logic: 
        # 1. Try sending to 'to' assuming it is a channel_id
        # 2. If failure (or if we know it's a user_id), try creating a DM channel first.
        # Use extra_data to hint if 'to' is user_id or channel_id? 
        # For simplicity: Assume 'to' is channel_id. If missing, we might use extra_data['user_id'] to create it.
        
        target_channel_id = to
        
        # If extra_data has user_id and 'to' seems invalid or we want to ensure DM existence
        if extra_data and extra_data.get('create_dm') and extra_data.get('user_id'):
            # Create DM Channel
            create_dm_url = "https://discord.com/api/v10/users/@me/channels"
            dm_payload = {"recipient_id": extra_data['user_id']}
            try:
                dm_resp = requests.post(create_dm_url, headers=headers, json=dm_payload, timeout=5)
                if dm_resp.status_code in [200, 201]:
                    target_channel_id = dm_resp.json().get('id')
                    logger.info(f"[Discord] Created/Found DM channel {target_channel_id} for user {extra_data['user_id']}")
                else:
                    logger.error(f"[Discord] Failed to create DM: {dm_resp.text}")
                    return False
            except Exception as e:
                logger.error(f"[Discord] Exception creating DM: {e}")
                return False

        full_text = content
        if link:
            full_text += f"\n\nLink: {link}"
            
        url = f"https://discord.com/api/v10/channels/{target_channel_id}/messages"
        payload = {
            "content": full_text
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"[Discord] Successfully sent to channel {target_channel_id}")
                return True
            else:
                logger.error(f"[Discord] Failed to send: {response.text}")
                return False
        except Exception as e:
            logger.error(f"[Discord] Exception: {e}")
            return False

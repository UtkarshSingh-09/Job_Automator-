"""
Delivery package for candidate notifications, match alerts, and artifact dispatch.
Supports Telegram Bot API with HTML formatting, inline buttons, and PDF attachments.
"""
from resume_agent.deliver.telegram import TelegramClient

__all__ = ["TelegramClient"]

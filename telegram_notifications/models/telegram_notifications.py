# -*- coding: utf-8 -*-

import logging
import requests
from odoo.exceptions import ValidationError
from odoo import api, fields, models
from datetime import timedelta

_logger = logging.getLogger(__name__)


class TelegramConfig(models.Model):
    _name = "telegram.config"
    _description = "Telegram Configuration"

    bot_token = fields.Char("Bot Token", required=True)
    chat_id = fields.Char("Chat ID", required=True)

    @api.model
    def get_config(self):
        config = self.search([], limit=1)
        if not config:
            config = self.create(
                {
                    "bot_token": "123",  # Replace with your actual BOT token
                    "chat_id": "123",  # Replace with your actual chat ID
                }
            )
        return config

    @api.model
    def create(self, values):
        existing_config = self.env["telegram.config"].search([], limit=1)
        if existing_config:
            raise ValidationError(
                "Не можна створювати кілька екземплярів моделі, редагуйте вже існуючий!!!"
            )
        return super(TelegramConfig, self).create(values)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, values):
        order = super(SaleOrder, self).create(values)
        website_id = values.get("website_id")
        if website_id and order.state in ["sale", "sent"]:
            self.send_telegram_notification(order)
        return order

    def write(self, values):
        result = super(SaleOrder, self).write(values)
        token = self.access_token
        if token and "state" in values and values["state"] in ["sale", "sent"]:
            for order in self:
                self.send_telegram_notification(order)
        return result

    def send_telegram_notification(self, order):
        try:
            # Get config TG
            config = self.env["telegram.config"].get_config()
            if not config:
                _logger.warning("Telegram configuration is missing.")
                return

            bot_token = config.bot_token
            chat_id = config.chat_id
            # http://localhost:8069/web#id=50&cids=1&menu_id=205&action=335&model=sale.order&view_type=form
            order_link = f"Enter your order link, from Sales"
            message = (
                f"Повідомлення з сайту 📩\n"
                f"Нове замовлення {order.name}, від {order.partner_id.name}, на суму {order.amount_total}\n"
                f"<a href='{order_link}'>Переглянути замовлення</a>"
            )

            # Sending msg to TG
            params = {"chat_id": chat_id, "parse_mode": "HTML", "text": message}
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage", data=params
            )

            if response.status_code != 200:
                _logger.error(
                    "Failed to send Telegram notification for order %s", order.name
                )
            else:
                _logger.info(
                    "Telegram notification sent successfully for order %s",
                    order.name,
                )

        except Exception as e:
            _logger.error(
                "Error sending Telegram notification for order %s: %s",
                order.name,
                str(e),
            )


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, values):
        # Call super to create the partner
        partner = super(ResPartner, self).create(values)
        if (
            not self.env.context.get("import_file")
            and str(values.get("website_id")) == "None"
        ):
            self.send_telegram_notification(partner)
        return partner

    def send_telegram_notification(self, partner):
        try:
            # Get Telegram configuration
            config = self.env["telegram.config"].get_config()
            bot_token = config.bot_token
            chat_id = config.chat_id
            # http://localhost:8069/web#id=42&cids=1&menu_id=347&action=508&model=res.partner&view_type=form
            parnter_link = f"Enter your partner link, from Partner"

            # registration_time = fields.Datetime.to_string(partner.create_date)
            # registration_time = partner.create_date.strftime("%Y-%m-%d о %H:%M:%S")
            registration_time = (partner.create_date + timedelta(hours=3)).strftime(
                "%Y-%m-%d о %H:%M:%S"
            )

            message = (
                f"Новий користувач 🙋🏻‍♀️🙋🏼‍♂️ \n"
                f"{partner.name} зареєструвався {registration_time}\n"
                f"<a href='{parnter_link}'>Переглянути користувача</a>"
            )

            # Send the message using requests or any other suitable method
            params = {"chat_id": chat_id, "parse_mode": "HTML", "text": message}
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage", data=params
            )

            if response.status_code != 200:
                _logger.error(
                    "Failed to send Telegram notification for new user %s", partner.name
                )
            else:
                _logger.info(
                    "Telegram notification sent successfully for new user %s",
                    partner.name,
                )

        except Exception as e:
            _logger.error(
                "Error sending Telegram notification for new user %s: %s",
                partner.name,
                str(e),
            )

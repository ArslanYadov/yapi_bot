from telegram.error import BadRequest


class BotSendMessageError(BadRequest):
    """Кастомная ошибка при отправке сообщения ботом."""

    def __init__(self, *args):
        """Инициализация сообщения."""
        if not self.args:
            self.message = None
        self.message = args[0]

    def __str__(self):
        """Строковое представление сообщения."""
        if not self.message:
            return 'BotSendMessageError has been raise'
        return self.message

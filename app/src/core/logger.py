import logging


def build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # чтобы не дублировались логи
    logger.propagate = False

    # handler (куда писать — stdout)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # формат с именем логгера
    formatter = logging.Formatter(
        "[%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)

    # очищаем старые хендлеры (важно при повторной инициализации)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(handler)

    return logger

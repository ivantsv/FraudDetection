import logging
import sys
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Класс для настройки подробного логирования"""
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        log_record['level'] = record.levelname
        log_record['message'] = record.getMessage()
        log_record['time'] = self.formatTime(record, self.datefmt)

        if not log_record.get('correlation_id'):
            log_record['correlation_id'] = getattr(record, 'correlation_id', None)

        if not log_record.get('component'):
            log_record['component'] = getattr(record, 'component', 'core')

        log_record['logger'] = record.name
        log_record['file'] = f"{record.pathname}:{record.lineno}"

def setup_logger(component: str = "core"):
    """Создание логера"""
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter('%(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    class ComponentFilter(logging.Filter):
        def filter(self, record):
            record.component = component
            return True

    logger.addFilter(ComponentFilter())

    return logger
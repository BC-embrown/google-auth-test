import logging, json, sys
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class SimpleLogger:    
    def __init__(
        self, 
        name: str, 
        app_name: str,
        log_type: str,
        level: int = logging.INFO
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.app_name = app_name
        self.log_type = log_type
        
        if self.logger.handlers:
            self.logger.handlers = []
        
        console_handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _format_event(self, event_data: Dict[str, Any]) -> str:
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        if "application" not in event_data:
            event_data["application"] = self.app_name
        if "log_type" not in event_data:
            event_data["log_type"] = self.log_type
            
        return json.dumps(event_data)
    
    def info(self, event_data: Dict[str, Any]) -> None:
        self.logger.info(self._format_event(event_data))
    
    def warning(self, event_data: Dict[str, Any]) -> None:
        self.logger.warning(self._format_event(event_data))
    
    def error(self, event_data: Dict[str, Any]) -> None:
        self.logger.error(self._format_event(event_data))
    
    def critical(self, event_data: Dict[str, Any]) -> None:
        self.logger.critical(self._format_event(event_data))
    
    def debug(self, event_data: Dict[str, Any]) -> None:
        self.logger.debug(self._format_event(event_data))

def get_logger(
    name: str, 
    app_name: str = "google-service", 
    log_type: str = "google-api",
) -> SimpleLogger:
    
    return SimpleLogger(name, app_name, log_type)
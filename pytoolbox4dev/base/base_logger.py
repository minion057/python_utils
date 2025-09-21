import sys
import logging
import functools
import pytoolbox4dev.config as cfg
import shutil

from pathlib import Path
from pytoolbox4dev.decorators.public_decorator import *

# for fast import
def _ensureAbsolutePath(check_path:str) -> Path:
    '''
    Determines the actual folder path of the file based on the given file path string.

    Args:
        check_path (str): Path of the folder or file to check.

    Returns:
        pathlib.Path: Absolute path.
    '''
    check_path = Path(check_path)
    if not check_path.is_absolute(): # Absolute path.
        # If it is not an absolute path, it is assumed to be a relative path.
        check_path = check_path.resolve()
    return check_path

def _ensure_dir(dirname, exist_ok:bool=False):
    dirname = Path(dirname)
    if not dirname.is_dir():
        dirname.mkdir(parents=True, exist_ok=exist_ok)

# Custom error handler (unchanged)
class CustomLoggingErrorHandler:
    def handleError(self, record):
        try:
            print(f'Error processing logs: {record.getMessage()}', file=sys.stderr)
            print(f'Logging system internal error: {self.format(record)}', file=sys.stderr)
            print(f'Error-causing Handlers: {record.exc_info[0].__name__ if record.exc_info else "Unknown"}', file=sys.stderr)
            print(f'Error Message: {record.exc_text or record.getMessage()}', file=sys.stderr)
        except Exception:
            print('Error in the Custom Log Error Handler itself!', file=sys.stderr)
logging.Handler.handleError = CustomLoggingErrorHandler().handleError

# Custom FileHandler (simplified)
class CustomDisplayFileHandler(logging.FileHandler):
    # This handler no longer needs to store or manipulate 'display_name'
    # It just needs to be a standard FileHandler that formatters can use.
    def emit(self, record):
        try:
            super().emit(record)
        except Exception as e:
            print(f'ERROR: Could not write log to file {self.baseFilename}. Reason: {e}', file=sys.stderr)
            root_logger = logging.getLogger('')
            if root_logger.handlers:
                try:
                    self.disabled = True
                    root_logger.error(f'Failed to write log record "{record.getMessage()}" to file "{self.baseFilename}". Error: {e}')
                finally:
                    self.disabled = False
            else:
                print(f'CRITICAL: Failed to log error about file write failure: {e}', file=sys.stderr)

# BaseLogger (modified _output_message and formatter creation)
@public
class BaseLogger:
    _shared_file_handlers_by_path = {}
    
    def __init__(
        self,
        logger_name:str,
        file_path:str=cfg.LOG_FILE_PATH,
        log_to_separate_file: bool = False,
        shared_log_file_name: str = cfg.LOG_FILE_NAME,
        only_print:bool=cfg.LOG_ONLY_PRINT,
        init_print_path:bool=False
    ):
        self.logger, self.debug_logger = None, None
        self.logger_name = logger_name # This is the name we want to display in logs
        self.setup_params = dict(
            only_print=only_print, 
            log_to_separate_file=log_to_separate_file,
            shared_log_file_name=shared_log_file_name
        )
        self.save_path = dict(dir=file_path, logger=None, debug_logger=None)
        self._setup_loggers()
        init_str = f'`{self.logger_name}` Logger initialized.'
        if init_print_path:
            self.info(f'{init_str}.\n{self.getLogPath2str()}', debug_mirror_other=True)
        else:
            self.debug(init_str)

    def _setup_loggers(self):
        if self.setup_params['only_print']: return 
        log_to_separate_file = self.setup_params['log_to_separate_file']
        shared_log_file_name = self.setup_params['shared_log_file_name']
        # try: # Preventing “Circular Import” error
        #     from utils import ensureAbsolutePath, ensure_dir
        # except Exception as e:
        #     raise Exception(f'Could not import ensureAbsolutePath, ensure_dir from utils.py\n{e}')
        self.save_path['dir'] = _ensureAbsolutePath(Path(self.save_path['dir']))
        _ensure_dir(self.save_path['dir'])
        
        # --- Configure Main Logger ---
        # Keep logger name unique, but use display_name for log output.
        self.logger = logging.getLogger(str(self.save_path['dir'] / self.logger_name)) 
        self.logger.setLevel(logging.INFO) 
        self.logger.propagate = False # Prevent propagation to root logger
        
        # Clear existing handlers for this logger to prevent duplicates
        for handler in list(self.logger.handlers):
            if isinstance(handler, (logging.FileHandler, CustomDisplayFileHandler)):
                self.logger.removeHandler(handler)
                handler.close()

        if log_to_separate_file:
            self.save_path['logger'] = self.save_path['dir'] / f'{self.logger_name}.log'
            self._set_individual_file_handler(self.logger, self.save_path['logger'], logging.INFO)
        else:
            self.save_path['logger'] = self.save_path['dir'] / f'{shared_log_file_name}.log'
            self._set_shared_file_handler(self.logger, self.save_path['logger'], logging.INFO)
        
        # --- Configure Debug Logger ---
        self.debug_logger = logging.getLogger(str(self.save_path['dir'] / f'{self.logger_name}_debug')) 
        self.debug_logger.setLevel(logging.DEBUG) 
        self.debug_logger.propagate = False 

        # Clear existing handlers for the debug logger
        for handler in list(self.debug_logger.handlers):
            if isinstance(handler, (logging.FileHandler, CustomDisplayFileHandler)):
                self.debug_logger.removeHandler(handler)
                handler.close()

        if log_to_separate_file:
            self.save_path['debug_logger'] = self.save_path['dir'] / f'{self.logger_name}_debug.log'
            self._set_individual_file_handler(self.debug_logger, self.save_path['debug_logger'], logging.DEBUG)
        else:
            self.save_path['debug_logger'] = self.save_path['dir'] / f'{shared_log_file_name}_debug.log'
            self._set_shared_file_handler(self.debug_logger, self.save_path['debug_logger'], logging.DEBUG) 
            
        self.save_path['logger'] = _ensureAbsolutePath(self.save_path['logger'])
        self.save_path['debug_logger'] = _ensureAbsolutePath(self.save_path['debug_logger'])
    
    def _get_formatter(self, level: int):
        if level == logging.DEBUG:
            return logging.Formatter('%(asctime)s - %(logger_display_name)s | %(message)s')
        else: # info, warning, error, critical
            return logging.Formatter('%(asctime)s - %(logger_display_name)s | [%(levelname)s] %(message)s')
    
    def _set_individual_file_handler(self, logger_instance: logging.Logger, log_file_path: Path, level: int):
        new_handler = CustomDisplayFileHandler(str(log_file_path)) 
        # print(f'_set_individual_file_handler!!!!!! {logger_instance.name}')
        # Formatter uses 'logger_display_name' from the 'extra' dict on LogRecord
        new_handler.setFormatter(self._get_formatter(level))
        new_handler.setLevel(level) 
        logger_instance.addHandler(new_handler)

    def _set_shared_file_handler(self, logger_instance: logging.Logger, log_file_path: Path, level: int):
        str_log_file_path = str(log_file_path.resolve()) 

        current_shared_handler = None
        if str_log_file_path in BaseLogger._shared_file_handlers_by_path:
            potential_handler = BaseLogger._shared_file_handlers_by_path[str_log_file_path]
            if Path(potential_handler.baseFilename).exists():
                current_shared_handler = potential_handler
            else:
                potential_handler.close()
                del BaseLogger._shared_file_handlers_by_path[str_log_file_path]
            
        if current_shared_handler is None:
            new_handler = CustomDisplayFileHandler(str_log_file_path) 
            # print(f'_set_shared_file_handler!!!!!! {logger_instance.name}') # Use logger_instance.name for print
            # Formatter uses 'logger_display_name' from the 'extra' dict on LogRecord
            new_handler.setFormatter(self._get_formatter(level))
            new_handler.setLevel(level)
            BaseLogger._shared_file_handlers_by_path[str_log_file_path] = new_handler
            current_shared_handler = new_handler
        
        # Ensure the shared handler is added to this logger if not already
        if current_shared_handler not in logger_instance.handlers:
            logger_instance.addHandler(current_shared_handler)
        
        if current_shared_handler.level > level:
            current_shared_handler.setLevel(level)
    
    def _logger_has_valid_handler(self, logger_instance: logging.Logger):
        for handler in logger_instance.handlers:
            if isinstance(handler, (logging.FileHandler, CustomDisplayFileHandler)) and Path(handler.baseFilename).exists():
                return True
        return False
    
    def _logger_reset_handlers(self, level: int, message: str):
        def last_check(logger_instance, print_logger_name):
            if not self._logger_has_valid_handler(logger_instance):
                print(f'[CRITICAL] Failed to re-setup {print_logger_name} logger `{self.logger_name}`. Logging message to stderr.', file=sys.stderr)
                level_name = logging.getLevelName(level)
                print(f'[{level_name}] {message}', file=sys.stderr)
                return False
            return True
        
        logger_instance = self.logger if level != logging.DEBUG else self.debug_logger
        print_logger_name = 'Main' if level != logging.DEBUG else 'Debug'
        
        if not self._logger_has_valid_handler(logger_instance): 
            print(f'WARNING: {print_logger_name} logger `{self.logger_name}` has no active handlers. Attempting re-setup for all logs...', file=sys.stderr)
            self._setup_loggers() 
            self.warning(f'Re-setup of all `{self.logger_name}` loggers complete.', debug_mirror_other=True)
            
            if not last_check(self.logger, 'Main'): return False
            if not last_check(self.debug_logger, 'Debug'): return False
        return True
        
    def _output_message(self, message: str, level: int = logging.INFO, debug_mirror_other:bool=False):
        if self.logger is None:
            print(f'[{logging.getLevelName(level)}] {message}', file=sys.stderr) 
            return
        if not self._logger_reset_handlers(level, message):
            print(f'Faliled to log message.\n{message}', file=sys.stderr)
            return
        # Add the logger's display name to the LogRecord's 'extra' dictionary
        extra_data = {'logger_display_name': self.logger_name}
        if level == logging.DEBUG: 
            self.debug_logger.debug(message, extra=extra_data) 
        else:
            self.logger.log(level, message, extra=extra_data) # Pass extra_data here
            if debug_mirror_other:
                self.debug(f'[{logging.getLevelName(level)}] {message}')
        
    def debug(self, message: str):
        self._output_message(message, logging.DEBUG)

    def info(self, message: str, debug_mirror_other:bool=False):
        self._output_message(message, logging.INFO, debug_mirror_other)

    def warning(self, message: str, debug_mirror_other:bool=False):
        self._output_message(message, logging.WARNING, debug_mirror_other)

    def error(self, message: str, debug_mirror_other:bool=False):
        self._output_message(message, logging.ERROR, debug_mirror_other)

    def critical(self, message: str, debug_mirror_other:bool=False):
        self._output_message(message, logging.CRITICAL, debug_mirror_other)
        
    def getLogPath2str(self):
        return '\n'.join(f'{name}: {str(path)}' for name, path in self.save_path.items() if name != 'dir')
    
    def moveLogDirectory(self, destination_path):
        # try: # Preventing “Circular Import” error
        #     from utils import ensureAbsolutePath, ensure_dir
        # except Exception as e:
        #     raise Exception(f'Could not import ensureAbsolutePath, ensure_dir from utils.py\n{e}')
        source_path = self.save_path['dir']
        log_dir_name = source_path.name
        destination_path = _ensureAbsolutePath(Path(destination_path))
        _ensure_dir(destination_path)
    
        try:
            shutil.move(str(source_path), str(destination_path))
            print(f'Folder "{source_path}" moved to "{destination_path}" successfully.', file=sys.stderr)
        except FileNotFoundError:
            raise Exception(f'Error: Source folder "{source_path}" not found.')
        except Exception as e:
            raise Exception(f'An error occurred\n{e}')

        # Verify if the new folder exists and the old one does not.
        if destination_path.exists():
            print(f'Destination: "{destination_path}" now exists.', file=sys.stderr)
        else: 
            raise Exception(f'Error: Destination folder "{destination_path}" not found.')
        if not source_path.exists():
            print(f'Source: "{source_path}" no longer exists.', file=sys.stderr)
        else:
            raise Exception(f'Error: Source folder "{source_path}" still exists.')
        
        self.save_path['dir'] = destination_path / log_dir_name
        self.save_path['logger'] = self.save_path['dir'] / self.save_path['logger'].name
        self.save_path['debug_logger'] = self.save_path['dir'] / self.save_path['debug_logger'].name
        self.info(f'The logger\'s route has changed.\n{self.getLogPath2str()}', debug_mirror_other=True)
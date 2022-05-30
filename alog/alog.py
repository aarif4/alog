"""Main module."""

import os
import time
import logging
import traceback
from enum import Enum
from termcolor import colored

from .errors import *

timezone_fcn = time.localtime

class logger:
    _log_levels = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARN, logging.WARNING, logging.ERROR, logging.FATAL, logging.CRITICAL]

    _logger : logging.Logger
    _name : str
    _filename : str

    def __init__( 
        self, 
        log_name = 'root', 
        filename = '', 
        level = logging.INFO, 
        file_level = logging.NOTSET):

        if not log_name or not isinstance(log_name, str):
            raise aLogInputArgError(
                'Invalid name given (got "{}"). Must be a nonempty string'.format(log_name))
        self._name = log_name

        if not filename or not isinstance(filename, str) or os.path.isdir(os.path.dirname(filename)):
            raise aLogInputArgError(
                'Invalid filename given. Must be a string (can be empty)'
            )
        if not filename:
            self._filename = ''
        else:
            self._filename = os.path.abspath(filename)

        if self._name in logging.Logger.manager.loggerDict:
            self._logger = logging.getLogger(self._name)
        
        self._set_log_levels()
        
        self._logger = logging.getLogger(self._name)
        if self._logger.hasHandlers() and len(self._logger.handers) > 2:
            # this was made by someone else
            raise aLogUnknownHandlers('Found {} handlers in this already-existing logger'.format(len(self._logger.handers)))
        
        self._logger.setLevel(level=logging.NOTSET)

        if level not in self._log_levels:
            raise aLogInputArgError('Got invalid level for stderr logging. Got ({})'.format(level))
        self._set_stderr_handler(level)

        if file_level not in self._log_levels:
            raise aLogInputArgError('Got invalid level for stderr logging. Got ({})'.format(file_level))
        self._set_file_handler(file_level)
        
        self._set_timezone(timezone_fcn)
    
    def _set_log_levels(self):
        logging.addLevelName(logging.DEBUG,   colored('DEBUG','cyan'))
        logging.addLevelName(logging.INFO,    colored('INFO ','green'))
        logging.addLevelName(logging.WARNING, colored('WARN ','yellow'))
        logging.addLevelName(logging.ERROR,   colored('ERROR','red'))
        logging.addLevelName(logging.FATAL,   colored('FATAL','magenta'))

    def _get_format(self):
        return logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s','%Y-%m-%d %H:%M:%S')
    
    def _set_timezone(self, struct_time_fcn):
        fmt = self.get_format()
        fmt.converter = struct_time_fcn
        for handler in self._logger.handlers:
            handler.setFormatter(fmt)
    
    def _set_stderr_handler(self, print_log_lvl):
        ch = logging.StreamHandler()
        ch_name = getattr(ch.stream, 'name', '')
        for handler in self._logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                hndl_name = getattr(handler.stream, 'name', '')
                if hndl_name == ch_name:
                    # don't make one, it's already there
                    return
                else:
                    raise aLogUnknownHandlers('Found unknown StreamHandler in logger (got {})'.format(hndl_name))
        
        ch.setLevel(level=print_log_lvl)
        ch.setFormatter(self._get_format())
        self._logger.addHandler(ch)

    def _set_file_handler(self, file_log_level):
        for handler in self._logger.handlers:
            if isinstance(handler, logging.FileHandler):
                hndl_name = getattr(handler.stream, 'name', '')
                if hndl_name == self._filename:
                    # don't make one, it's already there
                    return
                else:
                    raise aLogUnknownHandlers('Found FileHandler in logger with an unknown file (got {})'.format(hndl_name))
        
        fp = logging.FileHandler(filename=self._filename)
        fp.setLevel(level=file_log_level)
        fp.setFormatter(self._get_format())
        self._logger.addHandler(fp)
    
    def __del__(self):
        # just delete the handlers, we'll recreate them the next time we instantiate this logger
        while self._logger.hasHandlers():
            self._logger.removeHandler(self._logger.handlers[0])
    
    def debug(self, string):
        self.log.debug(string)
    
    def info(self, string):
        self.log.info(string)
        
    def warning(self, string):
        self.log.warning(string)
        
    def error(self, string):
        self.log.error(string)
        
    def fatal(self, string):
        self.log.fatal(string)
        
    def exception(self, string):
        self.log.exception(string)
        # here it'll already call traceback.print_exception() to get the traceback
    
    def __repr__(self):
        return f'alog.{self.__class__.__name__}("{self._name}","{self._filename}")'

    def __str__(self):
        # in here you should try .isEnabledFor() to see what levels it will handle
        return ""

__all__ = [
    "timezone_fcn",
    "logger"
]
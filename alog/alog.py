"""Main module."""

import os
import time
import logging
import traceback
from enum import Enum
from termcolor import colored

from .errors import *


class logger:
    __log_levels = ['NOTSET','DEBUG','INFO','WARNING','ERROR','CRITICAL/FATAL']

    _logger : logging.Logger
    name : str
    filename : str
    print_log_lvl : int
    file_log_level : int

    def __init__( 
        self, 
        log_name = 'root', 
        filename = '', 
        print_log_lvl = logging.INFO, 
        file_log_level = logging.NOTSET ):

        if not log_name or not isinstance(log_name, str):
            raise aLogInputArgError(
                'Invalid name given (got {}). Must be a nonempty string'.format(log_name))

        if not isinstance(filename, str) or os.path.isdir(os.path.dirname(filename)):
            raise aLogInputArgError(
                'Invalid filename given. Must be a string'
            )
        if log_name in logging.Logger.manager.loggerDict:
            self.__logger = logging.getLogger(log_name)
        # you can find a logger from the dict keys here: logging.root.manager.loggerDict

        logging.addLevelName(logging.DEBUG,   colored('DEBUG','cyan'))
        logging.addLevelName(logging.INFO,    colored('INFO ','green'))
        logging.addLevelName(logging.WARNING, colored('WARN ','yellow'))
        logging.addLevelName(logging.ERROR,   colored('ERROR','red'))
        logging.addLevelName(logging.FATAL,   colored('FATAL','magenta'))

        fmt = self.get_format()

        self._logger = logging.getLogger(log_name)
        self._logger.setLevel(level=logging.NOTSET)

        ch = logging.StreamHandler()
        ch.setLevel(level=print_log_lvl)
        ch.setFormatter(fmt)
        self._logger.addHandler(ch)

        if filename:
            fp = logging.FileHandler(filename=filename)
            fp.setLevel(level=file_log_level)
            fp.setFormatter(fmt)
            self._logger.addHandler(fp)
        
        self.set_timezone(time.localtime)

            #if filename:
            #    self.fp = logging.FileHandler(filename=filename)
            #    self.fp.setLevel(level=log_lvl)
            #    self.fp.setFormatter(fmt)
            #    self.log.addHandler(self.fp)
    
    def get_format(self):
        return logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s','%Y-%m-%d %H:%M:%S')
    
    def set_timezone(self, struct_time_fcn):
        fmt = self.get_format()
        fmt.converter = struct_time_fcn
        for handler in self._logger.handlers:
            handler.setFormatter(fmt)
    
    def __del__(self):
        if not self.USE_PRINTF:
            if self.log:
                if self.ch:
                    self.log.removeHandler(self.ch)
                    del self.ch
                if self.fp:
                    self.log.removeHandler(self.fp)
                    del self.fp
                del self.log
    
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
    
    def __str__(self):
        # in here you should try .isEnabledFor() to see what levels it will handle
        return ""
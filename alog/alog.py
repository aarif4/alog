"""Main module."""

import os
import time
import logging
import logging.handlers
from enum import Enum
from termcolor import colored
from abc import abstractmethod

from .errors import *

timezone_fcn = time.localtime

# simple logger
# file logger (if given values, then do something)
# rotating file logger
# complex logger (simple + rotating)

class logger:
    _log_levels = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARN, logging.WARNING, logging.ERROR, logging.FATAL, logging.CRITICAL]

    _logger = None
    _name = ''
    _filename = ''
    _print_level = None
    _file_level = None

    def __init__( 
        self, 
        log_name = 'root', 
        print_level = logging.INFO, 
        filename = '',
        file_level = logging.NOTSET,
        file_sz = 0,
        num_files = 0):

        if not log_name or not isinstance(log_name, str):
            raise aLogInputArgError(
                'Invalid name given (got "{}"). Must be a nonempty string'.format(log_name))
        self._name = log_name

        if not filename or not isinstance(filename, str) or os.path.isdir(os.path.dirname(filename)):
            raise aLogInputArgError('Invalid filename given. Must be a string path that leads to an already existing directory (can be empty)')
        if not filename:
            self._filename = ''
        else:
            self._filename = os.path.abspath(filename)

        if print_level not in self._log_levels:
            raise aLogInputArgError('Got invalid level for print logging. Got ({})'.format(print_level))
        self._print_level = print_level

        if file_level not in self._log_levels:
            raise aLogInputArgError('Got invalid level for file logging. Got ({})'.format(file_level))
        self._file_level = file_level

        if not isinstance(file_sz, int):
            raise aLogInputArgError('Got invalid file_sz, must be an integer value')
        
        if not isinstance(num_files, int) or num_files < 0:
            raise aLogInputArgError('Got invalid num_files, must be a positive integer value')
        
        self._set_log_levels()

        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(level=logging.NOTSET) # set it to the lowest setting
    
    @abstractmethod
    def _add_handlers(self):
        raise NotImplementedError('Concrete implementation {} has not defined _add_handlers(), which is required.'.format(self.__class__.__name__))
    
    def _set_log_levels(self):
        logging.addLevelName(logging.DEBUG,   colored('DEBUG','cyan'))
        logging.addLevelName(logging.INFO,    colored('INFO ','green'))
        logging.addLevelName(logging.WARNING, colored('WARN ','yellow'))
        logging.addLevelName(logging.ERROR,   colored('ERROR','red'))
        logging.addLevelName(logging.FATAL,   colored('FATAL','magenta'))

    def _get_format(self):
        return logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s','%Y-%m-%d %H:%M:%S')
    
    def _find_matching_handlers(self, handlers_type_tuple = ()):
        #if not handlers_type_tuple and all([isinstance(handler_type,logging.Handler) for handler_type in handlers_type_tuple])
        response = []
        if handlers_type_tuple:
            for handler in self._logger.handlers:
                if isinstance(handler, handlers_type_tuple):
                    response.append(handler)
        
        return response

    def _validate_num_handlers(self, max_num_handlers):
        if self._logger.hasHandlers() and len(self._logger.handers) > max_num_handlers:
            # this was made by someone else
            raise aLogUnknownHandlers('Found {} handlers in the "{}" logger, is this logger the correct one you want to use?'.format(len(self._logger.handers), self._name))
    
    def set_timezone(self, struct_time_fcn=time.localtime):
        fmt = self.get_format()
        fmt.converter = struct_time_fcn
        for handler in self._logger.handlers:
            handler.setFormatter(fmt)    
    
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
    
    def __del__(self):
        # just delete the handlers, we'll recreate them the next time we instantiate this logger
        while self._logger.hasHandlers():
            self._logger.removeHandler(self._logger.handlers[0])
    
    def __repr__(self):
        return f'alog.{self.__class__.__name__}("{self._name}","{self._filename}")'

    def __str__(self):
        # in here you should try .isEnabledFor() to see what levels it will handle
        return ""


class SimpleLogger(logger):
    def __init__(self, name='root', print_level=logging.INFO):
        super().__init__(name, print_level)
        
        self._validate_num_handlers(1)

        self._add_handlers()
    
    def _add_handlers(self):
        ch = logging.StreamHandler()
        ch_name = getattr(ch.stream, 'name', '')
        handlers = self._find_matching_handlers((logging.StreamHandler))
        for handler in handlers:
            if isinstance(handler, logging.StreamHandler):
                hndl_name = getattr(handler.stream, 'name', '')
                if hndl_name == ch_name:
                    # don't make one, it's already there
                    return
                else:
                    raise aLogUnknownHandlers('Found unknown StreamHandler in logger (got "{}", expected "{}")'.format(hndl_name, ch_name))
        
        ch.setLevel(level=self._print_level)
        ch.setFormatter(self._get_format())
        self._logger.addHandler(ch)


class SilentLogger(logger):
    def __init__(self, name='root', filename = '', file_level=logging.INFO):
        super().__init__(name, logging.NOTSET, filename, file_level)

        self._validate_num_handlers(1)

        if not self._filename:
            raise aLogInputArgError('Expected a valid filename to use for logging purposes, instead got "{}"'.format(self._filename))
        
        self._add_handlers()

    def _add_handlers(self):
        handlers = self._find_matching_handlers((logging.FileHandler))
        for handler in handlers:
            if isinstance(handler, logging.FileHandler):
                hndl_name = getattr(handler.stream, 'name', '')
                if hndl_name == self._filename:
                    # don't make one, it's already there
                    return
                else:
                    raise aLogUnknownHandlers('Found FileHandler in logger with an unknown file (got "{}", expected "{}")'.format(hndl_name, self._filename))
        
        fp = logging.FileHandler(filename=self._filename)
        fp.setLevel(level=self._file_level)
        fp.setFormatter(self._get_format())
        self._logger.addHandler(fp)


class SilentRotatingLogger(logger):
    _file_sz = 0
    _num_files = 0
    
    def __init__(self, name = 'root', filename = '', file_level = logging.DEBUG, file_sz = int(1e6), num_files = 5):
        super().__init__(name, logging.NOTSET, filename, file_level, file_sz, num_files)
        self._file_sz = file_sz
        self._num_files = num_files

        self._validate_num_handlers(1)

        if self._file_sz <= 0:
            raise aLogInputArgError('Expected a positive file size (in bytes), instead got "{}"'.format(self._file_sz))
        
        if self._num_files <= 0:
            raise aLogInputArgError('Expected a positive integer representing the number of backup files, instead got "{}"'.format(self._num_files))
        
        if not self._filename:
            raise aLogInputArgError('Expected a valid filename to use for logging purposes, instead got "{}"'.format(self._filename))

        self._add_handlers()
    
    def _add_handlers(self):
        handlers = self._find_matching_handlers((logging.handlers.RotatingFileHandler))
        for handler in handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                hndl_name = getattr(handler.stream, 'name', '')
                if hndl_name == self._filename: # TODO: Verify this works same as FileHandler
                    # don't make one, it's already there
                    return
                else:
                    raise aLogUnknownHandlers('Found RotatingFileHandler in logger with an unknown file (got "{}", expected "{}")'.format(hndl_name, self._filename))
        
        fp = logging.handlers.RotatingFileHandler(filename=self._filename,maxBytes=self._file_sz, backupCount=self._num_files)
        fp.setLevel(level=self._file_level)
        fp.setFormatter(self._get_format())
        self._logger.addHandler(fp)


class Logger(logger):
    _file_sz = 0
    _num_files = 0
    
    def __init__(self, name = 'root', print_level = logging.INFO, filename = '', file_level = logging.DEBUG, file_sz = int(1e6), num_files = 5):
        super().__init__(name, print_level, filename, file_level, file_sz, num_files)
        self._file_sz = file_sz
        self._num_files = num_files

        self._validate_num_handlers(2)

        if self._file_sz <= 0:
            raise aLogInputArgError('Expected a positive file size (in bytes), instead got "{}"'.format(self._file_sz))
        
        if self._num_files <= 0:
            raise aLogInputArgError('Expected a positive integer representing the number of backup files, instead got "{}"'.format(self._num_files))
        
        if not self._filename:
            raise aLogInputArgError('Expected a valid filename to use for logging purposes, instead got "{}"'.format(self._filename))

        self._add_handlers()
    
    def _add_handlers(self):
        found_logger = False
        ch = logging.StreamHandler()
        ch_name = getattr(ch.stream, 'name', '')
        handlers = self._find_matching_handlers((logging.StreamHandler))
        for handler in handlers:
            if isinstance(handler, logging.StreamHandler):
                hndl_name = getattr(handler.stream, 'name', '')
                if hndl_name == ch_name:
                    # don't make one, it's already there
                    found_logger = True
                else:
                    raise aLogUnknownHandlers('Found unknown StreamHandler in logger (got "{}", expected "{}")'.format(hndl_name, ch_name))
        
        if not found_logger:
            ch.setLevel(level=self._print_level)
            ch.setFormatter(self._get_format())
            self._logger.addHandler(ch)

        # make file handler
        handlers = self._find_matching_handlers((logging.handlers.RotatingFileHandler))
        for handler in handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                hndl_name = getattr(handler.stream, 'name', '')
                if hndl_name == self._filename: # TODO: Verify this works same as FileHandler
                    # don't make one, it's already there
                    return
                else:
                    raise aLogUnknownHandlers('Found RotatingFileHandler in logger with an unknown file (got "{}", expected "{}")'.format(hndl_name, self._filename))
        
        fp = logging.handlers.RotatingFileHandler(filename=self._filename,maxBytes=self._file_sz, backupCount=self._num_files)
        fp.setLevel(level=self._file_level)
        fp.setFormatter(self._get_format())
        self._logger.addHandler(fp)


__all__ = [
    "SimpleLogger",
    "SilentLogger",
    "SilentRotatingLogger",
    "Logger"
]
# -*- coding: utf-8 -*-

import logging
import sys

import conf

g_Log = None

def debug(format, *tupleArg):
    #g_Log.debug(format, *tupleArg)
    print (format)


def info(format, *tupleArg):
    #g_Log.info(format, *tupleArg)
    print (format)


def warn(format, *tupleArg):
    #g_Log.warn(format, *tupleArg)
    print (format)


def error_stack(format, *tupleArg):
    #g_Log.error(format, *tupleArg, exc_info = True)
    print (format)


def error(format, *tupleArg):
    #g_Log.error(format, *tupleArg)
    print (format)


def exception(format, *tupleArg):
    #g_Log.exception(format, *tupleArg)
    print (format)
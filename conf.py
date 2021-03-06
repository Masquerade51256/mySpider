# -*- coding: utf-8 -*-

import os
import configparser

USER_DATA_DIR = ''
DOWNLOADS_DIR = ''

USER_ACCOUNT_NAME = ''
USER_ACCOUNT_PWD = ''

CONFIG_FILE_NAME = ''
COOKIE_FILE_NAME = ''
DB_FILE_NAME = ''
DB_DEF_FILE_NAME = ''
LOG_FILE_NAME = ''

def GetUserDataDir():
    global USER_DATA_DIR
    if USER_DATA_DIR == '':
        USER_DATA_DIR = os.path.join('pixivspider-data')
        if not os.path.exists(USER_DATA_DIR):
            os.makedirs(USER_DATA_DIR)
    return USER_DATA_DIR

def GetConfigFilePath():
    global CONFIG_FILE_NAME
    if CONFIG_FILE_NAME == '':
        CONFIG_FILE_NAME = os.path.join(GetUserDataDir(), 'config.ini')
    return CONFIG_FILE_NAME

def GetAccountName():
    global USER_ACCOUNT_NAME
    if USER_ACCOUNT_NAME == '':
        config = configparser.ConfigParser()
        config.read(GetConfigFilePath())
        USER_ACCOUNT_NAME = config.get('account', 'pixiv_id')
    return USER_ACCOUNT_NAME

def GetAccountPwd():
    global USER_ACCOUNT_PWD
    if USER_ACCOUNT_PWD == '':
        config = configparser.ConfigParser()
        config.read(GetConfigFilePath())
        USER_ACCOUNT_PWD = config.get('account', 'pixiv_password')
    return USER_ACCOUNT_PWD

def GetDownloadsDir():
    global DOWNLOADS_DIR
    if DOWNLOADS_DIR == '':
        DOWNLOADS_DIR = os.path.join(GetUserDataDir(), 'downloads')
        if not os.path.exists(DOWNLOADS_DIR):
            os.makedirs(DOWNLOADS_DIR)
    return DOWNLOADS_DIR

def GetCookiePath():
    global COOKIE_FILE_NAME
    if COOKIE_FILE_NAME == '':
        COOKIE_FILE_NAME = os.path.join(GetUserDataDir(), 'PixivCookie.txt')
        print (COOKIE_FILE_NAME)
    return COOKIE_FILE_NAME

def GetDBPath():
    global DB_FILE_NAME
    if DB_FILE_NAME == '':
        DB_FILE_NAME = os.path.join(GetUserDataDir(), 'download.db')
    return DB_FILE_NAME


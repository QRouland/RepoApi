import os


class ConfigProd(object):
    DEBUG = False
    TESTING = False
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    REPOS_JSON_CONFIG_PATH = "repos.json"


class ConfigDebug(ConfigProd):
    DEBUG = True


CURRENT_CONFIG = ConfigProd
from singleton import singleton
import yaml


# Other constants
READ_MODE = 'r'
DEFAULT_CONFIG_PATH = 'config.example.yaml'

###########################
# Configuration file keys #
###########################

# Flask
FLASK_KEY = 'flask'
PORT_KEY = 'port'
HOST_KEY = 'host'
THREADED_KEY = 'threaded'
RELOADER_KEY = 'use_reloader'

# Cluster
CLUSTER_KEY = 'cluster'
NODES_LIST_KEY = 'nodes'

# This current node
NODE_KEY = 'node'
PERSIST_KEY = 'persist'
NAME_KEY = 'name'
LOG_KEY = 'log'
PATH_KEY = 'path'
HANDLER_KEY = 'handler'


@singleton
class Configuration(object):
    def __init__(self, path=DEFAULT_CONFIG_PATH):
        self.__stream__ = open(path, READ_MODE)
        self.__struct__ = yaml.safe_load(self.__stream__)
        self.__struct_to_properties__()

    def __struct_to_properties__(self):
        struct = self.__struct__
        flask_config = struct[FLASK_KEY]
        cluster_config = struct[CLUSTER_KEY]
        self_config = struct[NODE_KEY]

        # Set flask options
        self.port = flask_config[PORT_KEY]
        self.host = flask_config[HOST_KEY]
        self.threaded = flask_config[THREADED_KEY]
        self.reloader = flask_config[RELOADER_KEY]

        # Set cluster options
        self.node_list = cluster_config[NODES_LIST_KEY]

        # Set self options
        self.persist = self_config[PERSIST_KEY]
        self.name = self_config[NAME_KEY]

        log_options = self_config[LOG_KEY]
        self.log_path = log_options[PATH_KEY]
        self.log_handler = log_options[HANDLER_KEY]

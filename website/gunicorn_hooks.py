import os

from log_services import logger_logout
from web_config import print_verbose, website_config

website_config['VERBOSE'] = True


def clean_up():
    """
    Called after every worker dies.
    :return:
    """
    logger_logout()


def on_starting(server):
    """
    Called when the server boot up (just once)
    :param server:
    :return:
    """
    print_verbose(sender="Master", color="cyan",
                  message=f"Booting withCPUs: {int(os.environ['CORES'])} ({int(os.environ['CORES']) * 2 + 1} Workers) "
                          f"with {int(os.environ['THREADS'])} Threads")


def when_ready(server):
    """
    Called when the server is done loading and is ready (just once)
    :param server:
    :return:
    """
    print_verbose(sender="Master", color="green", message="Server Initialization Complete!")


def on_exit(server):
    """
    Called when the server exits (just once)
    :param server:
    :return:
    """
    clean_up()


def worker_abort(worker):
    """
    Called when a worker receives a SIGABRT signal (generally a timeout)
    :param worker:
    :return:
    """
    print_verbose(sender=worker, color="red", message="Worker aborted")
    clean_up()


def worker_int(worker):
    """
    Called when a worker receives a SIGINT or SIGQUIT signal (normal behavior)
    :param worker:
    :return:
    """
    print_verbose(sender="Worker", message="Worker interrupted")
    clean_up()


def post_worker_init(worker):
    """
    Called when a worker finishes being initialized
    :param worker:
    :return:
    """
    pass


def pre_request(worker, req):
    """
    Called just before a worker handles a request
    :param worker:
    :param req: The request
    :return:
    """
    pass


def post_request(worker, req, environ, resp):
    """
    Called after a process have been processed by the worker
    :param worker:
    :param req:
    :param environ:
    :param resp:
    :return:
    """
    pass

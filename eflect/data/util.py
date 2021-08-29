""" Helper methods for sampling. """

from time import time

def get_unixtime(timestamp=None):
    """ Gets unixtime as ms or converts a ctime to unixtime. """
    if timestamp is None:
        return int(10 ** 3 * time())
    else:
        return int(10 ** 3 * timestamp)

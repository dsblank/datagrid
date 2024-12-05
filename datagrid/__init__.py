# -*- coding: utf-8 -*-
######################################################
#     _____                  _____      _     _      #
#    (____ \       _        |  ___)    (_)   | |     #
#     _   \ \ ____| |_  ____| | ___ ___ _  _ | |     #
#    | |  | )/ _  |  _)/ _  | |(_  / __) |/ || |     #
#    | |__/ ( ( | | | ( ( | | |__| | | | ( (_| |     #
#    |_____/ \_||_|___)\_||_|_____/|_| |_|\____|     #
#                                                    #
#    Copyright (c) 2023-2024 Kangas Development Team #
#    All rights reserved                             #
######################################################

import os
import sys
import time
import urllib

from ._version import __version__  # noqa
from ._datatypes import (  # noqa
    _DataGrid,
)
from .server.queries import sqlite_query, sqlite_query_explain  # noqa
from .utils import (
    _in_colab_environment,
    _in_jupyter_environment,
    _in_kaggle_environment,
    _is_running,
    get_localhost,
    terminate,
)

def read_datagrid(filename, **kwargs):
    """
    Reads a DataGrid from a filename or URL. Returns
    the DataGrid.

    Args:
        filename: the name of the file or URL to read the DataGrid
            from

    Note: the file or URL may end with ".zip", ".tgz", ".gz", or ".tar"
        extension. If so, it will be downloaded and unarchived. The JSON
        file is assumed to be in the archive with the same name as the
        file/URL. If it is not, then please use the datagrid.download()
        function to download, and then read from the downloaded file.

    Examples:

    ```python
    >>> import datagrid
    >>> dg = datagrid.read_datagrid("example.datagrid")
    >>> dg = datagrid.read_datagrid("http://example.com/example.datagrid")
    >>> dg = datagrid.read_datagrid("http://example.com/example.datagrid.zip")
    >>> dg.save()
    ```
    """
    return _DataGrid.read_datagrid(filename, **kwargs)



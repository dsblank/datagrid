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
from .datatypes import *
from ._datatypes import (  # noqa
    _DataGrid,
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


def download(url, ext=None):
    """
    Downloads a file, and unzips, untars, or ungzips it.

    Args:
        url: (str) the URL of the file to download
        ext: (optional, str) the format of the archive: "zip",
            "tgz", "gz", or "tar".

    Note: the URL may end with ".zip", ".tgz", ".gz", or ".tar"
        extension. If so, it will be downloaded and unarchived.
        If the URL doesn't have an extension or it does not match
        one of those, but it is one of those, you can override
        it using the `ext` argument.

    Example:

    ```python
    >>> import datagrid
    >>> datagrid.download("https://example.com/example.images.zip")
    ```
    """
    return _DataGrid.download(url, ext)



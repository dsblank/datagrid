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
    new_datagrid_version_available,
    terminate,
)

if new_datagrid_version_available():
    print("A new Kangas version is available", file=sys.stderr)


def launch(
    host=None, port=4000, debug=None, protocol="http", hide_selector=None, **cli_kwargs
):
    """
    Launch the Kangas servers.

    Note: this should never be needed as the Kangas
          servers are started automatically when needed.

    Args:
        host: (str) the name or IP of the machine the
            servers should listen on.
        port: (int) the port of the Kangas frontend server. The
            backend server will start on port + 1.
        debug: (str) the debugging output level will be
            shown as you run the servers.

    Example:

    ```python
    >>> import datagrid
    >>> datagrid.launch()
    ```
    """
    import subprocess

    host = host if host is not None else get_localhost()
    hide_selector = (
        hide_selector if hide_selector is not None else _in_jupyter_environment()
    )

    if not _is_running("node", "datagrid"):
        print("Terminating any stray Kangas servers...")
        terminate()
        command_line = [
            sys.executable,
            "-m",
            "datagrid.cli.server",
            "--frontend-port",
            str(port),
            "--backend-port",
            str(port + 1),
            "--open",
            "no",
            "--protocol",
            protocol,
        ]
        if host is not None:
            command_line.extend(["--host", host])

        if hide_selector:
            command_line.extend(["--hide-selector"])

        if debug is not None:
            command_line.extend(["--debug-level", debug])

        if cli_kwargs:
            for flag in cli_kwargs:
                command_line.extend(["--%s" % flag, str(cli_kwargs[flag])])

        subprocess.Popen(command_line)

        # FIXME: can we poll until it is ready?
        time.sleep(0.5)
        print("Starting Kangas server in 3...")
        time.sleep(1)
        print("Starting Kangas server in 2...")
        time.sleep(1)
        print("Starting Kangas server in 1...")
        time.sleep(1)

    return "%s://%s:%s/" % (protocol, host, port)


def show(
    datagrid=None,
    filter=None,
    host=None,
    port=4000,
    debug=None,
    height="750px",
    width="100%",
    protocol="http",
    hide_selector=False,
    use_ngrok=False,
    cli_kwargs=None,
    **kwargs
):
    """
    Start the Kangas servers and show the DatGrid UI
    in an IFrame or browser.

    Args:
        datagrid: (str) the DataGrid's location from current
            directory
        filter: (str) a filter to set on the DataGrid
        host: (str) the name or IP of the machine the
            servers should listen on.
        port: (int) the port of the Kangas frontend server. The
            backend server will start on port + 1.
        debug: (str) debugging output level will be
            shown as you run the servers.
        height: (str) the height (in "px" pixels) of the
            iframe shown in the Jupyter notebook.
        width: (str) the width (in "px" pixels or "%" percentages) of the
            iframe shown in the Jupyter notebook.
        use_ngrok: (optional, bool) force using ngrok as a proxy
        cli_kwargs: (dict) a dictionary with keys the names
            of the datagrid server flags, and values the setting value
            (such as: `{"backend-port": 8000}`)
        kwargs: additional URL parameters to pass to server

    Example:

    ```python
    >>> import datagrid
    >>> datagrid.show("./example.datagrid")
    >>> datagrid.show("./example.datagrid", "{'Column Name'} < 0.5")
    >>> datagrid.show("./example.datagrid", "{'Column Name'} < 0.5",
    ...     group="Another Column Name")
    ```
    """
    url = launch(
        host, port, debug, protocol, hide_selector, **(cli_kwargs if cli_kwargs else {})
    )

    if datagrid:
        query_vars = {
            "datagrid": datagrid,
            "timestamp": os.path.getmtime(datagrid),
        }
        query_vars.update(kwargs)
        if filter:
            query_vars["filter"] = filter
        qvs = "?" + urllib.parse.urlencode(query_vars)
        url = "%s%s" % (url, qvs)
    else:
        qvs = ""

    if _in_kaggle_environment() or use_ngrok:
        from IPython.display import IFrame, clear_output, display

        try:
            from pyngrok import ngrok  # noqa
        except ImportError:
            raise Exception(
                "pyngrok is required for use in kaggle; pip install pyngrok"
            ) from None

        from .kaggle_env import init_kaggle

        tunnel = init_kaggle(port)
        url = "%s%s" % (tunnel.public_url, qvs)

        if _in_jupyter_environment():
            clear_output(wait=True)
            display(IFrame(src=url, width=width, height=height))
        else:
            import webbrowser

            webbrowser.open(url, autoraise=True)

    elif _in_colab_environment():
        from IPython.display import clear_output

        from .colab_env import init_colab

        clear_output(wait=True)
        init_colab(port, width, height, qvs)

    elif _in_jupyter_environment():
        from IPython.display import IFrame, clear_output, display

        clear_output(wait=True)
        display(IFrame(src=url, width=width, height=height))

    else:
        import webbrowser

        webbrowser.open(url, autoraise=True)


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
    return DataGrid.download(url, ext)




def _jupyter_server_extension_paths():
    return [{
        "module": "ilot"
    }]

    # Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="ilot",
        # _also_ in the `nbextension/` namespace
        require="ilot/index")]

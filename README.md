# DropBot signals MicroDrop plugin #

This plugin demonstrates how to connect to DropBot signals, e.g., capacitance
updates, connected, disconnected, etc.

The following signals are logged:

 - `capacitance-updated`
 - `channels-updated`
 - `chip-inserted`
 - `chip-removed`
 - `connected`
 - `disconnected`

-------------------------------------------------------------------------------

Install
-------

The latest [`microdrop.dropbot-signals-plugin` release][1] is available as a
[Conda][2] package from the [`sci-bots`][2] channel.

To install `microdrop.dropbot-signals-plugin` in an **activated Conda environment**, run:

    conda install -c sci-bots -c conda-forge microdrop.dropbot-signals-plugin

-------------------------------------------------------------------------------

Develop
-------

 1. Install dependencies listed in `requirements.host` section of
    [`.conda-recipe/meta.yaml`](/.conda-recipe/meta.yaml).
 2. Run the following command from the repository root:
 ```
 python -m mpm.bin.build -p microdrop.dropbot-signals-plugin --properties-only -s . -t .
 ```
 3. Select or create directory as root to hold development plugins, e.g.,
 ```
 mkdir %USERPROFILE%\microdrop-dev-plugins
 ```
 4. Create link to repo directory in development root with import-friendly
    **_plugin_** name, e.g.:
 ```sh
 mklink /J %USERPROFILE%\microdrop-dev-plugins\dropbot_signals_plugin %REPO_DIR%
 ```
 5. Add development plugins directory to `;`-separated list of paths in
    `MICRODROP_PLUGINS_PATH` environment variable.

-------------------------------------------------------------------------------

License
-------

This project is licensed under the terms of the [BSD license](/LICENSE.md)

-------------------------------------------------------------------------------

Contributors
------------

 - Christian Fobel ([@cfobel](https://github.com/cfobel))


[1]: https://github.com/sci-bots/microdrop.dropbot-signals-plugin
[2]: https://anaconda.org/sci-bots/microdrop.dropbot-signals-plugin

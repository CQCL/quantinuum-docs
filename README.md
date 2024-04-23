# Sphinx docs sandbox

This is a repo for testing out things with Sphinx builds.

## Current branch: TKET manual process

This uses jupyter-sphinx to execute code that's embedded in an .rst file,
and display the output.

To build, cd to the `content` directory and run:

  poetry run sphinx-build -b html . build -W

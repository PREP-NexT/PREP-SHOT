#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py: PREP-SHOT Entry Point
=============================

██████   ██████   ███████  ██████            ███████  █     █   █████   ███████
█     █  █     █  █        █     █           █        █     █  █     █     █
█     █  █     █  █        █     █           █        █     █  █     █     █
██████   ██████   ███████  ██████   ███████  ███████  ███████  █     █     █
█        █   █    █        █                       █  █     █  █     █     █
█        █    █   █        █                       █  █     █  █     █     █
█        █     █  ███████  █                 ███████  █     █   █████      █

Run PREP-SHOT against a self-contained scenario directory (one of the
shipped ``examples/`` folders, or your own copy of that layout).

A scenario directory contains:

    <scenario>/config.json       general parameters
    <scenario>/params.json       input-file map
    <scenario>/input/            input CSVs
    <scenario>/output/           results land here (auto-created)

Two equivalent invocations:

.. code-block:: bash

    cd examples/three_zone
    python -m prepshot
    # OR (from any directory)
    python /path/to/run.py /path/to/examples/three_zone

If invoked without a path argument, ``run.py`` uses the current
working directory.

See :mod:`prepshot.cli` for the underlying entry point.
"""
import os
import sys

from prepshot.cli import main


if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        # Optional positional arg: scenario directory
        root_dir = os.path.abspath(sys.argv[1])
        # Strip the consumed positional so prepshot.set_up.parse_cli_arguments
        # only sees the per-input scenario flags (e.g. --demand=high).
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    else:
        root_dir = os.getcwd()
    main(root_dir=root_dir)

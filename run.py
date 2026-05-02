#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py: PREP-SHOT Entry Point (legacy)
======================================

██████   ██████   ███████  ██████            ███████  █     █   █████   ███████
█     █  █     █  █        █     █           █        █     █  █     █     █
█     █  █     █  █        █     █           █        █     █  █     █     █
██████   ██████   ███████  ██████   ███████  ███████  ███████  █     █     █
█        █   █    █        █                       █  █     █  █     █     █
█        █    █   █        █                       █  █     █  █     █     █
█        █     █  ███████  █                 ███████  █     █   █████      █

Backward-compatible entry point. Looks for ``config.json`` and
``params.json`` next to this file (i.e. the repo root). Equivalent to::

    python run.py

After ``pip install`` (or ``pip install -e .``) the same flow can be
launched from any working directory containing the two config files via::

    prepshot
    # or
    python -m prepshot

See :mod:`prepshot.cli` for the underlying entry point.
"""
import os

from prepshot.cli import main


if __name__ == "__main__":
    main(root_dir=os.path.dirname(os.path.abspath(__file__)))

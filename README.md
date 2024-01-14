<p align="center">
  <a href="https://prep-next.github.io/PREP-SHOT/">
    <img src="https://user-images.githubusercontent.com/50036800/221886195-3113531b-f9c4-4c6a-bb66-612c8b9c3d9a.png" width="550" alt="PREP-SHOT logo">
  </a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img alt="Build" src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg?color=purple"></a>
  <a href="https://github.com/PREP-NexT/PREP-SHOT"><img src="https://img.shields.io/github/contributors/PREP-NexT/PREP-SHOT.svg" alt="GitHub contributors"></a>
  <a href="https://github.com/PREP-NexT/PREP-SHOT"><img src="https://img.shields.io/github/issues/PREP-NexT/PREP-SHOT.svg" alt="GitHub issues"></a>
  <a href="https://twitter.com/PREPNexT_Lab"><img src="https://img.shields.io/twitter/follow/PREPNexT_Lab.svg?label=Follow&style=social" alt="Twitter Follow"></a>
  <a href="https://github.com/PREP-NexT/PREP-SHOT"><img src="https://img.shields.io/github/license/PREP-NexT/PREP-SHOT.svg" alt="License"></a>
  <a href="https://github.com/PREP-NexT/PREP-SHOT"><img src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" alt="Download"></a>
</p>

<p align="center">
  <a href="#overview">Overview</a> |
  <a href="#key-features">Features</a> |
  <a href="#getting-started">Quick Start</a> |
  <a href="#how-to-contribute">Contribute</a> |
  <a href="#citation">Citation</a>
</p>

## Overview

**PREP-SHOT** (**P**athways for **R**enewable **E**nergy **P**lanning coupling **S**hort-term **H**ydropower **O**pera**T**ion) is a transparent, modular, and open-source energy expansion model, offering advanced solutions for multi-scale, intertemporal, and cost-effective expansion of energy systems and transmission lines. It's developed by [Zhanwei Liu](https://www.researchgate.net/profile/Zhanwei-Liu-4) and [Xiaogang He](http://hydro.iis.u-tokyo.ac.jp/~hexg/) from the [PREP-NexT](https://github.com/PREP-NexT) Lab at the [National University of Singapore](https://nus.edu.sg/).

For more information, please visit our [Official Documentation](https://prep-next.github.io/PREP-SHOT/).

This project is licensed under the [GNU General Public License 3.0](https://github.com/PREP-NexT/PREP-SHOT/blob/main/LICENSE).

## Key Features

- Optimization model based on linear programming for multi-zone energy systems.
- Cost minimization while meeting given demand time series.
- Adjustable operation on hourly-spaced time steps.
- Input data in Excel format and output data in NetCDF format using ``Xarray``.
- Support for multiple solvers like Gurobi, CPLEX, MOSEK, and GLPK via `Pyomo`.
- Allows input of multiple scenarios for specific parameters.
- A pure Python program, leveraging ``pandas`` and ``Xarray`` for simplified complex data analysis and extensibility.

## Getting Started

This section includes a brief tutorial on running your first PREP-SHOT model.

1. Clone the repo

    ```bash
    git clone https://github.com/PREP-NexT/PREP-SHOT.git
    ```

2. Create the Conda Environment and install the dependencies

    ```bash
    conda env create -f prep-shot.yml
    ```

3. Activate the Conda Environment

    ```bash
    conda activate prep-shot-test
    ```

4. Run your first model

    ```bash
    python run.py
    ```

This example is inspired by real-world data. For a detailed elaboration of this tutorial, check out the [Tutorial Page](https://prep-next.github.io/PREP-SHOT/Tutorial.html) in our documentation.

## How to Contribute

To contribute to this project, please read our [Contributing Guidelines](https://prep-next.github.io/PREP-SHOT/Changelog.html#contributing-to-prep-shot).

## Citation

If you use PREP-SHOT in a scientific publication, we would appreciate citations. You can use the following BibTeX entry:

```bibtex
@article{liu2023,
  title = {Balancing-oriented hydropower operation makes the clean energy transition more affordable and simultaneously boosts water security},
  author = {Liu, Zhanwei and He, Xiaogang},
  journal = {Nature Water},
  volume = {1},
  pages = {778--789},
  year = {2023},
  doi = {10.1038/s44221-023-00126-0},
}
```

## Contact Us

If you have any questions, comments, or suggestions that aren't suitable for public discussions in the Issues section, please feel free to reach out to [Zhanwei Liu](mailto:liuzhanwei@u.nus.edu).

Please use the GitHub Issues for public discussions related to bugs, enhancements, or other project-related discussions.

## Roadmap

+ `Benders` decomposition-based fast solution framework
+ `JuMP`-based low-memory and fast modelling engine
+ Support for input of cost–supply curves of technologies
+ Support for expanding conventional hydropower plants
+ Support for refurbishing conventional hydropower plants to pumped-storage schemes
+ Support for refurbishing carbon-emission plants to carbon capture and storage (CCS) schemes

## Disclaimer

The PREP-SHOT model is an academic project and is not intended to be used as a precise prediction tool for specific hydropower operations or energy planning. The developers will not be held liable for any decisions made based on the use of this model. We recommend applying it in conjunction with expert judgment and other modeling tools in a decision-making context.

---

![Repo Analytics](https://repobeats.axiom.co/api/embed/159a603ee4c6124a5addc35d47b3cb02e3fc39f0.svg "Repo analytics")

.. _Contribution:

Contribution
=================

We welcome and appreciate contributions for the RPEP-SHOT library. Here are the steps to contribute:

Development Process
+++++++++++++++++++++++++++++++

1. **Create an Issue**

   If you find a bug or have an idea for an improvement or new feature, please create an `issue <https://github.com/PREP-NexT/PREP-SHOT/issues>`_.

2. **Fork the Repository**
   
   You can fork the `PREP-SHOT repository <https://github.com/PREP-NexT/PREP-SHOT>`_ on GitHub.

3. **Create a Branch**

   Create a new branch in your forked repository and name the branch according to the feature or fix you're working on.

4. **Commit Changes**

   Make changes in your branch. Once you've made improvements or bug fixes to the project, commit the changes with a meaningful commit message.

5. **Run Tests**
   To execute all tests, navigate to the root directory of PREP-SHOT and run:

.. code:: bash

    python -m unittest discover -s tests

To check your code for PEP8 compliance, run:

.. code:: bash

    pylint run.py
    pylint prepshot

6. **Start a Pull Request**

   Open a `pull request <https://github.com/PREP-NexT/PREP-SHOT/pulls>`_ from your forked repository to the main PREP-SHOT repository. Describe your changes in the pull request.

7. **Code Review**

   Maintainers of the PREP-SHOT project will review your code. They may ask for changes or improvements before the code is merged into the main codebase.

Please ensure that you update tests as necessary when you're contributing code, and follow the coding conventions established in the rest of the project.

Building Documentation
+++++++++++++++++++++++++++++++

The documentation is built using Sphinx. To build the documentation, you need to install the required packages using the following command:

.. code:: bash

    pip install -r docs/requirements.txt

You can build the documentation using the following command:

.. code:: bash

    cd doc
    make clean
    make html


The documentation will be built in the `doc/build` directory.

Contributing Guidelines
+++++++++++++++++++++++++++++++

PREP-SHOT is written in Python and follows the PEP8 coding standard. Please ensure that your code follows the PEP8 coding standard. You can use the `Pylint <https://pylint.readthedocs.io/en/stable/>`_ tool to check your code for PEP8 compliance.


Translating the Documentation
+++++++++++++++++++++++++++++++

Translations live in-tree at ``doc/source/locale/<lang>/LC_MESSAGES/*.po``
(one ``.po`` file per RST source file). The shipped Chinese (``zh_CN``)
translation is incomplete; only the :ref:`Glossary` is currently
translated. Help with the rest is welcome.

**To translate (or update) a single page:**

.. code-block:: bash

    # 1. Extract / refresh the .pot template files from the English RST
    sphinx-build -b gettext doc/source doc/build/gettext

    # 2. Update the .po files for your target language
    sphinx-intl update -p doc/build/gettext -l zh_CN -d doc/source/locale

    # 3. Edit doc/source/locale/zh_CN/LC_MESSAGES/<page>.po
    #    Fill in the empty msgstr "" entries with translations.

    # 4. Compile .po -> .mo and build the Chinese site locally
    sphinx-intl build -d doc/source/locale
    READTHEDOCS_LANGUAGE=zh_CN sphinx-build -b html doc/source doc/build/html-zh

    # 5. Check the result in doc/build/html-zh/, then commit only the
    #    .po files (the .mo is regenerated on every build).

**Adding a new language.** Pick the locale code (e.g. ``ja``,
``de``, ``es``) and uncomment the entry in ``supported_languages``
in ``doc/source/conf.py``. Then run step 2 above with your locale
code instead of ``zh_CN``. Once at least one page is meaningfully
translated, request that a maintainer create the corresponding
"translation" project on Read the Docs so the language switcher
picks it up.

**Reviewing a translation.** Native speakers are very welcome to
review translated ``.po`` files for tone and accuracy. Open a PR
with your suggested changes; tag a maintainer for merging.

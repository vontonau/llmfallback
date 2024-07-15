![license](https://img.shields.io/badge/license-MIT-blue) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-yellow?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) [![conventional-commits](https://img.shields.io/badge/conventional%20commits-1.0.0-yellow)](https://www.conventionalcommits.org/en/v1.0.0/) [![black](https://img.shields.io/badge/code%20style-black-000000)](https://github.com/psf/black) [![mypy](https://img.shields.io/badge/mypy-checked-brightgreen)](http://mypy-lang.org/) [![pylint](https://img.shields.io/badge/pylint-required%2010.0-brightgreen)](http://pylint.org/) [![pytest](https://img.shields.io/badge/pytest-enabled-brightgreen)](https://github.com/pytest-dev/pytest) [![coverage](https://img.shields.io/badge/coverage-required%20100%25-brightgreen)](https://github.com/nedbat/coveragepy) [![hypothesis](https://img.shields.io/badge/hypothesis-tested-brightgreen.svg)](https://hypothesis.readthedocs.io/)

# LLMFallback

This repository hosts a LLMFallback package - a wrapper for LLM calls that automatically detects failures and redirects call to the next-preferred model.

## How to use it?


## Supported LLMs


## Testing

This repository is set up to use [pytest](https://pytest.org/) either standalone or as a pre-push git hook. Tests are stored in the `tests/` folder, and you can run them manually like so:
```bash
make test
```
which runs all tests in both your local Python virtual environment. For more options, see the [pytest command-line flags](https://docs.pytest.org/en/7.4.x/reference/reference.html#command-line-flags). Also note that pytest includes [doctest](https://docs.python.org/3/library/doctest.html), which means that module and function [docstrings](https://www.python.org/dev/peps/pep-0257/#what-is-a-docstring), as well as the documentation, may contain test code that executes as part of the unit tests.

Both statement and branch coverage are being tracked using [coverage](https://github.com/nedbat/coveragepy) and the [pytest-cov](https://github.com/pytest-dev/pytest-cov) plugin for pytest, and it measures how much code in the `src/package/` folder is covered by tests:
```
Run unit tests...........................................................Passed
- hook id: pytest
- duration: 0.6s

============================= test session starts ==============================
platform darwin -- Python 3.11.7, pytest-7.4.4, pluggy-1.3.0 -- /path/to/python-package-template/.venv/bin/python
cachedir: .pytest_cache
hypothesis profile 'default-with-verbose-verbosity-with-explain-phase' -> max_examples=500, verbosity=Verbosity.verbose, phases=(Phase.explicit, Phase.reuse, Phase.generate, Phase.target, Phase.shrink, Phase.explain), database=DirectoryBasedExampleDatabase('/path/to/python-package-template/.hypothesis/examples')
rootdir: /path/to/python-package-template
configfile: pyproject.toml
plugins: custom-exit-code-0.3.0, cov-4.1.0, doctestplus-1.1.0, hypothesis-6.90.0, env-1.1.1
collected 3 items

src/package/something.py::package.something.Something.do_something PASSED [ 33%]
tests/test_something.py::test_something PASSED                            [ 66%]
docs/source/index.rst::index.rst PASSED                                   [100%]

---------- coverage: platform darwin, python 3.11.7-final-0 ----------
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
src/package/__init__.py        1      0      0      0   100%
src/package/something.py       4      0      2      0   100%
----------------------------------------------------------------------
TOTAL                          5      0      2      0   100%

Required test coverage of 100.0% reached. Total coverage: 100.00%
============================ Hypothesis Statistics =============================

tests/test_something.py::test_something:

  - during reuse phase (0.00 seconds):
    - Typical runtimes: < 1ms, of which < 1ms in data generation
    - 1 passing examples, 0 failing examples, 0 invalid examples

  - during generate phase (0.00 seconds):
    - Typical runtimes: < 1ms, of which < 1ms in data generation
    - 1 passing examples, 0 failing examples, 0 invalid examples

  - Stopped because nothing left to do

============================== 3 passed in 0.05s ===============================
```
Note that code that’s not covered by tests is listed under the `Missing` column, and branches not taken too. The net effect of enforcing 100% code and branch coverage is that every new major and minor feature, every code change, and every fix are being tested (keeping in mind that high _coverage_ does not imply comprehensive, meaningful _test data_).

Hypothesis is a package that implements [property based testing](https://en.wikipedia.org/wiki/Software_testing#Property_testing) and that provides payload generation for your tests based on strategy descriptions ([more](https://hypothesis.works/#what-is-hypothesis)). Using its [pytest plugin](https://hypothesis.readthedocs.io/en/latest/details.html#the-hypothesis-pytest-plugin) Hypothesis is ready to be used for this package.

## Generating documentation

As mentioned above, all package code should make use of [Python docstrings](https://www.python.org/dev/peps/pep-0257/) in [reStructured text format](https://www.python.org/dev/peps/pep-0287/). Using these docstrings and the documentation template in the `docs/source/` folder, you can then generate proper documentation in different formats using the [Sphinx](https://github.com/sphinx-doc/sphinx/) tool:

```bash
make docs
```

This example generates documentation in HTML, which can then be found here:

```bash
open docs/_build/html/index.html
```

In addition to the default HTML, Sphinx also generates Markdown documentation compatible with [Github Wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis), and the [Wiki Documentation](https://github.com/jenstroeger/python-package-template/blob/main/.github/workflows/_wiki-documentation.yaml) Action automatically updates the project repository’s Wiki.

## Synchronizing with template repo

The [sync-with-upstream.yaml](https://github.com/jenstroeger/python-package-template/blob/main/.github/workflows/sync-with-upstream.yaml) GitHub Acions workflow checks template repo daily and automatically creates a pull request in the downstream repo if there is a new release.

## Versioning, publishing and changelog

To enable automation for [semantic versioning](https://semver.org/), package publishing, and changelog generation it is important to use meaningful [conventional commit messages](https://www.conventionalcommits.org/)! This package template already has a built-in semantic release support enabled which is set up to take care of all three of these aspects — every time changes are pushed to the `main` branch.

With every package release, a new `bump:` commit is pushed to the `main` branch and tagged with the package’s new version. In addition, the `staging` branch (which this repository uses to stage merged pull requests into for the next release) is rebased on top of the updated `main` branch automatically, so that subsequent pull requests can be merged while keeping a [linear history](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-linear-history).

If you’d like to receive Slack notifications whenever a new release is published, follow the comments in the [Release Notification](https://github.com/jenstroeger/python-package-template/tree/main/.github/workflows/_release-notifications.yaml) Action and set up a Slack bot by following [the instructions here](https://github.com/slackapi/slack-github-action#setup-2).

In order to build a distribution of your package locally instead of publishing it through the Github Actions workflow, you can simply call:

```bash
make dist
```

This builds a source package and a binary distribution, and stores the files in your local `dist/` folder.

You can also generate a changelog and bump the version manually and locally using commitizen (already installed as a dev dependency), for example:

```bash
cz changelog
cz bump
```

## Build integrity using SLSA framework

The build process in this repository follows the requirements in the [SLSA framework](https://slsa.dev/) to be compliant at level 3. An important aspect of SLSA to improve the supply chain security posture is to generate a verifiable provenance for the build pipeline. Such a provenance can be used to verify the builder and let the consumers check the materials and configurations used while building an artifact. In this repository we use the [generic provenance generator reusable workflow](https://github.com/slsa-framework/slsa-github-generator) to generate a provenance that can attest to the following artifacts in every release:

- Binary dist (wheel)
- Source dist (tarball)
- SBOM (CycloneDx format)
- HTML and Markdown Docs
- A [UNIX epoch](https://en.wikipedia.org/wiki/Unix_time) timestamp file of the build time for [reproducible builds](https://reproducible-builds.org/)

To verify the artifact using the provenance follow the instructions in the [SLSA verifier](https://github.com/slsa-framework/slsa-verifier) project to install the verifier tool. After downloading the artifacts and provenance, verify each artifact individually, e.g.,:

```bash
slsa-verifier -artifact-path  ~/Downloads/package-2.2.0.tar.gz -provenance attestation.intoto.jsonl -source github.com/jenstroeger/python-package-template
```
Which should pass and provide the verification details.

## Cleaning up

On occasion it’s useful (and perhaps necessary) to clean up stale files, caches that tools like `mypy` leave behind, or even to nuke the complete virtual environment:

- **Remove distribution artifacts**: `make dist-clean`
- In addition, **remove tool caches and documentation**: `make clean`
- In addition, **remove Python code caches and git hooks**: `make nuke-caches`
- In addition and to **reset everything**, to restore a clean package to start over fresh: `make nuke`

Please be careful when nuking your environment, and make sure you know what you’re doing.

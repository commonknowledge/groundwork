# Style guide

1. All public APIs must be fully documented.

   - We use [Google docstring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). These will at some point be extracted into searchable API docs, so it's important to get this right. A linter will check for you that they are correctly formatted.

2. Aim for 100% test coverage on public APIs.

3. Use type hints.

4. Format your code.

   - Run `make formatting` to do this explicitly.
   - If you run `make bootstrap` to setup the project (as the devcontainer does automatically), you should get pre-commit hooks installed that do this for you.

5. Check that all checks pass before requesting a PR review.
   - You can do this using `make lint`
   - Individual checks are documented at:
     - https://pypi.org/project/darglint/
     - https://pypi.org/project/isort/
     - https://mypy-lang.org/
     - https://pypi.org/project/safety/
     - https://pypi.org/project/bandit/
   - Rules are configured in pyproject.yaml

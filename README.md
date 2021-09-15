# toolkit
Software tools for research, development, & production.

## Develop
``` shell
python3 -m venv venv        # create a virtual env.
. venv/bin/activate[.fish]  # activate env [in fish].
pip install .               # install dependencies.
flit install --symlink --env --python venv/bin/python3  # install a symlinked version for development (within venv)
```

# toolkit
Software tools for research, development, & production.

## Install
``` shell
pip install asmr

# enable autocompletions
eval "$(_ASMR_COMPLETE=bash_source asmr)"   # bash ~/.bashrc
eval "$(_ASMR_COMPLETE=zsh_source asmr)"    # zsh  ~/.zshrc
eval (env _ASMR_COMPLETE=fish_source asmr)  # fish ~/.config/fish/completions/asmr.fish
```

## Develop
``` shell
python3 -m venv venv        # create a virtual env.
. venv/bin/activate[.fish]  # activate env [in fish].
pip install .               # install dependencies.
flit install --symlink --env --python venv/bin/python3  # install a symlinked version for development (within venv)
```

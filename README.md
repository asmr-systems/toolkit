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
#### prerequisites
``` shell
# you must have Python3 installed.

python3 -m pip install flit # install flit.
```
#### setup
``` shell
python3 -m venv venv        # create a virtual env.
. venv/bin/activate[.fish]  # activate env [in fish].
pip install .               # install dependencies.
flit install --symlink --env --python venv/bin/python3  # install a symlinked version for development (within venv). This might not work in a virtualmachine shared folder.
```

#### notes
``` shell
# if you mount the toolkit repo inside a virtualmachine in order to
# develop it within the vm, you will need to create the venv in a separate
# directory (not in the current repo directory.) then everything should work.
```

## Configuration
The configuration directory is, by default, located within `~/.asmr.d/`. This can be changed by setting the `ASMR_HOME` environment variable.

# Maximum Flow by Augmenting Paths in Almost Quadratic Time

An implementation of https://arxiv.org/abs/2406.03648

## Installation
### uv

We use [uv](https://docs.astral.sh/uv/) to manage dependencies. After installing `uv`, run the following command to install the dependencies:

```bash
uv sync
```

Then run the following command to run a Python script:

```bash
uv run <relative-path>
```
or use the following command to run a command in the environment:
```
uv run <command>
```

### Nix

If you use nix, then we provide a `flake.nix` file built on [uv2nix](https://pyproject-nix.github.io/uv2nix/introduction.html), to activate install the dependencies and activate the environment run the following command:

```bash
nix develop
# or
nix develop flake.nix
```

You can now run the Python scripts as usual or use the `uv` commands as above. I personally suggest using `uv` as it is more feature-rich.


## Code style

[Ruff](github.com/astral-sh/ruff) and [basedpyright](https://github.com/DetachHead/basedpyright) are installed, with proper versions, in the `uv` and `nix` environments provided above. Please integrate these tools into your editor as your LSP and linter to ensure that your code is formatted correctly and follows the rules imposed by the type checker.

Both tools should be configured to respect the `pyproject.toml` file in the root of the repository. (They do so by default)


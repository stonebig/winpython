# wppm — dependency trees, offline wheelhouses, portable Pythons

`wppm` complements `pip` on **any** Python environment (it was born in
[WinPython](https://winpython.github.io/), the portable distribution for Windows,
but does not require it). `pip` remains the recommended way to add or remove
packages; `wppm` covers what `pip` doesn't show or do:

- **extras-aware dependency trees**: what does `pandas[test]` pull in? What does
  *each* extra of a package pull in (`pandas[.]`)? Which installed packages use
  `pytest`, through which extra?
- **constraint hunting**: `wppm -r numpy!` shows only the packages that *pin or cap*
  numpy — the ones that will hurt when you upgrade,
- **missing-dependency detection**: trees flag requirements that are not installed
  (`lxml==? >=5.3.0;extra==xml`),
- **JSON everywhere** (`-j`): dependency trees, package lists and environment
  manifests as machine-readable output, for CI gates and diffing,
- **offline wheelhouse tooling**: install from a directory of wheels or a
  `pylock.toml`, inventory a wheelhouse without installing anything (`-ls -ws`),
- **environment manifest** (`-md`): one document — Markdown or JSON — describing the
  distribution, its tools, its packages and its wheelhouse; a lightweight SBOM,
- **portability housekeeping**: make any target Python movable (relative shebangs
  and launchers) or fixed, register/unregister it in Windows.

Compared with `pipdeptree`: `wppm` adds per-`[extra]` granularity in both
directions, the constraining-dependency filter (`!`), missing-dependency flags,
and it can inspect another environment (`-t`) or a plain directory of wheels
(`-ws`) — no need to install anything into it first.

## Examples

What each extra of `pandas` would pull in, one level deep:

```console
wppm -p pandas[.] -l1
```

Which installed packages depend on `pytest` (through which extra), and which ones
constrain it hard (`!`):

```console
wppm -r pytest[test]
wppm -r pytest![test]
```

The full constraint web of your environment — every package, every extra, nine
levels deep:

```console
wppm -p .[.] -l9
```

A JSON inventory of an offline wheel bundle, without installing it:

```console
wppm -ls -ws .\wheelhouse\included.wheels --json
```

A manifest of the current environment (distribution, tools, packages, wheelhouse):

```console
wppm -md --json
```

Fail a CI job if anything in the tree is missing:

```console
wppm -p myapp -j | python -c "import sys,json; s=json.load(sys.stdin); [s.extend(n['depends']) for n in s]; sys.exit(1 if any(not n['installed'] for n in s) else 0)"
```

## Command line

```text
usage: wppm [-h] [-v] [--register] [--unregister] [--fix] [--movable]
            [-ws WHEELSOURCE] [-wd WHEELDRAIN] [-ls] [-lsa] [-md] [-p] [-r]
            [-l LEVELS] [-j] [-t TARGET] [-i] [-u]
            [package(s) or lockfile ...]

WinPython Package Manager: handle a Python distribution (WinPython or not) and its packages

positional arguments:
  package(s) or lockfile
                        optional package names, wheels, or lockfile

options:
  -h, --help            show this help message and exit
  -v, --verbose         show more details on packages and actions
  --register            Register the target Python: associate file extensions, icons and context menu with it (useful for portable distributions like WinPython)
  --unregister          Unregister the target Python: de-associate file extensions, icons and context menu from it
  --fix                 make the target Python use absolute (fixed) paths in launchers and shebangs
  --movable             make the target Python movable/portable: relative paths in launchers and shebangs
  -ws WHEELSOURCE       wheels location, ('.' = WheelHouse): wppm pylock.toml -ws source_of_wheels, wppm -ls -ws .
  -wd WHEELDRAIN        wheels destination: wppm pylock.toml -wd destination_of_wheels
  -ls, --list           list installed packages matching [optional] expression: wppm -ls, wppm -ls pand
  -lsa                  list details of packages matching [optional] expression: wppm -lsa pandas -l1
  -md                   markdown summary of the installation
  -p                    show Package (!= missing) dependencies of the given package[option], [.]=all: wppm -p pandas[.]
  -r                    show Reverse (!= constraining) dependancies of the given package[option]: wppm -r pytest![test]
  -l LEVELS             show 'LEVELS' levels of dependencies (with -p, -r): wppm -p pandas -l1
  -j, --json            machine-readable JSON output (with -p, -r, -ls, -md): wppm -p pandas[.] -j
  -t TARGET             path to target Python distribution (default: current environment)
  -i, --install         install a given package wheel or pylock file (use pip for more features)
  -u, --uninstall       uninstall package (use pip for more features)
```

## Links

- Source code: <https://github.com/winpython/winpython>
- Issues and feature requests: <https://github.com/winpython/winpython/issues>
- Discussions: <https://github.com/winpython/winpython/discussions>
- WinPython distribution: <https://winpython.github.io/>

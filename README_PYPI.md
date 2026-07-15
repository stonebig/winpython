# wppm — WinPython Package Manager

`wppm` is the package manager companion of [WinPython](https://winpython.github.io/), the portable
Python distribution for Windows. It works on any Python environment, WinPython or not.

It complements `pip` (which remains the recommended way to add or remove packages) with:

- **dependency tree navigation**: see what a package requires (`-p`), or which installed
  packages require it (`-r`), across any number of levels — including `[extra]` variants,
- **wheelhouse installs**: install a set of wheels from a local directory or a `pylock.toml` file,
- **WinPython housekeeping**: register/unregister a WinPython distribution in Windows,
  make it movable, list or summarize installed packages.

## Examples

Which installed packages depend on `pytest`, and which pin it hard (`!`):

```console
wppm -r pytest![test]
```

The full constraint web of your environment — every package, every extra, nine levels deep:

```console
wppm -p .[.] -l9
```

What `pandas` pulls in, one level:

```console
wppm -p pandas -l1
```

## Command line

```text
usage: wppm [-h] [-v] [--register] [--unregister] [--fix] [--movable]
            [-ws WHEELSOURCE] [-wd WHEELDRAIN] [-ls] [-lsa] [-md] [-p] [-r]
            [-l LEVELS] [-t TARGET] [-i] [-u]
            [package(s) or lockfile ...]

WinPython Package Manager: handle a WinPython Distribution and its packages

positional arguments:
  package(s) or lockfile
                        optional package names, wheels, or lockfile

options:
  -h, --help            show this help message and exit
  -v, --verbose         show more details on packages and actions
  --register            Register WinPython: associate file extensions, icons and context menu with this WinPython
  --unregister          Unregister WinPython: de-associate file extensions, icons and context menu from this WinPython
  --fix                 make WinPython fix
  --movable             make WinPython movable
  -ws WHEELSOURCE       wheels location, ('.' = WheelHouse): wppm pylock.toml -ws source_of_wheels, wppm -ls -ws .
  -wd WHEELDRAIN        wheels destination: wppm pylock.toml -wd destination_of_wheels
  -ls, --list           list installed packages matching [optional] expression: wppm -ls, wppm -ls pand
  -lsa                  list details of packages matching [optional] expression: wppm -lsa pandas -l1
  -md                   markdown summary of the installation
  -p                    show Package (!= missing) dependencies of the given package[option], [.]=all: wppm -p pandas[.]
  -r                    show Reverse (!= constraining) dependancies of the given package[option]: wppm -r pytest![test]
  -l LEVELS             show 'LEVELS' levels of dependencies (with -p, -r): wppm -p pandas -l1
  -t TARGET             path to target Python distribution (default: current environment)
  -i, --install         install a given package wheel or pylock file (use pip for more features)
  -u, --uninstall       uninstall package (use pip for more features)
```

## Links

- WinPython distribution: <https://winpython.github.io/>
- Source code: <https://github.com/winpython/winpython>
- Issues and feature requests: <https://github.com/winpython/winpython/issues>
- Discussions: <https://github.com/winpython/winpython/discussions>

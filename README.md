# Historyline 1914-1918 REMAKE 
A remake of a classical amiga game 

This fork is porting the game to Go with [Ebitengine](https://ebitengine.org). The plan is in
[PLAN.md](PLAN.md). Until the Go version catches up, the original Python/pygame code stays in the
repo as the reference implementation. Both versions use the same `gfx/` and `levels/`.

## Running the Go version

You need Go (see `go.mod` for the version) and [just](https://github.com/casey/just). On Linux,
Ebitengine also needs the OpenGL and X11 headers, e.g. on Debian/Ubuntu:
`sudo apt-get install libgl1-mesa-dev xorg-dev libasound2-dev`.

```sh
just run     # start the game (for now this is an empty window)
just test    # go test ./...
just lint    # go vet + golangci-lint
just build   # build ./historyline
just wasm    # build historyline.wasm and copy wasm_exec.js
just ci      # everything CI runs
```

## Running the Python reference

You need Python 3 with `pygame` and `numpy`. Pass a level name from `levels/` without the `.json`
extension:

```sh
python3 main.py level1_cp            # play a level
python3 main.py level1_cp --reveal   # show the whole map (dev)
python3 main.py level1_cp --mapedit  # map editor (dev)
python3 main.py --help               # all options
```

# Go version of Historyline 1914-1918. The Python reference runs via `python3 main.py`.

binary := "historyline"

# List the available recipes
default:
    @just --list

# Run the game
run *args:
    go run ./cmd/historyline {{args}}

# Run all Go tests
test:
    go test ./...

# Run go vet and golangci-lint
lint:
    go vet ./...
    golangci-lint run ./...

# Build the desktop binary
build:
    go build -o {{binary}} ./cmd/historyline

# Build the WASM binary plus the wasm_exec.js loader
wasm:
    GOOS=js GOARCH=wasm go build -o {{binary}}.wasm ./cmd/historyline
    cp "$(go env GOROOT)/lib/wasm/wasm_exec.js" .

# Everything CI checks
ci: lint test build wasm

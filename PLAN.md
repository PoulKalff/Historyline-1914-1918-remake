# PLAN — Historyline 1914-1918 remake in Go

This plan continues PoulKalff's Python/pygame remake (last upstream commit `b2915b9`, 2024-11-21,
version `0.80`) as a Go port. The Python code stays in the repo as the reference implementation
until the Go version reaches parity (Phase 2). `gfx/` and `levels/` are shared between the two
versions.

---

## 1. Where the Python version stands

About 3,400 lines: `main.py` (loop/input), `gui.py` (rendering, movement, combat, fog of war),
`hlrData.py` (data tables, classes and menus), `mapEditor.py`, `ArtificialIntelligence.py`,
and `FINdecoder/`.

### Working

- **Hex map.** Offset layout: each row is a "line" in the level JSON, odd lines are shifted half
  a hex, and odd lines hold one hex fewer. Hexes are 142 × 40 px. Maps are 8 or 12 hexes wide and
  47 lines tall. The view scrolls, and the minimap supports click-to-jump.
- **Terrain.** Summer and winter tile sets, about 65 hex types. Each type has movement, battle
  and sight modifiers. Infrastructure overlays: road, path, rail, bridge, stream, lake, trench,
  barbed wire, and more than one overlay per hex.
- **Fog of war.** Three states (never seen, seen before, visible), driven by each unit's sight
  radius. Owned depots and the HQ reveal their neighbouring hexes. `--reveal` is a dev flag.
- **Units and weapons.** 27 unit types (German/French variants of infantry, elite infantry,
  cavalry, light/medium/heavy artillery, supply car, bunker, armoured car, Charron, patrol boat,
  transport/armoured/artillery train, sappers) and 15 weapons. Icons are recoloured per faction,
  with six rotations. Moved units are drawn greyed out.
- **Movement.** Reachable hexes and a BFS path. The move is animated along the path. Movement
  types: normal, rail-only and water-only.
- **Combat.** A weapon menu and min/max range. The formula combines power − armour, distance,
  terrain, experience, unit size and a random term. The defender counter-attacks with its best
  weapon in range. Experience goes up to rank 10. Combat has an animated result bar, hit markers
  and a death explosion.
- **Containers.** HQ (capacity 50), depots (40) and factories (40) hold units in a 2 × 9 grid.
  Units with storage (e.g. supply car) can carry units. A content menu lets the player move a
  contained unit out.
- **Capture.** A unit with skill 1 that enters an enemy or neutral depot captures it. Capturing
  the HQ ends the game.
- **Turns.** F1 ends the turn and increments the round counter.
- **Levels.** `level1_cp` "Pulse" (8 × 47), `level2_cp` "Civil" (12 × 47), `level3_cp` "Mouse"
  (12 × 47), all played from the Central Powers side. `BACK-level1_cp.json` is a backup.
- **Map editor** (`-m`, dev only). It edits hex type, infrastructure and units, and `-g`
  generates an empty map.

### Stubbed or not started

- **AI.** `AI.moveUnit()` is empty, so the computer's turn does nothing and hands the turn back.
  `ArtificialIntelligence_the7thGame.py` is a move-scoring AI from an unrelated 7 × 7 board game.
  It is only an idea source.
- **FIN decoder.** Started on the original game's map format (`00.FIN`). It contains the TPWM
  ("Turbo Packer") unpack routine as C-like pseudocode inside a `.py` file, and a byte dumper. It
  does not decode yet.
- **Upstream TODOs** in `main.py`:
  - Movement cost should use terrain and roads.
  - Units should block adjacent hexes.
  - Supply truck contents should go into a depot when the truck enters it.
  - The AI is not written.

### Known bugs and gaps found while reading the code

| Area | Problem |
|---|---|
| Movement | Range is `speed` counted in hex *steps*. `movementModifier` (terrain cost, road = 0) is never applied. |
| Movement | `findPath` checks only units and fog, not terrain, so a path can cross impassable hexes (water, houses). |
| Movement | The obstruction check in `getMovableSquares` tests `movingUnit.faction != player` instead of the occupant's faction. |
| Combat | Ammo is shown but never decremented. Weapons with `ammo: 0` can still be chosen. |
| Combat | The `air`/`ground`/`water` target flags are never checked. |
| Combat | Attacking does not mark the unit as having acted, so a unit can attack again and again. |
| Combat | `markAttackableSquares` compares the target faction to `playerTurn`, not to the attacker's faction. |
| Fog of war | Terrain `sightModifier` is never used. Fog is computed only for `info.player`, which makes hot-seat or AI-side vision impossible. |
| Logistics | Fuel is shown but never consumed. There is no resupply, repair or reinforcement. |
| Factory | Factories are only containers. There is no production. Only `factoryE` is recognised as a factory; the N/S/W variants are not. |
| Turns | The HQ is the only win condition. There is no turn limit and no "all units destroyed" condition. |
| UI | Layout is hard-coded for an 1800 × 1000 window. `findHex` hard-codes an 8-wide, 23-line view. In `ContentMenu`, the "actual" and "max" labels are swapped. |

---

## 2. Target architecture (Go)

- **Engine:** [Ebitengine](https://ebitengine.org) v2. It is pure Go 2D with images, input and
  audio, and runs on desktop and WASM (browser) from one codebase.
- **Layout:** Go code at the repo root. The Python code is left untouched so upstream changes
  can still be merged.

```
go.mod                      module github.com/CWBudde/Historyline-1914-1918-remake
cmd/historyline/            game binary (flags: -level, -reveal, -hexnumbers, -edit)
cmd/hlmapedit/              standalone map editor (later)
cmd/finextract/             original-data importer (Phase 5)
internal/hexgrid/           offset<->cube coords, neighbours, distance, ring/range, pixel<->hex
internal/data/              terrain, infrastructure, unit and weapon definitions (embedded YAML/JSON)
internal/level/             load/save of the existing levels/*.json format (+ versioned successor)
internal/game/              pure rules engine — no rendering, no ebiten import
    state.go                Map, Hex, Unit, Container, Player, Turn
    commands.go             Move, Attack, Load, Unload, Produce, Resupply, EndTurn
    movement.go             Dijkstra with terrain cost, ZOC, movement types
    combat.go               battle resolution with injectable RNG
    vision.go               per-player fog of war
internal/ai/                computer player working through the command API
internal/ui/                ebiten Game: renderer, camera, input, menus, panels, animations
internal/assets/            go:embed of gfx/, faction recolouring and rotation cached at load time
```

**Principles:**

- **Rules and rendering are separate.** `internal/game` is deterministic and fully unit-tested.
  The UI only sends commands and plays back the events the engine returns (moved, attacked,
  died, captured, …). The AI, save games, replays and tests all build on this split.
- **Data-driven.** Unit, weapon and terrain stats move out of code into data files. Tests check
  that the ported values match `hlrData.py` exactly.
- **Two-phase porting.** First reach parity (the Python rules, bugs fixed), then extend.

---

## 3. Phases

### Phase 0 — Bootstrap

- [x] `go mod init`, add Ebitengine, add `.gitignore` entries for Go build output (2026-10-14) —
      module `github.com/CWBudde/Historyline-1914-1918-remake`, Ebitengine v2.10.5, a stub
      `cmd/historyline` that opens an empty 1800 × 1000 window, binaries/wasm ignored
- [x] Add a `Makefile`/`justfile` with `run`, `test`, `lint`, `build`, `wasm` targets (2026-10-14) —
      `justfile` with those recipes plus `ci`; lint = `go vet` + golangci-lint v2 (`.golangci.yml`)
- [ ] GitHub Actions: `go test ./...`, `golangci-lint`, a build matrix (linux/windows/macos) and a
      WASM build (2026-10-14) — partial: `.github/workflows/ci.yml` added and passes actionlint;
      tick once the first run on GitHub is green
- [ ] Clarify asset provenance. `gfx/` holds tiles and sprites modelled on (or taken from) the 1992
      Blue Byte original. Find out which, and record it in the README before any public release.
- [x] README section: how to run the Go version vs. the Python reference (2026-10-14) — README
      lists the `just` recipes and the `python3 main.py <level>` options

### Phase 1 — Core model (no graphics)

- [ ] `hexgrid`: port the offset layout exactly. Table-driven tests against Python
      `adjacentHexes` for every hex of every shipped level, including edge cases (odd lines are
      one hex shorter). Add cube-coordinate distance to replace the BFS `calculateDistance`.
- [ ] `data`: port `bgTilesModifiers`, the infrastructure rules (road/path/bridge/rail/stream/
      trench/barbed wire modifiers and `movementAllowed`), the 27 units and the 15 weapons.
      Add a parity test.
- [ ] `level`: load `levels/*.json` unchanged. This covers tile, infra (a string or a list), unit,
      and `[owner, [units…]]` for HQ/depot/factory. Round-trip test: load → save → identical JSON.
- [ ] `game` state: hexes, units (size, experience, ammo per weapon, fuel, moved/attacked flags),
      containers (2 × 9 slots, weight capacity), owners
- [ ] `game` commands at Python parity: move with a path, attack with counter-attack, enter
      container, leave container, capture, end turn, HQ-capture victory
- [ ] `game` vision: fog of war for each player (never seen / seen / visible)

### Phase 2 — Playable parity (Ebitengine UI)

- [ ] Asset loading via `go:embed`. Port the faction recolouring (palette swap of the five brown
      shades), the six rotations, the greyscale "moved" and "hidden" variants, and depot
      ownership stripes.
- [ ] Map renderer with camera and scrolling, plus pixel→hex picking. Replace the hard-coded
      `findHex` with general geometry.
- [ ] Minimap with view rectangle and click-to-jump
- [ ] Terrain panel (movement/battle/sight bars), and unit panel (flag, rank, picture, stats,
      skills, four weapon rows)
- [ ] Action menu (move / attack / contents / exit), weapon menu, content menu (2 × 9 grid)
- [ ] Overlays for reachable and attackable hexes. Movement animation along the path with
      rotation.
- [ ] Battle screen (result bars, sizes, ranks, weapons), hit markers, explosion animation,
      capture banner, round banner
- [ ] Keyboard and mouse controls matching the Python version. Replace the double-click
      detection.
- [ ] Dev flags: `-reveal`, `-hexnumbers`
- [ ] **Milestone:** all three levels play the same as in Python (apart from the fixed bugs)

### Phase 3 — Complete the rules

- [ ] Movement points: the terrain `movementModifier` is the cost and roads are cheap. Use
      Dijkstra and show the remaining points.
- [ ] Zone of control: hexes next to an enemy cost extra or stop movement (upstream TODO)
- [ ] Pathfinding respects impassable terrain and movement types (rail, water)
- [ ] One action per unit per turn (move then attack, or attack only). This needs to be checked
      against the original's rules before implementing.
- [ ] Ammo is used per shot and empty weapons are disabled. Target-type flags (`air`, `ground`,
      `water`) are enforced.
- [ ] Fuel use for motorised units. Units with no fuel cannot move.
- [ ] Resupply and repair: units in or next to an owned depot/HQ, or next to a supply car,
      regain ammo, fuel and size. A supply truck that enters a depot unloads its contents into it
      (upstream TODO).
- [ ] Factory production: owned factories build units each turn, depending on type and owner.
      Recognise all `factory*` orientations.
- [ ] `sightModifier` reduces vision through forest, hills and mountains
- [ ] Experience affects combat (it already does) and possibly sight and speed. Use the skills
      bitmap (`gfx/skills.png`) for real abilities beyond "capture".
- [ ] Win and lose conditions: capture the HQ, destroy all enemy units, optional turn limit set
      per level
- [ ] Two-player hot-seat, with a fog-of-war "hand over" screen between turns
- [ ] Save and load a game, including in the middle of a turn

### Phase 4 — Computer opponent

- [ ] The AI works only through `game` commands and its own side's vision (no cheating, with an
      optional difficulty setting that allows it)
- [ ] Base heuristic: for each unit, generate candidate move+attack pairs. Score each by
      expected damage dealt minus expected damage taken, using the combat formula's expected
      value. Add terms for capture value, distance to the enemy HQ, terrain defence, and keeping
      artillery behind the front line.
- [ ] Strategic layer: assign each unit a role (attack, defend HQ/depots, capture neutral
      depots, escort), and manage resupply and production
- [ ] Optional animated playback of AI moves, with a skip option (like Battle Isle 3)
- [ ] Headless AI-vs-AI runner for balance testing and regression tests

### Phase 5 — Original content

- [ ] TPWM unpacker in Go, from the pseudocode in `FINdecoder/twpm.py`, tested on
      `FINdecoder/00.FIN`
- [ ] Decode the `.FIN` map layout (tile byte + unit byte per hex, according to the notes in
      `decode.py`). Write a mapping table from original tile and unit IDs to the remake's names.
- [ ] `cmd/finextract`: convert original maps into `levels/*.json`
- [ ] Import or rebuild the remaining campaign maps for **both** sides (only `*_cp` levels exist
      so far)
- [ ] Unit types the original has but the remake lacks. Compare against the original; likely
      candidates are aircraft (the weapons already carry an `air` flag), more train and boat
      variants, and engineer abilities (bridges, trenches).
- [ ] Mission briefings, campaign progression, and level codes/passwords as in the original

### Phase 6 — Polish and distribution

- [ ] Title screen, side and level selection, options (window size, scroll speed, AI animation)
- [ ] Resolution independence: scale the 1800 × 1000 logical layout and support fullscreen
- [ ] Sound effects and music via `ebiten/audio`
- [ ] Map editor ported (in game with `-edit`, or `cmd/hlmapedit`): tile, infra, unit and
      container palettes, plus a new-map wizard (replaces `generateMap()`'s console prompts)
- [ ] WASM build published (e.g. GitHub Pages)
- [ ] Release binaries via GoReleaser
- [ ] Remove the Python sources (or move them to `legacy/`) once they are no longer needed as a
      reference

### Beyond the original (from upstream's wish list)

- [ ] Artillery can destroy infrastructure
- [ ] Dedicated ammo and fuel supply units
- [ ] Engineer units that build infrastructure

---

## 4. Open questions

1. **Rule fidelity.** Should the remake match the 1992 original's rules exactly (combat formula,
   one action per turn, production) or keep PoulKalff's simplified formula? Getting the original
   rules needs a manual, a disassembly or careful play-testing.
2. **Upstream relationship.** Keep merging upstream Python changes, or treat the fork as
   independent once Phase 2 is reached?
3. **Level format.** Keep the current JSON format permanently, or move to a versioned format
   (with per-level metadata: turn limit, briefing, side, season) and keep a reader for the old
   one?

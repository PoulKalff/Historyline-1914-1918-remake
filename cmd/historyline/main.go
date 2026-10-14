// Command historyline is the Go port of the Historyline 1914-1918 remake.
//
// For now it only opens an empty window. The game itself follows in later
// phases of PLAN.md.
package main

import (
	"log"

	"github.com/hajimehoshi/ebiten/v2"
)

const (
	screenWidth  = 1800
	screenHeight = 1000
)

type game struct{}

func (g *game) Update() error { return nil }

func (g *game) Draw(*ebiten.Image) {}

func (g *game) Layout(int, int) (int, int) { return screenWidth, screenHeight }

func main() {
	ebiten.SetWindowSize(screenWidth, screenHeight)
	ebiten.SetWindowTitle("Historyline 1914-1918")
	if err := ebiten.RunGame(&game{}); err != nil {
		log.Fatal(err)
	}
}

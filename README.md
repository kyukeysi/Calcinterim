# Calcinterim

An air-drawn mathematical spellcasting game made with Python, OpenCV, MediaPipe, and SymPy.

Calcinterim lets the player draw mathematical numbers and operators in the air using their index finger. The drawing appears as a magical orange/gold energy trail, inspired by eldritch spellcasting.

The goal is to build mathematical expressions through hand gestures and solve target expressions using SymPy.

## Concept

```text
Webcam
   ↓
MediaPipe hand tracking
   ↓
Index finger drawing
   ↓
Magical spell trail
   ↓
Stroke recognition
   ↓
Mathematical expression
   ↓
SymPy
   ↓
Target comparison
   ↓
Victory
```

## Gameplay

At the beginning of a round, the player receives a mathematical target.

Example:

```text
TARGET: 12x²
```

The player can draw individual mathematical tokens:

```text
3 → x² → × → 4
```

The game builds the expression:

```text
3x² × 4
```

SymPy then evaluates the expression and checks whether it is mathematically equivalent to the target:

```text
3x² × 4
      ↓
12x²
      ↓
TARGET REACHED
```

The game does not rely on comparing expression strings. Mathematically equivalent expressions should be treated as equivalent.

## Controls

### Drawing

The drawing gesture uses:

* Index finger pointing upward
* Thumb extended outward

The index fingertip acts as the drawing cursor.

```text
Index up
   +
Thumb out
   ↓
DRAW
```

### Commit

While drawing, the fingertip creates a spell trail.

Lowering the thumb releases the drawing gesture and commits the current stroke.

```text
Drawing
   ↓
Thumb lowered
   ↓
Stroke committed
   ↓
Recognition
```

### Open Palm

An open palm can be used to clear the current stroke.

## Visual Style

Calcinterim uses a magical eldritch spellcasting aesthetic.

Visual effects include:

* Orange and gold energy
* Glowing spell trails
* Sparks
* Magical particles
* Spell circles
* Glowing HUD elements
* Hand-following spell effects
* Golden victory explosions

The goal is to make the drawing feel like magical energy rather than a normal neon drawing application.

## Current Status

### Milestone 1 - Air Drawing Prototype

* [ ] Webcam capture
* [ ] MediaPipe hand tracking
* [ ] L/gun drawing gesture
* [ ] Index fingertip cursor
* [ ] Magical glowing trail
* [ ] Particle effects
* [ ] Stroke collection
* [ ] Thumb-release commit
* [ ] Temporary stroke recognition

### Planned

### Milestone 2 - Math Engine

* [ ] Token system
* [ ] Mathematical expression construction
* [ ] SymPy parsing
* [ ] Expression simplification
* [ ] Target comparison

### Milestone 3 - Game HUD

* [ ] Target display
* [ ] Live expression display
* [ ] Timer
* [ ] Hand-following spell ring
* [ ] Game state system

### Milestone 4 - Spell Effects

* [ ] Advanced magical particles
* [ ] Sparks
* [ ] Rotating spell rings
* [ ] Stroke commit effects
* [ ] Victory explosion
* [ ] Screen flash
* [ ] Victory animation

### Milestone 5 - Stroke Recognition

* [ ] Stroke preprocessing
* [ ] Template recognition
* [ ] Mathematical symbol recognition
* [ ] Recognition confidence
* [ ] Recognition improvements

## Technology

* Python 3.12
* OpenCV
* MediaPipe Tasks API
* Pygame
* Pillow
* NumPy
* SymPy

## MediaPipe

Calcinterim uses the MediaPipe Tasks API for hand tracking.

The project does **not** use the deprecated:

```python
mp.solutions.hands
```

API.

The project uses the newer Tasks API, including:

```python
mp.tasks.BaseOptions
mp.tasks.vision.HandLandmarkerOptions
mp.tasks.vision.VisionRunningMode
```

## Project Structure

```text
Calcinterim/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│
├── docs/
│   ├── DESIGN.md
│   ├── DEVELOPMENT.md
│   └── MILESTONES.md
│
└── milestones/
    └── milestone-01.md
```

The project may initially keep multiple systems inside `main.py` while prototyping. As the project becomes more stable, systems will be separated into modules.

## Development Philosophy

Calcinterim is being developed incrementally.

The core gameplay loop will be tested before implementing complex handwriting recognition.

The major systems are kept separate so that the recognition system can be improved or replaced without rewriting the hand tracking, drawing, rendering, or math systems.

The planned development order is:

```text
1. Webcam
        ↓
2. MediaPipe hand tracking
        ↓
3. Index fingertip cursor
        ↓
4. Drawing gesture
        ↓
5. Glowing trail
        ↓
6. Stroke collection
        ↓
7. Thumb-release commit
        ↓
8. Temporary recognition
        ↓
9. SymPy math engine
        ↓
10. Target comparison
        ↓
11. Timer
        ↓
12. HUD
        ↓
13. Spell ring
        ↓
14. Particle effects
        ↓
15. Golden victory effects
        ↓
16. Actual handwriting recognition
```

## Development Environment

The project is currently developed on Windows.

Python is run using:

```bash
py -3.12 main.py
```

Python version:

```text
Python 3.12.10
```

## Project Goal

The long-term goal is to create a playable mathematical spellcasting game where the player physically draws mathematical expressions in the air and uses them to solve targets.

Calcinterim is currently a prototype and is being developed milestone by milestone.

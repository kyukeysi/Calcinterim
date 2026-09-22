# Calcinterim - Development Milestones

## Milestone 1 - Air Drawing Prototype

**Status:** In Progress

### Goal

Create the first working webcam-based air drawing system.

### Features

- [ ] Webcam capture
- [ ] MediaPipe hand tracking
- [ ] L/gun drawing gesture
- [ ] Index fingertip cursor
- [ ] Magical glowing trail
- [ ] Particle effects
- [ ] Stroke collection
- [ ] Thumb-release commit
- [ ] Temporary stroke recognition

### Pipeline

```text
Webcam
   ↓
MediaPipe
   ↓
Hand landmarks
   ↓
Gesture controller
   ↓
Index fingertip
   ↓
Glow renderer
   ↓
Stroke manager
   ↓
Thumb release
   ↓
Temporary recognizer
```

### Not Included

The following are intentionally not part of Milestone 1:

- SymPy
- Mathematical target comparison
- OCR
- Handwriting recognition
- Final HUD
- Timer
- Victory system
- Advanced spell effects

---

## Milestone 2 - Math Engine

**Status:** Planned

### Goal

Connect recognized tokens to a mathematical expression system.

### Features

- Token storage
- Expression construction
- Controlled SymPy parsing
- Expression simplification
- Mathematical equivalence checking
- Target expressions

### Pipeline

```text
Recognized token
      ↓
Token list
      ↓
Expression string
      ↓
SymPy
      ↓
Simplified expression
      ↓
Target comparison
```

---

## Milestone 3 - Game System and HUD

**Status:** Planned

### Goal

Turn the prototype into an actual timed game.

### Features

- Target generation
- Live expression
- Timer
- Playing state
- Won state
- Lost state
- Hand-following spell ring
- Clear/reset behavior

---

## Milestone 4 - Magical Effects

**Status:** Planned

### Goal

Improve the visual presentation.

### Features

- Advanced spell trail
- Sparks
- Particles
- Spell circles
- Rotating arcs
- Commit effects
- Victory explosion
- Screen flash
- Magical victory animation

---

## Milestone 5 - Stroke Recognition

**Status:** Planned

### Goal

Recognize mathematical symbols drawn by the player.

### Features

- Stroke preprocessing
- Stroke normalization
- Template matching
- Mathematical symbol recognition
- Recognition confidence
- Recognition feedback
- Improved air-drawing recognition

### Initial Symbols

The recognition system may initially support:

```text
0 1 2 3 4 5 6 7 8 9
+
-
×
÷
x
²
(
)
```

The exact supported symbol set may change during development.

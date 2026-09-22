# Calcinterim - Game Design

## Overview

Calcinterim is an air-drawn mathematical spellcasting game.

The player uses a webcam and hand gestures to draw mathematical numbers and operators in the air.

The drawings appear as glowing orange and gold magical energy.

The long-term goal is to let the player solve mathematical targets by physically drawing the required expressions.

---

## Core Gameplay

At the beginning of a round, the game generates or provides a mathematical target.

Example:

```text
TARGET: 12x²
```

The player draws individual mathematical tokens:

```text
3 → x² → × → 4
```

The game builds the live expression:

```text
3x² × 4
```

The expression is converted into a SymPy expression:

```text
3*x**2*4
```

SymPy simplifies the expression:

```text
12*x**2
```

The game then checks whether the live expression is mathematically equivalent to the target.

---

## Mathematical Equivalence

The game should not compare expressions using strings.

For example:

```text
3x² × 4
```

and:

```text
12x²
```

are different strings but represent the same mathematical result.

SymPy should be used to determine equivalence.

Conceptually:

```python
sp.simplify(expr1 - expr2) == 0
```

---

## Drawing System

The player's index fingertip acts as the drawing cursor.

The drawing gesture is:

```text
Index finger pointing upward
+
Thumb pointing outward
```

Conceptually:

```text
        INDEX
          ↑
          |
          |
          |
          ●──────→ THUMB
         /
        /
      PALM
```

When the drawing gesture is active, the fingertip position is continuously added to the current stroke.

---

## Stroke System

A stroke is a collection of fingertip coordinates.

Example:

```python
[
    (320, 240),
    (323, 237),
    (327, 234),
    (331, 231)
]
```

The stroke manager is responsible only for collecting and storing these points.

It should not know about:

- SymPy
- OCR
- mathematical expressions
- game state
- recognition algorithms

This keeps the systems separate.

---

## Stroke Commitment

A stroke is committed when the player releases the drawing gesture by lowering their thumb.

The process is:

```text
DRAWING
   ↓
Thumb lowered
   ↓
Commit detected
   ↓
Stroke saved
   ↓
Recognition system
   ↓
Mathematical token
   ↓
Math engine
```

The commit gesture should use debounce logic so that a single noisy frame does not accidentally commit a stroke.

---

## Open Palm

An open palm is used as a clearing gesture.

The initial implementation should clear the current unfinished stroke.

Future versions may allow the gesture to clear the entire mathematical expression.

---

## Recognition System

MediaPipe provides hand landmarks, but it does not recognize the mathematical symbol being drawn.

For example, MediaPipe does not automatically know whether a stroke represents:

```text
3
8
+
-
×
x
²
4
```

Therefore recognition is a separate system.

The recognition interface should eventually look like:

```python
class StrokeRecognizer:

    def recognize(self, stroke):
        ...
```

The rest of the game should only care about the returned token.

---

## Recognition Development

Recognition will be implemented gradually.

### Version 1

Temporary/manual recognition for testing the gameplay loop.

### Version 2

Basic OpenCV/template-based recognition.

### Version 3

Handwriting recognition model.

### Version 4

Specialized recognition for air-drawn mathematical symbols.

Complex handwriting recognition should not be implemented before the core gameplay loop is working.

---

## Visual Style

The visual style is inspired by magical eldritch spellcasting.

The drawing should look like magical energy rather than a normal neon drawing application.

### Main Visual Elements

- Orange energy
- Gold highlights
- Bright spell cores
- Glowing trails
- Sparks
- Magical particles
- Spell circles
- Rotating arcs
- Glowing HUD
- Hand-following effects
- Victory explosions

---

## Spell Trail

The drawing trail should consist of multiple visual layers.

Conceptually:

```text
Camera frame
     +
Large blurred aura
     +
Orange energy
     +
Bright core
     +
Particles
     ↓
Final magical trail
```

The trail should have:

- a wide blurred glow
- a brighter orange middle layer
- a thin bright core
- occasional sparks

---

## Spell Ring

A magical ring will eventually follow the player's hand.

The ring can display the current live mathematical expression.

Conceptually:

```text
        ✦
    ╭────────╮
   ╱          ╲
  │  LIVE: 3x² │
   ╲          ╱
    ╰────────╯
        ✦
```

Future effects may include:

- rotating arcs
- magical runes
- particles
- pulsing brightness
- token commit pulses

---

## HUD

The HUD should eventually display:

```text
             TARGET: 12x²

                         TIME: 18


              LIVE: 3x²
```

The target should remain visible near the top of the screen.

The timer should remain visible in a corner.

The live expression should follow or appear near the player's hand.

---

## Victory

When the live expression becomes mathematically equivalent to the target:

```text
PLAYING
   ↓
WON
```

The game should:

1. Freeze the timer.
2. Trigger a magical spell effect.
3. Expand the spell ring.
4. Spawn a golden/orange particle burst.
5. Flash the screen.
6. Display a victory message.

Example:

```text
TARGET REACHED
```

The effect should feel like a magical spell completing rather than generic game confetti.

---

## Architecture

The planned architecture is:

```text
Camera
   ↓
Hand Tracker
   ↓
Gesture Controller
   ↓
Stroke Manager
   ↓
Recognizer
   ↓
Math Engine
   ↓
Game State
   ↓
HUD / Effects
```

The systems should remain modular so individual components can be tested and replaced independently.

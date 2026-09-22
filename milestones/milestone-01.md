# Calcinterim - Milestone 1

## Air Drawing Prototype

**Status:** In Progress

## Goal

Build the first working version of Calcinterim.

The player should be able to:

1. Open the webcam.
2. Detect their hand using MediaPipe.
3. Use the L/gun gesture to activate drawing.
4. Move their index fingertip to draw.
5. See the drawing as a magical glowing trail.
6. Generate particles around the drawing.
7. Lower their thumb to commit the stroke.
8. Pass the completed stroke to a temporary recognizer.

---

## Milestone Pipeline

```text
Webcam
   ↓
MediaPipe Hand Tracking
   ↓
Hand Landmarks
   ↓
Gesture Controller
   ↓
Index Fingertip
   ↓
Magical Trail
   ↓
Stroke Manager
   ↓
Thumb Release
   ↓
Temporary Recognizer
```

---

## Requirements

### 1. Webcam

- [ ] Open the default webcam.
- [ ] Read camera frames continuously.
- [ ] Display the camera feed.
- [ ] Handle webcam failure.
- [ ] Release the camera when the program exits.

### 2. MediaPipe Hand Tracking

- [ ] Load the `hand_landmarker.task` model.
- [ ] Initialize the MediaPipe Tasks API.
- [ ] Detect the player's hand.
- [ ] Retrieve hand landmarks.
- [ ] Track the hand while it is visible.

### 3. Drawing Gesture

The drawing gesture should use:

```text
Index finger pointing upward
+
Thumb pointing outward
```

- [ ] Detect the index finger position.
- [ ] Detect whether the index finger is raised.
- [ ] Detect whether the thumb is extended.
- [ ] Activate drawing when both conditions are satisfied.
- [ ] Stop drawing when the gesture is released.

### 4. Fingertip Cursor

The index fingertip is landmark `8`.

- [ ] Read landmark `8`.
- [ ] Convert normalized coordinates to screen coordinates.
- [ ] Use the fingertip as the drawing cursor.
- [ ] Display a visual indicator around the fingertip.

### 5. Magical Trail

The drawing should look like magical energy rather than a normal line.

- [ ] Create a drawing layer.
- [ ] Draw a wide glowing layer.
- [ ] Draw an orange middle layer.
- [ ] Draw a bright core.
- [ ] Apply blur to create the glow.
- [ ] Composite the glow with the camera frame.

Target appearance:

```text
Wide Glow
    ↓
Orange Energy
    ↓
Bright Core
```

### 6. Particles

Particles should appear around the active drawing area.

- [ ] Create a particle system.
- [ ] Spawn particles near the fingertip.
- [ ] Give particles movement.
- [ ] Give particles a limited lifetime.
- [ ] Remove particles after their lifetime expires.
- [ ] Render particles above the camera frame.

### 7. Stroke Manager

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

- [ ] Start a new stroke.
- [ ] Add fingertip coordinates.
- [ ] Check whether the stroke is empty.
- [ ] Finish a stroke.
- [ ] Clear a stroke.

The stroke manager should only manage stroke data.

It should not contain:

- SymPy logic
- Recognition algorithms
- Game state
- Rendering logic

### 8. Thumb Release

Lowering the thumb commits the current stroke.

Pipeline:

```text
Drawing
   ↓
Thumb lowered
   ↓
Debounce
   ↓
Commit
   ↓
Stroke saved
```

- [ ] Detect thumb release.
- [ ] Require multiple consecutive frames before committing.
- [ ] Prevent accidental commits from noisy frames.
- [ ] Finish the current stroke.
- [ ] Send the completed stroke to the recognizer.

### 9. Temporary Recognizer

Milestone 1 does not require real handwriting recognition.

The recognizer can temporarily return a manually selected or placeholder token.

Example interface:

```python
class StrokeRecognizer:

    def recognize(self, stroke):
        return "3"
```

- [ ] Create the recognizer interface.
- [ ] Accept a completed stroke.
- [ ] Return a temporary token.
- [ ] Print or display the recognized token for testing.

---

## Open Palm

An open palm may be implemented as a basic clearing gesture.

- [ ] Detect an open palm.
- [ ] Clear the current unfinished stroke.
- [ ] Clear the active visual trail when appropriate.

Clearing the entire mathematical expression is not required for Milestone 1.

---

## Testing Checklist

Before marking Milestone 1 complete, verify:

### Webcam

- [ ] Camera opens successfully.
- [ ] Camera feed displays correctly.
- [ ] Camera closes correctly.

### Hand Tracking

- [ ] Hand is detected.
- [ ] Hand landmarks follow movement.
- [ ] Index fingertip position is accurate enough for drawing.

### Gesture

- [ ] L/gun gesture activates drawing.
- [ ] Moving the fingertip creates a stroke.
- [ ] Lowering the thumb commits the stroke.
- [ ] Noisy frames do not cause repeated commits.

### Rendering

- [ ] Trail follows the fingertip.
- [ ] Trail has a visible glow.
- [ ] Particles appear while drawing.
- [ ] Trail remains visible after drawing when appropriate.

### Stroke

- [ ] Points are collected correctly.
- [ ] Stroke can be completed.
- [ ] Completed stroke is passed to the recognizer.
- [ ] Stroke can be cleared.

### Recognition

- [ ] Temporary recognizer receives the stroke.
- [ ] A temporary token is returned.
- [ ] The returned token can be displayed or printed.

---

## Milestone 1 Definition of Done

Milestone 1 is complete when the following workflow works reliably:

```text
Start program
     ↓
Webcam opens
     ↓
Hand detected
     ↓
L/gun gesture
     ↓
Index fingertip moves
     ↓
Magical trail appears
     ↓
Particles appear
     ↓
Thumb lowered
     ↓
Stroke committed
     ↓
Temporary recognizer
     ↓
Token returned
```

---

## Not Included in Milestone 1

The following systems will be implemented in later milestones:

- SymPy math engine
- Mathematical target comparison
- Real handwriting recognition
- Advanced template recognition
- Final HUD
- Timer
- Target generation
- Win/lose states
- Spell ring
- Advanced magical effects
- Victory explosion

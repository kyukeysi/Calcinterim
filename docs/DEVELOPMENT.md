# Calcinterim - Development Guide

## Development Environment

Calcinterim is currently developed on Windows.

### Python

The project uses:

```text
Python 3.12.10
```

Python is run using:

```text
py -3.12 main.py
```

### Dependencies

The project uses:

- OpenCV
- MediaPipe
- Pygame
- Pillow
- NumPy
- SymPy

The dependency list is stored in:

```text
requirements.txt
```

---

## MediaPipe

The project uses the MediaPipe Tasks API.

The deprecated:

```python
mp.solutions.hands
```

API is not used.

The hand tracker uses the newer Tasks API:

```python
mp.tasks.BaseOptions
mp.tasks.vision.HandLandmarkerOptions
mp.tasks.vision.VisionRunningMode
```

The project requires a compatible MediaPipe hand landmark model:

```text
hand_landmarker.task
```

---

## Development Philosophy

The project is built incrementally.

Each major system should be tested before the next system is added.

The development order is:

```text
Webcam
   ↓
Hand tracking
   ↓
Gesture detection
   ↓
Fingertip cursor
   ↓
Spell trail
   ↓
Stroke collection
   ↓
Stroke commitment
   ↓
Temporary recognition
   ↓
Math engine
   ↓
Target comparison
   ↓
HUD
   ↓
Spell effects
   ↓
Actual recognition
```

---

## Prototype First

Early versions should prioritize functionality over complexity.

For example, the first prototype may use a temporary recognizer instead of actual handwriting recognition.

This allows the following systems to be tested independently:

```text
Hand tracking
      +
Gesture system
      +
Drawing
      +
Stroke management
      +
Math engine
```

Actual handwriting recognition can be added after these systems are stable.

---

## Separation of Systems

The following systems should remain independent.

### Camera

Responsible for:

- Opening the webcam
- Reading frames
- Releasing the camera

### Hand Tracker

Responsible for:

- MediaPipe initialization
- Detecting hands
- Returning hand landmarks

### Gesture Controller

Responsible for:

- Detecting drawing gestures
- Detecting thumb release
- Detecting open palm
- Debouncing gestures

### Stroke Manager

Responsible for:

- Starting strokes
- Adding points
- Finishing strokes
- Clearing strokes

### Renderer

Responsible for:

- Magical trails
- Glow
- Sparks
- Particles
- Spell effects

### Recognizer

Responsible for:

- Converting strokes into mathematical tokens

### Math Engine

Responsible for:

- Token storage
- Expression construction
- SymPy parsing
- Mathematical comparison

### Game State

Responsible for:

- Playing state
- Win state
- Lose state
- Timer

### HUD

Responsible for:

- Target display
- Live expression
- Timer
- Status messages

---

## Testing

When adding a new feature, test that feature independently when possible.

For example:

```text
Test webcam
    ↓
Test hand tracking
    ↓
Test gesture
    ↓
Test drawing
    ↓
Test stroke commit
```

This makes errors easier to identify.

---

## Code Style

The project should prioritize readable and beginner-friendly Python.

Prefer:

```python
def is_drawing_gesture(hand):
    ...
```

over overly compressed logic.

Use descriptive names for classes, functions, and variables.

Keep comments focused on explaining why something is necessary.

---

## Git Workflow

Major features should be committed separately.

Example commit messages:

```text
docs: add project documentation
feat: implement hand tracking
feat: implement drawing gesture
feat: add magical trail renderer
feat: add stroke manager
feat: add temporary recognizer
feat: add math engine
```

Avoid committing unrelated changes together whenever possible.

---

## Milestones

Development is organized into milestones.

Each milestone should have:

- A clear goal
- A limited feature set
- Testable requirements
- Its own documentation

A milestone should be considered complete only after its required functionality has been tested.

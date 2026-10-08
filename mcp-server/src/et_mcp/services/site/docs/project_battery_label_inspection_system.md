# Battery Label Inspection System

## Project Overview

The Battery Label Inspection System is an industrial vision inspection solution designed for inspection of finished batteries before the packaging process.

The system verifies labels, codes, text, and tear-cap presence on battery terminals. It supports inspection of both larger and smaller battery variants using the same setup with minimal hardware and fixture changes.

A primary objective of the system is to reduce changeover time when switching between battery variants while maintaining inspection consistency.

---

## Application Domain

### Industry

Battery Manufacturing

### Inspection Stage

Finished Battery Inspection

### Production Stage

Pre-Packing Inspection

### Inspection Target

Finished Batteries

---

## Inspection Objectives

The system performs inspection of the following parameters:

### Label Inspection

- Label presence verification
- Label absence detection
- Label reverse detection

### Code Verification

- 1D code reading
- 1D code verification
- 2D code reading
- 2D code verification

### OCR Inspection

- Optical Character Recognition (OCR)

### Terminal Inspection

- Presence verification of tear caps on positive (+ve) terminals
- Presence verification of tear caps on negative (-ve) terminals
- Absence detection of tear caps on battery terminals

---

## Key System Advantage

The same inspection setup can be used for:

- Large battery variants
- Small battery variants

This reduces:

- Mechanical fixture changes
- Hardware modifications
- Production line changeover time

---

## System Architecture

### Controller

- Advantech MIC Series Controller

### Imaging System

- 3 Basler 21 Megapixel Cameras (Rolling Shutter)
- High-resolution lenses

### Lighting System

- High-intensity bar lights

### Control System

- AB Micrologix 1400 PLC
- Delta VFD

### Mechanical Components

- Bonfiglioli motor
- SMC pneumatic actuators
- SMC solenoid valves

### Software

- ET-Xpro Vision Software

---

## Inspection Process

The inspection process consists of three phases:

1. Positioning Phase
2. Inspecting Phase
3. Rejection Phase

---

## Phase 1: Positioning Phase

### Objective

Maintain consistent battery positioning before inspection.

### Challenge

Battery orientation on the conveyor may vary during production.

Variable orientation can affect inspection accuracy.

### Solution

A pneumatic positioning mechanism is used to align batteries before inspection.

### Components Used

#### Positioning Actuator

Used to position batteries correctly before entering the inspection station.

#### Buffer Actuator

Used to maintain adequate spacing between batteries moving on the conveyor.

### Outcome

Provides consistent positioning for image acquisition and inspection.

---

## Phase 2: Inspecting Phase

### Camera Configuration

Three 21-megapixel cameras inspect the battery from:

- Top side
- Left side
- Right side

### Lighting Configuration

Four high-intensity bar lights with dedicated drivers provide illumination for image acquisition.

### Optical System

High-resolution lenses are used because the inspection field of view is approximately 520 mm.

### Data Transfer

Cameras communicate with the controller through:

- USB 3.0 interface

This supports high-speed image transfer.

### Inspection Software

The inspection process is executed using ET-Xpro software installed on the controller.

---

## ET-Xpro Vision Software

### Overview

ET-Xpro is an in-house vision system software platform designed for industrial inspection applications.

The software is intended to be operable by both technical and non-technical users.

### Inspection Functions

ET-Xpro supports:

#### Label Verification

- Label presence inspection
- Label absence inspection
- Label reverse inspection

#### Code Inspection

- 1D code reading
- 1D code verification
- 2D code reading
- 2D code verification

#### OCR

- Optical Character Recognition (OCR)

#### Terminal Component Verification

- Tear-cap presence inspection
- Tear-cap absence inspection

### Recipe Management

The software supports:

- Multiple inspection recipes
- Recipe storage in internal memory

### Image Storage

Images of non-conforming products are stored for future reference.

---

## Phase 3: Rejection Phase

### Good Product Handling

When a battery passes inspection:

1. The controller sends an OK signal to the PLC.
2. The battery proceeds to the next production stage.
3. The battery moves to the packing process.

### Defective Product Handling

When a battery fails inspection:

1. The controller sends a rejection signal to the PLC.
2. A rejection cylinder removes the battery.
3. The battery is transferred to a rejection bin.

---

## Automated Decision Logic

### Acceptance Criteria

A battery is accepted when all configured inspection parameters pass verification.

### Rejection Criteria

A battery is rejected when one or more configured inspection parameters fail verification.

---

## Data Management

### Stored Data

The system stores:

- Inspection recipes
- Non-good images

### Applications

Stored information can support:

- Quality review
- Defect analysis
- Process improvement
- Production traceability

---

## Functional Benefits

### Automated Inspection

Reduces reliance on manual inspection processes.

### Variant Flexibility

Supports multiple battery variants using the same inspection platform.

### Reduced Changeover Time

Minimizes production interruptions when switching between battery models.

### Improved Quality Control

Provides consistent verification of labels, codes, text, and terminal components.

### Automated Rejection

Prevents defective batteries from reaching the packing process.

---

## Key Technologies

- Machine Vision
- Industrial Inspection
- OCR (Optical Character Recognition)
- 1D Barcode Verification
- 2D Code Verification
- Multi-Camera Inspection
- Automated Product Rejection
- Recipe-Based Inspection
- PLC Integration
- Conveyor-Based Inspection

---

## Inspection Category

Industrial Vision Inspection

## Product Type

Finished Batteries

## Primary Inspection Functions

- Label Presence Verification
- Label Absence Detection
- Label Reverse Detection
- OCR Inspection
- 1D Code Verification
- 2D Code Verification
- Tear Cap Presence Verification
- Automated Product Rejection
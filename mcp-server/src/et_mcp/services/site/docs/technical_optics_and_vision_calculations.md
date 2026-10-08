# Optics and Vision Calculations

## Technical Overview

This document covers the optical concepts used in machine vision systems, including Working Distance, Focal Length, Field of View, and Depth of Field. These concepts are fundamental to camera and lens selection, system setup, and vision-based measurement applications.

---

# Working Distance (WD)

## Definition

Working Distance (WD) is the distance from the end of the lens to the target when the focal point is aligned with the target.

Working Distance is also referred to as the operating distance.

---

## Relationship with Field of View and Sensor Size

With a CMOS sensor, the following proportional relationship applies:

Working Distance : Field of View = Focal Length : CMOS Size

This relationship can be used when determining the optical configuration required for an application.

---

# Focal Length

## Definition

Focal length is one of the primary specifications of a lens.

Example focal lengths referenced in the source material include:

- 8 mm (0.32")
    
- 16 mm (0.63")
    
- 25 mm (0.98")
    
- 50 mm (1.97")
    

---

## Role in Machine Vision

The working distance can be determined based on the focal length and the field of view required for the target being captured.

The size of the working distance and field of view is determined by:

- Lens focal length
    
- CMOS sensor size
    

For ranges where a close-up ring is not required, these values can be related using proportional calculations.

---

# Field of View (FOV)

## Definition

Field of View (FOV) is the image area visible within the selected working distance.

It represents the portion of the target scene captured by the imaging system.

---

## Relationship with Working Distance

In general:

- A longer working distance results in a wider field of view.
    
- A shorter working distance results in a narrower field of view.
    

---

## Relationship with Focal Length

The width of the field of view is determined according to the focal length of the lens.

### Shorter Focal Length

A shorter focal length produces:

- A larger angle of view
    
- A wider field of view
    

### Longer Focal Length

A longer focal length produces:

- A smaller angle of view
    
- Greater apparent magnification of distant targets
    

---

# Angle of View

## Definition

The angle covered by the lens when capturing images is referred to as:

- Angle of View
    
- View Angle
    

---

## Relationship with Focal Length

As focal length becomes shorter:

- Angle of view increases
    
- Field of view widens
    

As focal length becomes longer:

- Angle of view decreases
    
- Distant targets can appear larger
    

---

# Depth of Field (DOF)

## Definition

Depth of Field (DOF) is the range that appears to be in focus through the lens.

Although only one plane is perfectly focused, the human eye perceives a range around that plane as appearing clear.

This visible focus range is called the depth of field.

---

## Deep Depth of Field

When the focus range is wide, it is referred to as a deep depth of field.

Characteristics:

- Larger focus range
    
- More of the scene appears clear
    

---

## Shallow Depth of Field

When the focus range is narrow, it is referred to as a shallow depth of field.

Characteristics:

- Smaller focus range
    
- Less of the scene appears clear
    

---

# Optical Relationships Summary

## Working Distance, Field of View, Focal Length, and Sensor Size

The source material defines the following proportional relationship:

Working Distance : Field of View = Focal Length : CMOS Size

These parameters are commonly considered together when:

- Selecting lenses
    
- Selecting cameras
    
- Determining imaging geometry
    
- Designing machine vision inspection systems
    

---

# Optical Calculations

The technical guidance material includes the following optical calculation topics:

## Field of View using Pixel Size

Calculation of field of view based on pixel dimensions.

## Field of View using Sensor Size

Calculation of field of view based on sensor dimensions.

## Working Distance

Working distance calculation methods.

## Working Distance using Focal Length, Object and Sensor Size

Working distance calculation using focal length, object size, and sensor size.

## Depth of Field (DOF)

Depth of field calculation considerations.

## O Rings

O-ring related calculation topic referenced in the source material.

## Focal Length

Focal length calculation and selection considerations.

---

# Camera Calculations

The technical guidance material includes the following camera-related calculation topics:

## Camera Measurement Accuracy

Accuracy considerations for machine vision measurements.

## Camera Exposure Time

Exposure time selection and calculation considerations.

## Sensor Selection

Sensor selection considerations for machine vision applications.

## Line Scan Frequency

Line scan frequency calculation considerations.
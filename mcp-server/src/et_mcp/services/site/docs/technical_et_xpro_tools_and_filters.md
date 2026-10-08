# ET XPro Tools and Filters

## Technical Overview

ET XPro provides a collection of image processing tools used for verification, recognition, inspection, and measurement applications.

The source material provides detailed documentation for the Pixel Count tool and lists additional tools and filters available within the software.

---

# Pixel Count Tool

## Purpose

The Pixel Count tool is used to calculate the total number of selected pixels within an image.

The tool is typically used to verify whether a target region matches a reference image based on pixel quantity.

---

## Operation

To use the Pixel Count tool, the user selects the colour that should be evaluated.

This colour selection is used to isolate the region of interest and eliminate unwanted image areas.

After colour selection:

- The selected colour is treated as white pixels.
    
- All remaining pixels are treated as black pixels.
    

The software then calculates the total number of white pixels.

---

## Inspection Process

The number of white pixels in the reference image is compared with the number of white pixels in the current image.

A judgment is made based on predefined tolerance limits.

The user configures:

- Upper threshold
    
- Lower threshold
    

Inspection results are evaluated as follows:

### NG Condition

The result is considered NG (Not Good) when:

- Pixel count is greater than the upper threshold, or
    
- Pixel count is less than the lower threshold
    

### Acceptable Condition

The result is considered acceptable when the pixel count remains within the configured threshold limits.

---

## Example Workflow

According to the source material:

1. A target colour is selected.
    
2. The selected colour is converted into white pixels.
    
3. Remaining image regions become dark or black.
    
4. White pixels are counted.
    
5. Total pixel count is compared against a reference image.
    
6. Upper and lower tolerances determine the inspection judgment.
    

---

# Tool Reference

The following tools are listed as available in ET XPro.

---

## Find Shape

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## 1D Code

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## 2D Code

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## OCR

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Blob

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Measure Position

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Width Measurement

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Fuzzy Measurement

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Fuzzy Position

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Diameter

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Colour Tool

### Purpose

Tool available in ET XPro.

### Documentation Status

Detailed documentation was not provided in the source material.

---

# Filter Guide

The following image processing filters are listed in the source material.

---

## Binary Filter

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Expand Filter

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Shrink Filter

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Blur Filter

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Sharp Filter

### Documentation Status

Detailed documentation was not provided in the source material.

---

## Bright Filter

### Documentation Status

Detailed documentation was not provided in the source material.

---

# Source Coverage Notes

The source material provides:

- Detailed documentation for the Pixel Count tool.
    
- Tool names for additional ET XPro inspection and measurement tools.
    
- Filter names available within the software.
    

No operational descriptions, configuration procedures, parameters, examples, or calculation methods were provided for the remaining tools and filters.
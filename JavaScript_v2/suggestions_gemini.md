# Manuscript Critique & Revision Roadmap

**Title:** *Moving Windows on Fixed Ground: Climate Adaptation as the Intersection of a Migrating Suitability Set and a Stationary Feasibility Set*  
**Author:** Simon-Hans Edasi (2026)  
**Target Journals:** *Nature Climate Change*, *Global Change Biology*, or *Environmental Research Letters*

---

## Executive Summary

The paper presents an exceptionally strong, mathematically elegant, and novel framework ($\mathcal{F}(\Delta T) = \mathcal{C}(\Delta T) \cap \mathcal{S}$) illustrating how decadal climate suitability migration intersects with geologically fixed terroir feasibility sets. The core finding—that the adaptation space contracts geometrically even when neither the climate window nor the terrain footprint shrinks—is intuitive, rigorous, and highly generalizable.

To maximize impact and withstand rigorous peer review, the following methodological, structural, and narrative adjustments are recommended.

---

## 1. High-Priority Methodological & Technical Revisions

### A. Clarify the Elevation–Temperature Collinearity
* **The Vulnerability:** Within the 150–950 m coffee belt, the Kodama et al. (2024) temperature climatology is heavily constrained by elevation ($R^2 = 0.999$, residual $SD = 0.032^\circ\text{C}$). Reviewers may argue that "gaining land concentrates at the upper fringe, which then runs out of footprint" is an artifact of the dataset's lapse rate.
* **Action Items:**
  - [ ] Explicitly state in **Section 4 (Discussion)** and **Section 6.4 (Methods)** that this high correlation is an inherent property of gridded climatological interpolations in steep island orography.
  - [ ] **Sensitivity Test (Optional but Strong):** Run an exploratory test where elevation is removed from the 8-feature topographic vector to observe how non-elevation features (aspect, slope, relief, coastal distance) alone define the Kona/Ka'u footprint boundaries.

### B. Reframing Out-of-Sample Behavior (Section 6.3 & Supp. Note S2)
* **The Vulnerability:** Reporting **0% recall on Kaua'i** and a **38% recovery rate on one spatial cross-validation fold** can be weaponized by reviewers questioning the validity of the terrain screen.
* **Action Items:**
  - [ ] Reframe the topographic screen in the main narrative from a general *"Arabica Suitability Mask"* to an **"Appellation / Terroir Identity Screen"**.
  - [ ] Emphasize that zero recall on Kaua'i is expected behavior (a feature, not a bug): Kaua'i is low-elevation plantation coffee (84 m, $7^\circ$ slope), whereas Kona/Ka'u are mountain-terroir designations (494–524 m, $17–19^\circ$ slope).
  - [ ] Add a brief explanatory sentence in Section 6.3 explaining the spatial anomaly in the 38% cross-validation fold (e.g., local micro-relief or steep elevation transitions in that latitude band).

### C. Elevate the Non-Uniform Warming Sensitivity
* **The Vulnerability:** Using a spatially uniform warming increment ($\Delta T$) is necessary due to CMIP6 grid resolution, but trade-wind inversion (TWI) dynamics in Hawai'i are elevation-dependent.
* **Action Items:**
  - [ ] Bring the elevation-dependent warming sweep ($g = 0\text{ to }2^\circ\text{C}\text{ km}^{-1}$) out of parenthetical methods text and highlight it in **Section 3.4** or **Supplementary Information**.
  - [ ] Frame uniform warming explicitly as the *conservative baseline*, showing that steepening $g$ actually accelerates the intersection contraction (Kona: -15.5% to -22.3%).

---

## 2. Narrative & Structural Enhancements

### A. Visualizing the "Pest Squeeze" (Coffee Berry Borer)
* **Insight:** Section 4 brilliantly demonstrates that the upper margin—the *only* gaining thermal fringe—faces the steepest proportional increases in Coffee Berry Borer (CBB) generation capacity (+34% to +51% by 2035).
* **Action Items:**
  - [ ] Add a small conceptual sub-panel to **Figure 4** or a dedicated Figure 5 illustrating the dual-axis squeeze on the adaptation corridor.
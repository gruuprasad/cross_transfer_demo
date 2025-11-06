# 🦾 Robotic Lab — USD Learning Project

A hands-on exploration of **Pixar USD (Universal Scene Description)** for an industrial automation context.  
Built step-by-step by writing USD scenes and Python scripts, not by using DCC tools like Blender.

---

## 🧭 Overview

This project simulates a **robotic lab environment** using **OpenUSD**, exploring key USD concepts:
- Stages, Prims, and Layers
- Composition (references, variants, sublayers)
- Animation via time samples
- Materials, lighting, and cameras

Each stage builds on the previous one, following a “learn by building” path.

---

## 🧠 Key Learnings

- **USD Composition** = Layers + Arcs  
  (Sublayers, References, Variants, Payloads, Inherits)
- **Layer order matters** — later sublayers are stronger.
- **References** introduce external prim hierarchies.
- **Variants** give behavioral or visual alternatives.
- **Time samples** enable smooth animation.

---

## 🧩 Example Commands

Run any stage script:
```bash
python scripts/stage3_lab_with_robots_modern.py

View in usdview:
```bash
usdview scenes/RobotLab.usda


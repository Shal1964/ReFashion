# 📚 ReFashion Documentation Index

## Start Here

### 🚀 New Users
1. **[README.md](README.md)** - Start here! Project overview, features, and quick start
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - User guide and usage examples
3. Run: `streamlit run app.py`

### 👨‍💻 Developers
1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and patterns
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview
3. **[TESTING.md](TESTING.md)** - Validation and testing guide

### ⚙️ Administrators
1. **[CONFIGURATION.md](CONFIGURATION.md)** - Customization guide
2. **[TESTING.md](TESTING.md)** - Validation checklist

### 📊 Stakeholders
1. **[TRANSFORMATION.md](TRANSFORMATION.md)** - Before/after comparison
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Key achievements

---

## Documentation Files

| File | Purpose | When to Read |
|------|---------|-------------|
| **[README.md](README.md)** | Main documentation, features, setup | First time, always |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | User guide, quick tips | Daily usage |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design, data flow | Understanding code |
| **[TRANSFORMATION.md](TRANSFORMATION.md)** | Before/after analysis | Understanding changes |
| **[TESTING.md](TESTING.md)** | Test cases, validation | QA, debugging |
| **[CONFIGURATION.md](CONFIGURATION.md)** | Customization options | Changing settings |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Complete overview | High-level view |

---

## Code Files

### 🎨 Application
| File | Purpose | Lines |
|------|---------|-------|
| **[app.py](app.py)** | Main Streamlit application (NEW) | ~400 |
| **[main.py](main.py)** | Legacy chatbot (reference) | ~876 |

### 🧠 Core System
| File | Purpose | Lines |
|------|---------|-------|
| **[core/data_layer.py](core/data_layer.py)** | Data access & brand lookup | ~60 |
| **[core/logic_layer.py](core/logic_layer.py)** | EcoScore calculation | ~120 |
| **[core/llm_formatter.py](core/llm_formatter.py)** | Constrained LLM interface | ~140 |

### 🎯 Features
| File | Purpose | Lines |
|------|---------|-------|
| **[features/ecoscore_calculator.py](features/ecoscore_calculator.py)** | Feature 1: Score calculation | ~90 |
| **[features/product_advisor.py](features/product_advisor.py)** | Feature 2: Product analysis | ~140 |
| **[features/impact_awareness.py](features/impact_awareness.py)** | Feature 3: Impact education | ~90 |
| **[features/shopping_assistant.py](features/shopping_assistant.py)** | Feature 4: Shopping guidance | ~150 |

### 🤖 Machine Learning
| File | Purpose |
|------|---------|
| **[regression/ml_predictor.py](regression/ml_predictor.py)** | ML-based EcoScore prediction |
| **[regression/train_model.py](regression/train_model.py)** | Model training script |
| **[regression/visualize_model.py](regression/visualize_model.py)** | Model visualization |

### 🛠️ Utilities
| File | Purpose |
|------|---------|
| **[utils/chart_renderer.py](utils/chart_renderer.py)** | Plotly visualization helpers |

---

## Common Tasks

### 🚀 Running the Application
```bash
streamlit run app.py
```
See: [README.md](README.md) → Quick Start

### 🔧 Configuring API Key
See: [CONFIGURATION.md](CONFIGURATION.md) → Environment Setup

### 🧪 Testing
See: [TESTING.md](TESTING.md) → Quick Validation Tests

### 🎨 Customizing UI
See: [CONFIGURATION.md](CONFIGURATION.md) → UI Customization

### 📊 Changing Score Weights
See: [CONFIGURATION.md](CONFIGURATION.md) → Score Calculation

### 🤖 Modifying LLM Behavior
See: [CONFIGURATION.md](CONFIGURATION.md) → LLM Configuration

### 🔍 Understanding Architecture
See: [ARCHITECTURE.md](ARCHITECTURE.md) → Layer Separation

### 📈 Viewing Changes
See: [TRANSFORMATION.md](TRANSFORMATION.md) → Before vs After

---

## Learning Path

### Beginner (User)
1. Read **[README.md](README.md)** - Understand what it does
2. Run `streamlit run app.py`
3. Follow **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Try each feature
4. Check **[TESTING.md](TESTING.md)** - Validate it works

### Intermediate (Developer)
1. Read **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand design
2. Explore `core/` modules - See separation of concerns
3. Explore `features/` modules - See feature implementation
4. Read **[CONFIGURATION.md](CONFIGURATION.md)** - Learn customization

### Advanced (Contributor)
1. Read **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Full context
2. Read **[TRANSFORMATION.md](TRANSFORMATION.md)** - Design decisions
3. Modify code following patterns in **[ARCHITECTURE.md](ARCHITECTURE.md)**
4. Test changes using **[TESTING.md](TESTING.md)**

---

## Quick Navigation

### By Topic

**Setup & Installation**
- [README.md](README.md) → Quick Start
- [CONFIGURATION.md](CONFIGURATION.md) → Environment Setup

**Using the System**
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → User Guide
- [README.md](README.md) → 4 Core Features

**Understanding Design**
- [ARCHITECTURE.md](ARCHITECTURE.md) → System Design
- [TRANSFORMATION.md](TRANSFORMATION.md) → Design Decisions

**Customization**
- [CONFIGURATION.md](CONFIGURATION.md) → All customization options
- [ARCHITECTURE.md](ARCHITECTURE.md) → Module Responsibilities

**Quality Assurance**
- [TESTING.md](TESTING.md) → Test Cases
- [TESTING.md](TESTING.md) → Success Criteria

**Project Overview**
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) → Complete overview
- [TRANSFORMATION.md](TRANSFORMATION.md) → Key achievements

### By Role

**End User**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Developer**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**Admin**
→ [CONFIGURATION.md](CONFIGURATION.md)

**Tester**
→ [TESTING.md](TESTING.md)

**Manager/Stakeholder**
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**New Team Member**
→ [README.md](README.md) → [ARCHITECTURE.md](ARCHITECTURE.md) → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## File Sizes

| Documentation | ~Size |
|---------------|-------|
| README.md | 10 KB |
| ARCHITECTURE.md | 8 KB |
| QUICK_REFERENCE.md | 6 KB |
| TRANSFORMATION.md | 7 KB |
| TESTING.md | 7 KB |
| CONFIGURATION.md | 8 KB |
| PROJECT_SUMMARY.md | 7 KB |

| Code | ~Lines |
|------|--------|
| app.py | 400 |
| main.py (legacy) | 876 |
| Core modules | 320 |
| Feature modules | 470 |
| Total new code | 1,190 |

---

## Search Guide

### Looking for...

**How to run?**
→ [README.md](README.md) → Quick Start

**How to configure?**
→ [CONFIGURATION.md](CONFIGURATION.md)

**How to test?**
→ [TESTING.md](TESTING.md)

**How it works?**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**What changed?**
→ [TRANSFORMATION.md](TRANSFORMATION.md)

**Feature overview?**
→ [README.md](README.md) → 4 Core Features

**Code structure?**
→ [ARCHITECTURE.md](ARCHITECTURE.md) → Layer Separation

**Customization?**
→ [CONFIGURATION.md](CONFIGURATION.md)

**LLM constraints?**
→ [README.md](README.md) → Constrained LLM Assistant
→ [ARCHITECTURE.md](ARCHITECTURE.md) → Constraint Enforcement

**Design patterns?**
→ [ARCHITECTURE.md](ARCHITECTURE.md) → Design Patterns Applied

---

## Visual Guide

```
📁 ReFashion/
├── 📘 Start Here: README.md
├── 🎯 User Guide: QUICK_REFERENCE.md
├── 🏗️ Architecture: ARCHITECTURE.md
├── 🔄 Changes: TRANSFORMATION.md
├── ✅ Testing: TESTING.md
├── ⚙️ Config: CONFIGURATION.md
├── 📊 Summary: PROJECT_SUMMARY.md
│
├── 🚀 Run This: app.py
├── 📜 Reference: main.py
│
├── 🧠 Core Logic/
├── 🎯 Features/
├── 🤖 ML Models/
└── 📊 Data/
```

---

## Cheat Sheet

| Need to... | Go to... |
|-----------|----------|
| Start app | `streamlit run app.py` |
| Set API key | `.streamlit/secrets.toml` |
| Change colors | `app.py` → styles |
| Adjust scores | `core/logic_layer.py` → weights |
| Modify LLM | `core/llm_formatter.py` → payload |
| Add material | `features/product_advisor.py` → MATERIALS |
| Add topic | `features/impact_awareness.py` → TOPICS |
| Test system | Follow `TESTING.md` |
| Debug | Enable DEBUG in `app.py` |

---

## Support

**Questions?** Check documentation in this order:
1. [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. [README.md](README.md)
3. [CONFIGURATION.md](CONFIGURATION.md)
4. [TESTING.md](TESTING.md)

**Issues?** See:
- [TESTING.md](TESTING.md) → Common Issues & Fixes
- [CONFIGURATION.md](CONFIGURATION.md) → Troubleshooting section

**Contributing?** Read:
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand design
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) → Contributing section
3. Follow existing patterns

---

**Last Updated**: December 2024
**Documentation Version**: 1.0
**Project Status**: ✅ Complete

# ReFashion System - Quick Reference Guide

## 🚀 Launch the Application

```bash
streamlit run app.py
```

## 📋 System Overview

### Architecture Pattern: **Strict Separation of Concerns**

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Data Layer  │ --> │ Logic Layer  │ --> │ LLM Formatter│
│ (facts)     │     │ (compute)    │     │ (structure)  │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 🎯 4 Core Features

### 1. Eco Score Calculator
**Purpose**: Calculate & explain brand sustainability scores

**Usage**:
- Single Brand Analysis: Select brand → Calculate
- Brand Comparison: Select 2+ brands → Compare

**Output**:
- Numerical score (0-100)
- Verdict (Excellent/Good/Moderate/Poor/Very Poor)
- LLM-formatted explanation (table + bullets)
- Raw metrics (carbon, water, waste, wages, etc.)

---

### 2. Product Sustainability Advisor
**Purpose**: Analyze specific products and materials

**Usage**:
- Analyze Product: Select type + brand + materials → Analyze
- Material Guide: Enter use case → Get recommendations

**Output**:
- Overall sustainability score
- Material-by-material breakdown (recommended/avoid)
- Structured checklist (tables, bullets)

---

### 3. Fashion Impact Awareness
**Purpose**: Learn about industry impacts through data

**Usage**:
- Fast Fashion Impact: Click to get summary
- Industry Topics: Select topic → Learn

**Available Topics**:
- Fast fashion
- Water usage
- Carbon emissions
- Textile waste
- Labor rights
- Microplastics
- Chemical pollution

**Output**:
- Statistical tables
- Bullet-point facts
- Action checklists

---

### 4. Conscious Shopping Assistant
**Purpose**: Make informed purchase decisions

**Usage**:
- Find Brands: Set min score → Search
- Get Alternatives: Select brand → Find better options
- Shopping Checklist: Select category → Generate

**Output**:
- Comparison tables
- Alternative recommendations
- Checklist format (actionable items)

---

## 🤖 LLM Constraints

### What the AI CAN do:
✅ Explain EcoScore numbers
✅ Summarize statistics
✅ Format as tables/bullets/checklists
✅ Provide structured recommendations

### What the AI CANNOT do:
❌ Free-form conversation
❌ Answer questions outside 4 functions
❌ Write long paragraphs
❌ Engage in general fashion chat

---

## 📊 Output Format Examples

### Table Format (Comparisons)
```markdown
| Brand | EcoScore | Carbon | Verdict |
|-------|----------|--------|---------|
| H&M   | 45       | 8500   | Poor    |
| Zara  | 48       | 8200   | Poor    |
```

### Bullet Points (Facts)
```markdown
• Carbon emissions 37% above industry average
• 24 fashion cycles per year (fast fashion)
• Limited supply chain transparency
```

### Checklist (Actions)
```markdown
- [ ] Look for GOTS certification
- [ ] Check transparency score > 70
- [ ] Verify fair wage policies
```

---

## 🔧 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `core/data_layer.py` | Data access & brand lookup |
| `core/logic_layer.py` | EcoScore calculation |
| `core/llm_formatter.py` | Constrained LLM interface |
| `features/ecoscore_calculator.py` | Feature 1 |
| `features/product_advisor.py` | Feature 2 |
| `features/impact_awareness.py` | Feature 3 |
| `features/shopping_assistant.py` | Feature 4 |

---

## 🎨 UI Structure

```
Sidebar:
  - Feature selector (1-4)
  - AI scope reminder

Main Area:
  Tab 1: Primary function
  Tab 2: Secondary function
  Tab 3: Additional function (if applicable)
```

---

## 🔑 Configuration

### API Key Setup
`.streamlit/secrets.toml`:
```toml
DEEPINFRA_API_KEY = "your_key"
```

### LLM Parameters
In `core/llm_formatter.py`:
```python
temperature = 0.2    # Consistency
max_tokens = 500     # Brevity
```

---

## 💡 Usage Tips

1. **Start with Feature 1**: Get familiar with EcoScore calculation
2. **Use comparisons**: Compare 2-3 brands to see differences
3. **Check raw data**: Expand "View Raw Data" to see all metrics
4. **Shopping Assistant**: Use Feature 4 to find better alternatives
5. **Material matters**: Feature 2 helps understand fabric impact

---

## 🚨 Important Constraints

### Design Principles
- No free-form chatbot
- Structured output only
- Clear separation: data → logic → formatting
- Concise information (no long paragraphs)
- LLM limited to 4 specific functions

### User Experience
- Select from dropdowns (no free text for brands)
- Structured tabs for features
- Visual metrics (cards, charts)
- Expandable raw data sections

---

## 📈 Data Source

- **Dataset**: `true_cost_fast_fashion.csv`
- **Brands**: 50+ fashion companies
- **Years**: 2015-2024
- **Metrics**: 15+ sustainability indicators

---

## 🎯 System Goals

✅ Data-driven insights (not opinions)
✅ Structured, scannable output
✅ Clear action items
✅ Separation of facts and formatting
✅ Consistent user experience

---

## 🛠️ Troubleshooting

**Issue**: LLM returns long responses
**Fix**: Check `max_tokens=500` in `llm_formatter.py`

**Issue**: Unstructured output
**Fix**: Verify `STRICT_SYSTEM_PROMPT` is active

**Issue**: Brand not found
**Fix**: Use dropdown selector (don't type names)

**Issue**: API key error
**Fix**: Check `.streamlit/secrets.toml` or environment variable

---

**Remember**: This is NOT a general chatbot. It's a structured system with 4 specific functions and constrained AI formatting.

# ReFashion - Structured Sustainable Fashion System

A data-driven sustainability platform with **constrained AI assistance** for fashion industry analysis.

## 🎯 System Requirements

### 4 Core Features

#### 1. 🔢 Eco Score Calculator
- Calculate sustainability scores for fashion brands
- Compare multiple brands side-by-side
- Get structured explanations of score components
- View detailed environmental and labor metrics

#### 2. 👕 Product Sustainability Advisor
- Analyze specific products (brand + materials)
- Get material sustainability ratings
- Receive structured buying advice
- Compare material impact scores

#### 3. 📚 Fashion Impact Awareness
- Learn about fast fashion impacts
- Explore industry statistics
- Understand environmental topics (water, carbon, waste, etc.)
- Access structured, data-driven summaries

#### 4. 🛍️ Conscious Shopping Assistant
- Find sustainable brand recommendations
- Get better alternatives for any brand
- Access shopping checklists by category
- Compare purchase options

## 🤖 Constrained LLM Assistant

The AI assistant is **strictly limited** to:

### Allowed Functions
✅ **Explaining EcoScore results** - Interpreting numerical scores and metrics
✅ **Summarizing fast fashion impacts** - Presenting statistical data
✅ **Providing structured recommendations** - Actionable steps based on data
✅ **Formatting output** - Tables, bullet points, checklists, numbered lists

### Output Formatting
- **Tables**: Comparisons and metrics
- **Bullet points (•)**: Lists of facts
- **Checkboxes (- [ ])**: Actionable recommendations
- **Numbered lists**: Sequential steps

### Design Constraints
❌ No free-form chatbot conversations
❌ No long paragraphs (max 2-3 sentences)
❌ No answers outside the 4 functions
❌ Clear separation: logic → data → language generation

## 🏗️ Architecture

```
ReFashion/
├── core/
│   ├── data_layer.py          # Data access & brand detection
│   ├── logic_layer.py          # EcoScore calculation logic
│   └── llm_formatter.py        # Constrained LLM output formatting
├── features/
│   ├── ecoscore_calculator.py  # Feature 1: Score calculation
│   ├── product_advisor.py      # Feature 2: Product analysis
│   ├── impact_awareness.py     # Feature 3: Impact education
│   └── shopping_assistant.py   # Feature 4: Shopping guidance
├── regression/
│   ├── ml_predictor.py         # ML-based EcoScore prediction
│   ├── train_model.py
│   └── visualize_model.py
├── utils/
│   └── chart_renderer.py       # Visualization utilities
├── model/                      # Trained ML models
├── app.py                      # Main Streamlit application
├── main.py                     # Legacy chatbot (reference)
└── true_cost_fast_fashion.csv  # Dataset
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit pandas numpy joblib scikit-learn plotly requests
```

### 2. Set API Key
Create `.streamlit/secrets.toml`:
```toml
DEEPINFRA_API_KEY = "your_api_key_here"
```

Or set environment variable:
```bash
export DEEPINFRA_API_KEY="your_api_key_here"
```

### 3. Run Application
```bash
streamlit run app.py
```

## 📊 Key Features in Detail

### Eco Score Calculator
- **Input**: Brand name
- **Output**:
  - Numerical score (0-100)
  - Category breakdown (carbon, water, labor, waste, transparency)
  - Structured explanation via LLM
  - Industry comparison

### Product Sustainability Advisor
- **Input**: Product type, brand (optional), materials
- **Output**:
  - Overall sustainability score
  - Material-by-material analysis
  - Structured buying checklist
  - Recommendations formatted as tables

### Fashion Impact Awareness
- **Topics**: Fast fashion, water usage, carbon emissions, textile waste, labor rights, microplastics, chemical pollution
- **Output**:
  - Data tables with statistics
  - Bullet-point fact summaries
  - Action checklists

### Conscious Shopping Assistant
- **Functions**:
  - Find brands by minimum EcoScore
  - Get alternatives to specific brands
  - Generate category-specific shopping checklists
  - Compare multiple brands

## 🔒 LLM Constraints Implementation

### System Prompt Structure
```python
STRICT_SYSTEM_PROMPT = """
You are a structured sustainability data formatter.
Strictly limited to:
1. Explaining EcoScore results
2. Summarizing fast fashion impacts
3. Providing structured recommendations
4. Formatting output (tables/bullets/checklists)

DO NOT engage in free-form conversation.
ALWAYS use structured formatting.
Max 2-3 sentences per point.
"""
```

### Output Validation
- Max tokens: 500 (prevents long responses)
- Temperature: 0.2 (consistent, factual output)
- Prompt engineering: Forces specific formats
- Context separation: Data provided separately from instructions

## 📈 Data Processing Flow

```
User Input → Data Layer → Logic Layer → LLM Formatter → Structured Output
     ↓            ↓             ↓              ↓                ↓
  "Nike"    Brand Data    EcoScore: 45   Format as      Table + Bullets
                          Verdict: Poor   table/list     + Checkboxes
```

## 🧪 Example Usage

### Calculate EcoScore
```python
from core.data_layer import DataLayer
from core.llm_formatter import LLMFormatter
from features.ecoscore_calculator import EcoScoreCalculator

data_layer = DataLayer("true_cost_fast_fashion.csv")
llm_formatter = LLMFormatter(api_key, api_url, model)
calculator = EcoScoreCalculator(data_layer, llm_formatter)

result = calculator.get_explanation("H&M")
print(result['explanation'])  # Structured table + bullets
```

### Get Shopping Alternatives
```python
from features.shopping_assistant import ConsciousShoppingAssistant

assistant = ConsciousShoppingAssistant(data_layer, llm_formatter)
result = assistant.get_alternatives_for_brand("Zara", count=5)

print(result['structured_recommendations'])  # Checklist format
```

## 🎨 UI Features

- **Tab-based navigation**: Organized by 4 main features
- **Metric cards**: Visual score displays
- **Structured output areas**: Dedicated sections for LLM-formatted content
- **Data tables**: Raw data always accessible
- **Gradient designs**: Clear visual hierarchy

## 📝 Output Examples

### EcoScore Explanation (Structured)
```markdown
### Score Interpretation
H&M receives 45/100 - Poor rating due to high environmental impact.

| Metric | H&M | Industry Avg | Status |
|--------|-----|--------------|--------|
| Carbon | 8500 tCO2e | 6200 tCO2e | ⚠️ High |
| Water | 220M L | 180M L | ⚠️ High |
| Transparency | 52/100 | 68/100 | ⚠️ Low |

**Key Issues:**
• 37% above industry average carbon emissions
• Limited supply chain transparency
• Fast fashion model (24 cycles/year)
```

### Shopping Recommendations (Checklist)
```markdown
- [ ] Look for GOTS or Fair Trade certifications
- [ ] Check brand transparency score (aim for 70+)
- [ ] Verify worker wage data availability
- [ ] Consider brands: Patagonia, Eileen Fisher, Reformation
```

## 🔧 Configuration

### Adjust LLM Constraints
Edit `core/llm_formatter.py`:
```python
payload = {
    "temperature": 0.2,  # Lower = more consistent
    "max_tokens": 500,   # Prevents long responses
}
```

### Modify Score Weights
Edit `core/logic_layer.py`:
```python
weights = {
    "carbon": 0.12,
    "transparency": 0.08,
    # ... adjust as needed
}
```

## 📊 Dataset

`true_cost_fast_fashion.csv` includes:
- 50+ fashion brands
- 2015-2024 data
- Metrics: carbon, water, waste, wages, transparency, compliance, etc.

## 🚫 Anti-Patterns Avoided

❌ Free-form chatbot that answers anything
❌ Long conversational paragraphs
❌ Mixed logic and presentation
❌ Unstructured LLM outputs
❌ No clear separation of concerns

## ✅ Design Principles Followed

✅ Strict feature boundaries (4 functions only)
✅ Constrained LLM with specific formatting
✅ Separation: Data → Logic → Language
✅ Structured output (tables/bullets/checklists)
✅ Concise, scannable information
✅ Consistent formatting patterns

## 📄 License

MIT

## 🤝 Contributing

This is a structured system - maintain the following when contributing:
1. Keep LLM prompts constrained to 4 functions
2. Use structured output formats only
3. Separate data, logic, and formatting layers
4. Avoid adding free-form conversation features

---

**Built with**: Streamlit, Python, DeepSeek LLM (constrained)
**Focus**: Structured, data-driven sustainability insights

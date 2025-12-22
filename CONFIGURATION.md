# Configuration & Customization Guide

## Environment Setup

### 1. API Key Configuration

**Option A: Streamlit Secrets (Recommended)**
Create `.streamlit/secrets.toml`:
```toml
DEEPINFRA_API_KEY = "your_deepinfra_api_key_here"
```

**Option B: Environment Variable**
```bash
export DEEPINFRA_API_KEY="your_deepinfra_api_key_here"
```

---

## LLM Configuration

### File: `core/llm_formatter.py`

#### Adjust Response Length
```python
payload = {
    "max_tokens": 500,  # Default: 500
    # Reduce to 300 for shorter responses
    # Increase to 800 for more detailed output
}
```

#### Adjust Consistency/Creativity
```python
payload = {
    "temperature": 0.2,  # Default: 0.2 (more consistent)
    # 0.1 = Very consistent, minimal variation
    # 0.3 = Slightly more creative
    # 0.5 = More variation (not recommended)
}
```

#### Change LLM Provider
```python
def __init__(self, api_key: str, api_url: str, model_name: str):
    self.api_url = api_url
    # Change to: "https://api.openai.com/v1/chat/completions"

    self.model_name = model_name
    # Change to: "gpt-4" or "gpt-3.5-turbo"
```

---

## Score Calculation

### File: `core/logic_layer.py`

#### Adjust EcoScore Weights
```python
weights = {
    "carbon": 0.12,        # Carbon emissions weight
    "water": 0.08,         # Water usage weight
    "waste": 0.08,         # Landfill waste weight
    "release": 0.05,       # Release cycles weight
    "child_labor": 0.10,   # Child labor incidents weight
    "hours": 0.05,         # Working hours weight
    "wage": 0.10,          # Worker wage weight
    "transparency": 0.08,  # Transparency index weight
    "compliance": 0.08,    # Compliance score weight
    "ethical": 0.10,       # Ethical rating weight
    "sustainability": 0.10, # Sustainability score weight
    "env_cost": 0.06,      # Environmental cost weight
}
# Ensure total = 1.00
```

#### Change Verdict Thresholds
```python
@staticmethod
def get_verdict(score: float) -> tuple[str, str]:
    if score >= 85:        # Change threshold
        return "Excellent", "🌟"
    elif score >= 70:      # Change threshold
        return "Good", "✅"
    elif score >= 65:      # Change threshold
        return "Moderate", "⚠️"
    elif score >= 30:      # Change threshold
        return "Poor", "🔶"
    else:
        return "Very Poor", "❌"
```

---

## Product Advisor Configuration

### File: `features/product_advisor.py`

#### Add/Modify Materials
```python
SUSTAINABLE_MATERIALS = {
    "organic cotton": {"score": 85, "impact": "Low water, no pesticides"},
    "recycled polyester": {"score": 75, "impact": "Reduces plastic waste"},
    # Add new material:
    "bamboo": {"score": 82, "impact": "Fast growing, sustainable"},
}

AVOID_MATERIALS = {
    "virgin polyester": {"score": 30, "impact": "Petroleum-based"},
    # Add material to avoid:
    "rayon": {"score": 40, "impact": "Chemical-intensive production"},
}
```

#### Adjust Score Calculation
```python
# Current: 40% brand, 60% materials
overall_score = (brand_score * 0.4 + avg_material * 0.6)

# Change to: 50% brand, 50% materials
overall_score = (brand_score * 0.5 + avg_material * 0.5)
```

---

## Impact Awareness Configuration

### File: `features/impact_awareness.py`

#### Add New Topics
```python
IMPACT_TOPICS = {
    "fast_fashion": "Environmental and social impacts...",
    "water_usage": "Water consumption in textile production",
    # Add new topic:
    "recycling": "Textile recycling and circular fashion",
    "certifications": "Sustainability certifications explained",
}
```

---

## Shopping Assistant Configuration

### File: `features/shopping_assistant.py`

#### Change Default Thresholds
```python
def get_brand_recommendations(self,
                              min_score: float = 70,  # Change default
                              max_results: int = 10): # Change default
```

#### Adjust Alternative Selection
```python
# Current: Alternatives must be 15+ points better
if result['ecoscore'] > current_score + 15:

# Change to: 10+ points better
if result['ecoscore'] > current_score + 10:
```

---

## UI Customization

### File: `app.py`

#### Change Color Scheme
```python
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    # Change to: linear-gradient(135deg, #667eea 0%, #4CAF50 100%)
}
.metric-card {
    background: linear-gradient(135deg, #B7D292 0%, #9cb87a 100%);
    # Change to your brand colors
}
</style>
""", unsafe_allow_html=True)
```

#### Modify Feature Names
```python
feature = st.radio(
    "Select Feature:",
    [
        "1️⃣ Eco Score Calculator",      # Rename as needed
        "2️⃣ Product Advisor",            # Simplify
        "3️⃣ Impact Awareness",           # Customize
        "4️⃣ Shopping Assistant"          # Rebrand
    ]
)
```

#### Add Logo/Branding
```python
# In app.py, add after set_page_config:
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("your_logo.png", width=300)
```

---

## Data Source Configuration

### File: `core/data_layer.py`

#### Change CSV File
```python
def __init__(self, csv_path: str = "true_cost_fast_fashion.csv"):
    # Change to point to different file
    self.df = pd.read_csv(csv_path)
```

#### Add Data Filtering
```python
def __init__(self, csv_path: str):
    self.df = pd.read_csv(csv_path)

    # Filter to recent years only
    self.df = self.df[self.df['Year'] >= 2020]

    # Filter to specific regions
    # self.df = self.df[self.df['Region'] == 'Europe']
```

---

## Advanced Configurations

### Enable Debug Mode
```python
# In app.py
DEBUG = True  # Set to True for debugging

if DEBUG:
    st.sidebar.write("Debug Info")
    st.sidebar.json({
        "data_points": len(data_layer.df),
        "brands_count": len(data_layer.get_brand_list())
    })
```

### Add Caching for Performance
```python
# In features files
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_score_cached(brand_name: str):
    # Cached calculation
    pass
```

### Logging
```python
# Add to any file
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In functions:
logger.info(f"Calculating score for {brand_name}")
```

---

## Prompt Engineering

### Modify System Prompts

**Make LLM More Concise:**
```python
STRICT_SYSTEM_PROMPT = """
...existing prompt...

CRITICAL: Keep ALL responses under 3 sentences per section.
Use ONLY tables and bullet points. NO paragraphs.
"""
```

**Add Specific Format Requirements:**
```python
STRICT_SYSTEM_PROMPT = """
...existing prompt...

Table format:
| Column1 | Column2 | Column3 |
|---------|---------|---------|
| data    | data    | data    |

Bullet format:
• Point 1 (max 10 words)
• Point 2 (max 10 words)

Checklist format:
- [ ] Action 1 (imperative verb)
- [ ] Action 2 (imperative verb)
"""
```

---

## Feature Toggle

### Enable/Disable Features
```python
# In app.py
ENABLED_FEATURES = {
    "ecoscore": True,
    "product_advisor": True,
    "impact_awareness": True,
    "shopping_assistant": True,
}

# Then conditionally show:
if ENABLED_FEATURES["ecoscore"]:
    feature_options.append("1️⃣ Eco Score Calculator")
```

---

## Performance Tuning

### Reduce API Calls
```python
# Cache LLM responses
from streamlit import cache_data

@cache_data(ttl=3600)  # Cache for 1 hour
def get_llm_response(prompt, context):
    return llm_formatter._call_llm(prompt, context)
```

### Optimize Data Loading
```python
# In data_layer.py
@st.cache_resource
def load_data(csv_path: str):
    return pd.read_csv(csv_path)

# Use in __init__:
self.df = load_data(csv_path)
```

---

## Multi-Language Support (Future)

### Structure for Internationalization
```python
# Create translations.py
TRANSLATIONS = {
    "en": {
        "ecoscore_title": "Eco Score Calculator",
        "calculate_button": "Calculate EcoScore"
    },
    "es": {
        "ecoscore_title": "Calculadora de EcoScore",
        "calculate_button": "Calcular EcoScore"
    }
}

# Use in app.py:
lang = st.sidebar.selectbox("Language", ["en", "es"])
st.title(TRANSLATIONS[lang]["ecoscore_title"])
```

---

## Environment-Specific Configs

### Development vs Production
```python
# config.py
import os

ENV = os.getenv("APP_ENV", "development")

if ENV == "production":
    DEBUG = False
    CACHE_TTL = 3600
    MAX_RESULTS = 10
else:
    DEBUG = True
    CACHE_TTL = 60
    MAX_RESULTS = 5
```

---

## Testing Configurations

### Mock LLM for Testing
```python
# In llm_formatter.py
class MockLLMFormatter(LLMFormatter):
    def _call_llm(self, prompt, context):
        # Return mock response instead of API call
        return "| Brand | Score |\n|-------|-------|\n| Test | 50 |"

# Use in tests:
formatter = MockLLMFormatter("", "", "")
```

---

## Summary: Key Configuration Points

| What to Configure | Where | When |
|-------------------|-------|------|
| API Keys | `.streamlit/secrets.toml` | Always (required) |
| LLM Provider | `core/llm_formatter.py` | If changing from DeepInfra |
| Score Weights | `core/logic_layer.py` | To adjust priorities |
| Verdict Thresholds | `core/logic_layer.py` | To change ratings |
| Materials List | `features/product_advisor.py` | To add/remove materials |
| UI Colors | `app.py` | For branding |
| Response Length | `core/llm_formatter.py` | If too long/short |
| Temperature | `core/llm_formatter.py` | For consistency |

---

**Best Practice**: Make configuration changes incrementally and test after each change.

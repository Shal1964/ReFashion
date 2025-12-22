# ReFashion System Architecture

## Layer Separation

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│                           (app.py)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Feature 1 │  │Feature 2 │  │Feature 3 │  │Feature 4 │       │
│  │EcoScore  │  │Product   │  │Impact    │  │Shopping  │       │
│  │Calculator│  │Advisor   │  │Awareness │  │Assistant │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
┌───────┼─────────────┼─────────────┼─────────────┼──────────────┐
│       │             │             │             │               │
│       ▼             ▼             ▼             ▼               │
│  ┌──────────────────────────────────────────────────┐          │
│  │           FEATURE LAYER (features/)              │          │
│  │  • ecoscore_calculator.py                        │          │
│  │  • product_advisor.py                            │          │
│  │  • impact_awareness.py                           │          │
│  │  • shopping_assistant.py                         │          │
│  └────────────┬────────────────┬────────────────────┘          │
│               │                │                                │
└───────────────┼────────────────┼────────────────────────────────┘
                │                │
┌───────────────┼────────────────┼────────────────────────────────┐
│               ▼                ▼                                │
│  ┌─────────────────┐  ┌──────────────────┐                    │
│  │   DATA LAYER    │  │   LOGIC LAYER    │                    │
│  │ data_layer.py   │  │ logic_layer.py   │                    │
│  │                 │  │                  │                    │
│  │ • Load CSV      │  │ • Calculate      │                    │
│  │ • Brand lookup  │  │   EcoScore       │                    │
│  │ • Get stats     │  │ • Normalize      │                    │
│  │ • Detect brands │  │ • Get verdict    │                    │
│  └────────┬────────┘  └────────┬─────────┘                    │
│           │                    │                                │
│           ▼                    │                                │
│  ┌──────────────────┐          │                                │
│  │ Database/CSV     │          │                                │
│  │ true_cost_fast   │          │                                │
│  │ _fashion.csv     │          │                                │
│  └──────────────────┘          │                                │
│                                 │                                │
│  ┌──────────────────────────────┼────────────────┐             │
│  │         FORMATTING LAYER     │                │             │
│  │         llm_formatter.py     │                │             │
│  │                              │                │             │
│  │  • Constrained prompts       ◄────────────────┘             │
│  │  • Format as tables/bullets                   │             │
│  │  • Max 500 tokens                             │             │
│  │  • Temperature 0.2                            │             │
│  │  • 4 functions ONLY                           │             │
│  └───────────────────────────────────────────────┘             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: EcoScore Calculation

```
User selects "H&M" in app.py
        |
        ▼
ecoscore_calculator.get_explanation("H&M")
        |
        ▼
data_layer.get_brand_data("H&M")
        |
        ▼
Returns: DataFrame with H&M records
        |
        ▼
logic_layer.calculate_ecoscore(brand_data, full_dataset)
        |
        ▼
Returns: {ecoscore: 45, carbon: 8500, ...}
        |
        ▼
llm_formatter.explain_ecoscore("H&M", 45, metrics)
        |
        ▼
LLM API Call with constrained prompt
        |
        ▼
Returns: Structured markdown (table + bullets)
        |
        ▼
Display in Streamlit UI
```

## Constraint Enforcement

```
┌─────────────────────────────────────────┐
│     LLM FORMATTER (Gatekeeper)          │
│                                         │
│  STRICT_SYSTEM_PROMPT:                  │
│  "You are limited to:                   │
│   1. EcoScore explanations              │
│   2. Fast fashion summaries             │
│   3. Structured recommendations         │
│   4. Formatted output"                  │
│                                         │
│  ┌────────────────────────────────┐    │
│  │ Allowed Requests:              │    │
│  │ ✓ explain_ecoscore()           │    │
│  │ ✓ summarize_fast_fashion()     │    │
│  │ ✓ provide_recommendations()    │    │
│  │ ✓ format_comparison_table()    │    │
│  │ ✓ format_product_advice()      │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │ Blocked Requests:              │    │
│  │ ✗ General chat                 │    │
│  │ ✗ Fashion trends               │    │
│  │ ✗ Styling advice               │    │
│  │ ✗ Unstructured responses       │    │
│  └────────────────────────────────┘    │
│                                         │
│  Output Controls:                       │
│  • max_tokens: 500                      │
│  • temperature: 0.2                     │
│  • Format enforcement in prompt         │
└─────────────────────────────────────────┘
```

## Feature-Specific Flows

### Feature 1: Eco Score Calculator
```
Input: Brand name(s)
  ↓
Data Layer: Get brand records
  ↓
Logic Layer: Calculate weighted score
  ↓
LLM Formatter: Structure explanation
  ↓
Output: Score + table + bullets
```

### Feature 2: Product Sustainability Advisor
```
Input: Product type + brand + materials
  ↓
Logic Layer: Score brand & materials
  ↓
LLM Formatter: Create advice checklist
  ↓
Output: Score + material analysis + checklist
```

### Feature 3: Fashion Impact Awareness
```
Input: Topic selection
  ↓
Data Layer: Get impact statistics
  ↓
LLM Formatter: Summarize with tables
  ↓
Output: Stats table + fact bullets + action checklist
```

### Feature 4: Conscious Shopping Assistant
```
Input: Criteria (min score, category, brand)
  ↓
Logic Layer: Filter & rank brands
  ↓
LLM Formatter: Create comparison table
  ↓
Output: Recommendation table + checklist
```

## Security & Constraints

```
┌─────────────────────────────────────────┐
│      Constraint Enforcement             │
├─────────────────────────────────────────┤
│ 1. Prompt Engineering                   │
│    ✓ Explicit function definitions      │
│    ✓ "DO NOT" statements                │
│    ✓ Format requirements                │
│                                         │
│ 2. Token Limiting                       │
│    ✓ max_tokens = 500                   │
│    ✓ Prevents rambling                  │
│                                         │
│ 3. Temperature Control                  │
│    ✓ temperature = 0.2                  │
│    ✓ Consistent, factual output         │
│                                         │
│ 4. Context Separation                   │
│    ✓ Data in separate context block     │
│    ✓ Instructions in system prompt      │
│                                         │
│ 5. Function Boundaries                  │
│    ✓ Only 5 methods in LLMFormatter     │
│    ✓ No generic chat endpoint           │
└─────────────────────────────────────────┘
```

## Module Responsibilities

| Module | Responsibility | NOT Responsible For |
|--------|----------------|---------------------|
| `data_layer.py` | Load CSV, lookup brands, get stats | Calculations, formatting |
| `logic_layer.py` | Calculate scores, normalize, rank | Data access, formatting |
| `llm_formatter.py` | Format output, call LLM | Data access, calculations |
| `ecoscore_calculator.py` | Orchestrate score feature | Direct data/LLM access |
| `product_advisor.py` | Orchestrate product feature | Direct data/LLM access |
| `impact_awareness.py` | Orchestrate impact feature | Direct data/LLM access |
| `shopping_assistant.py` | Orchestrate shopping feature | Direct data/LLM access |
| `app.py` | UI, user input, display | Business logic, calculations |

## Design Patterns Applied

1. **Separation of Concerns**: Data, Logic, Formatting are isolated
2. **Dependency Injection**: Features receive layer instances
3. **Single Responsibility**: Each module has one clear purpose
4. **Constraint by Design**: LLM cannot be used outside 4 functions
5. **Structured Output**: All LLM calls enforce format in prompt

## Anti-Pattern Prevention

❌ **Avoided**: Mixed data access and formatting
✅ **Applied**: Separate layers

❌ **Avoided**: Free-form LLM with "do anything"
✅ **Applied**: Constrained to 4 functions

❌ **Avoided**: Business logic in UI
✅ **Applied**: Features handle logic

❌ **Avoided**: Unstructured text responses
✅ **Applied**: Forced formatting (tables/bullets/checklists)

❌ **Avoided**: Long conversational responses
✅ **Applied**: Token limit + prompt constraints

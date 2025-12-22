# Testing & Validation Guide

## Quick Validation Tests

### Test 1: Launch Application
```bash
streamlit run app.py
```
**Expected**: Application loads without errors, shows 4 features in sidebar

---

### Test 2: Eco Score Calculator - Single Brand

**Steps:**
1. Select "1️⃣ Eco Score Calculator"
2. Go to "Single Brand Analysis" tab
3. Select "H&M" from dropdown
4. Click "Calculate EcoScore"

**Expected Output:**
- ✅ Score displayed (e.g., 45/100)
- ✅ Verdict shown (e.g., "Poor")
- ✅ Metric cards (carbon, transparency)
- ✅ Structured explanation with table
- ✅ Bullet points listing issues
- ✅ "View Raw Data" expander available

**Validate Constraints:**
- ❌ No long conversational paragraphs
- ✅ Information in tables/bullets
- ✅ Response < 500 tokens

---

### Test 3: Eco Score Calculator - Comparison

**Steps:**
1. Go to "Brand Comparison" tab
2. Select 2-3 brands (e.g., H&M, Zara, Patagonia)
3. Click "Compare Brands"

**Expected Output:**
- ✅ Markdown table with all brands
- ✅ Columns: Brand, EcoScore, metrics
- ✅ Brief summary after table
- ❌ No long explanations

---

### Test 4: Product Sustainability Advisor

**Steps:**
1. Select "2️⃣ Product Sustainability Advisor"
2. Go to "Analyze Product" tab
3. Select:
   - Product Type: "T-shirt"
   - Brand: "H&M"
   - Materials: "Organic Cotton", "Recycled Polyester"
4. Click "Analyze Product"

**Expected Output:**
- ✅ Overall sustainability score
- ✅ Material analysis cards (green for recommended, red for avoid)
- ✅ Structured advice section
- ✅ Checklist format (- [ ] items)

---

### Test 5: Material Recommendations

**Steps:**
1. Go to "Material Guide" tab
2. Enter use case: "everyday casual wear"
3. Click "Get Material Recommendations"

**Expected Output:**
- ✅ Table with materials
- ✅ Scores and impact descriptions
- ✅ Clear categorization (recommended/avoid)
- ❌ No conversational advice

---

### Test 6: Fashion Impact Awareness

**Steps:**
1. Select "3️⃣ Fashion Impact Awareness"
2. Click "Get Fast Fashion Summary"

**Expected Output:**
- ✅ Metric cards (carbon, water, labor)
- ✅ Structured summary with table
- ✅ Bullet points with facts
- ✅ Checklist of actions

---

### Test 7: Topic Deep Dive

**Steps:**
1. Go to "Industry Topics" tab
2. Select topic: "water_usage"
3. Click "Learn About This Topic"

**Expected Output:**
- ✅ Topic definition (1 sentence)
- ✅ Statistics table
- ✅ 3-4 bullet points with facts
- ✅ 2-3 checklist items for action

---

### Test 8: Conscious Shopping Assistant

**Steps:**
1. Select "4️⃣ Conscious Shopping Assistant"
2. Set minimum EcoScore: 70
3. Click "Find Recommendations"

**Expected Output:**
- ✅ Success message with count
- ✅ Formatted table with brands
- ✅ Columns: Brand, Score, Verdict
- ❌ No general shopping advice

---

### Test 9: Find Alternatives

**Steps:**
1. Go to "Get Alternatives" tab
2. Select brand: "Zara"
3. Click "Show Better Alternatives"

**Expected Output:**
- ✅ Current brand score shown
- ✅ List of alternatives with improvement scores
- ✅ Structured recommendations
- ✅ Checklist format

---

### Test 10: Shopping Checklist

**Steps:**
1. Go to "Shopping Checklist" tab
2. Select category: "Basics"
3. Click "Generate Checklist"

**Expected Output:**
- ✅ Organized sections (Before You Buy, What to Look For, Red Flags)
- ✅ Checkbox format (- [ ] items)
- ✅ Concise 1-line items
- ❌ No long explanations

---

## LLM Constraint Validation

### Test: Out-of-Scope Request
**Not possible in UI** - all inputs are structured (dropdowns/selects)

This is by design! User cannot ask free-form questions.

---

### Test: Response Length
**How to check:**
1. Perform any LLM-calling action
2. Copy the response
3. Count approximate tokens (words × 1.3)

**Expected**: < 500 tokens per response

---

### Test: Output Format Consistency
**Repeat same action 3 times:**
1. Calculate EcoScore for "H&M" three times
2. Compare outputs

**Expected**:
- ✅ Same structure each time
- ✅ Same sections (table, bullets)
- ✅ Minor variation in wording only

---

## Error Handling Tests

### Test: Unknown Brand
**Steps:**
1. Manually type brand name not in database (if possible)

**Expected**: "Brand not found" message

---

### Test: Empty Selection
**Steps:**
1. Try to calculate without selecting brand

**Expected**: Button should be disabled or validation error

---

### Test: API Key Missing
**Steps:**
1. Remove API key from secrets.toml
2. Restart app

**Expected**: Clear error message about missing key

---

## Performance Tests

### Test: Load Time
**Measure:**
- Initial app load: < 5 seconds
- Feature switch: < 1 second
- EcoScore calculation: < 3 seconds
- LLM response: < 10 seconds

---

### Test: Concurrent Features
**Steps:**
1. Calculate EcoScore
2. Immediately switch to Product Advisor
3. Analyze product

**Expected**: No conflicts, clean state per feature

---

## Data Validation

### Test: Score Ranges
**Validate:**
- All EcoScores are 0-100
- All percentages are 0-100
- All metrics are non-negative

---

### Test: Data Consistency
**Check:**
1. Calculate score for same brand multiple times
2. Verify same score returned

**Expected**: Deterministic calculations

---

## UI/UX Tests

### Test: Sidebar Navigation
**Steps:**
1. Click each of 4 features
2. Verify content changes

**Expected**: Clear visual feedback, content updates

---

### Test: Tab Navigation
**Steps:**
1. Within each feature, click all tabs
2. Verify content switches

**Expected**: Tab highlighting, content display

---

### Test: Expandable Sections
**Steps:**
1. Click "View Raw Data" expander
2. Verify JSON display

**Expected**: Formatted JSON with all metrics

---

## Integration Tests

### Test: Data → Logic → LLM Flow
**Steps:**
1. Select brand "Patagonia"
2. Calculate EcoScore
3. Verify data flows correctly:
   - Data layer retrieves CSV data
   - Logic layer calculates score
   - LLM formats explanation
   - UI displays all components

**Expected**: Seamless flow, all parts working

---

### Test: Feature Independence
**Steps:**
1. Use Feature 1 (EcoScore)
2. Switch to Feature 4 (Shopping Assistant)
3. No state from Feature 1 should affect Feature 4

**Expected**: Clean state per feature

---

## Regression Tests (vs old main.py)

### Test: Same EcoScore Calculation
**Steps:**
1. Run `streamlit run main.py`
2. Ask about "H&M"
3. Note the EcoScore
4. Run `streamlit run app.py`
5. Calculate EcoScore for "H&M"

**Expected**: Same score (calculation logic preserved)

---

## Automated Test Script (Optional)

```python
# test_system.py
import pytest
from core.data_layer import DataLayer
from core.logic_layer import LogicLayer

def test_data_layer():
    data = DataLayer("true_cost_fast_fashion.csv")
    assert len(data.get_brand_list()) > 0
    assert data.detect_brand("I love H&M") == "H&M"

def test_logic_layer():
    data = DataLayer("true_cost_fast_fashion.csv")
    brand_data = data.get_brand_data("H&M")
    result = LogicLayer.calculate_ecoscore(brand_data, data.df)
    assert 0 <= result['ecoscore'] <= 100
    assert result['brand'] == "H&M"

def test_verdict():
    verdict, emoji = LogicLayer.get_verdict(85)
    assert verdict == "Excellent"
    assert emoji == "🌟"
```

Run with:
```bash
pytest test_system.py
```

---

## Checklist: System Validation

- [ ] App launches without errors
- [ ] All 4 features accessible
- [ ] EcoScore calculations work
- [ ] Brand comparisons display
- [ ] Product analysis functions
- [ ] Material recommendations load
- [ ] Impact awareness shows data
- [ ] Shopping assistant provides recommendations
- [ ] All LLM responses are structured (tables/bullets/checklists)
- [ ] No long paragraphs in output
- [ ] No conversational tone
- [ ] All dropdowns populated
- [ ] Buttons trigger correct actions
- [ ] Error messages are clear
- [ ] Raw data expandable
- [ ] Metric cards display correctly

---

## Common Issues & Fixes

**Issue**: API key error
**Fix**: Check `.streamlit/secrets.toml` or environment variable

**Issue**: Module not found
**Fix**: Ensure all `__init__.py` files exist in core/ and features/

**Issue**: LLM response too long
**Fix**: Verify `max_tokens=500` in `llm_formatter.py`

**Issue**: Unstructured output
**Fix**: Check `STRICT_SYSTEM_PROMPT` is being used

**Issue**: Brand not found
**Fix**: Verify brand name matches exactly in CSV

**Issue**: Slow responses
**Fix**: Check API connection, consider timeout settings

---

## Success Criteria

✅ **Functional**: All 4 features work correctly
✅ **Constrained**: LLM only formats, doesn't chat
✅ **Structured**: All output in tables/bullets/checklists
✅ **Consistent**: Same input → same structured output
✅ **Performant**: Responses within acceptable time
✅ **Error-handled**: Clear messages for failures
✅ **Maintainable**: Modular code, easy to modify

---

Test completed successfully when all checkboxes above are marked ✅

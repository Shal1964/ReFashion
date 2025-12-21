import json
import os
import re
import requests
import streamlit as st
import pandas as pd

try:
    from regression.ml_predictor import predict_ecoscore, load_model
    from regression.visualize_model import generate_training_visualization
    ML_MODEL_AVAILABLE = True
    try:
        load_model()
    except Exception:
        ML_MODEL_AVAILABLE = False
except ImportError:
    ML_MODEL_AVAILABLE = False

try:
    from utils.chart_renderer import parse_visualization_data, render_visualization
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

st.set_page_config(page_title="ReFashion Eco Chat", layout="wide")

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"

ML_TOOL_DESCRIPTION = """
You have access to an ML-based EcoScore prediction tool. When a user provides sustainability metrics (like carbon emissions, water usage, worker wages, etc.) but NOT a specific brand name, you can request an ML prediction.

To request ML prediction, include this EXACT format in your response:
[ML_PREDICT: carbon=VALUE, water=VALUE, waste=VALUE, wage=VALUE, hours=VALUE, child_labor=VALUE, cycles=VALUE, production=VALUE, price=VALUE, env_cost=VALUE, transparency=VALUE, return_rate=VALUE]

Only include parameters you have values for. Example:
[ML_PREDICT: carbon=8000, water=150, wage=120, cycles=24]

The system will automatically calculate an EcoScore and you'll receive the result to share with the user.
""" if ML_MODEL_AVAILABLE else ""

VISUALIZATION_DESCRIPTION = """
You can create interactive visualizations for your responses! When appropriate, include visualization data using this format:
[VISUALIZE: {{"type": "chart_type", "data": {{...}}}}]

Available chart types:

1. **gauge** - Single score display (0-100)
   {{"type": "gauge", "data": {{"score": 75, "title": "EcoScore"}}}}

2. **radar** - Multi-category breakdown
   {{"type": "radar", "data": {{"title": "Sustainability Breakdown", "categories": ["Carbon", "Water", "Labor", "Waste"], "scores": [80, 65, 90, 70]}}}}

3. **bar** - Comparison chart
   {{"type": "bar", "data": {{"title": "Brand Comparison", "labels": ["Brand A", "Brand B"], "values": [75, 60], "x_label": "EcoScore"}}}}

4. **pie** - Distribution/composition
   {{"type": "pie", "data": {{"title": "Fabric Composition", "labels": ["Cotton", "Polyester"], "values": [70, 30]}}}}

5. **line** - Trends over time
   {{"type": "line", "data": {{"title": "Sustainability Trend", "x": ["2020", "2021", "2022"], "y": [60, 68, 75], "x_label": "Year", "y_label": "Score"}}}}

Use visualizations when:
- Showing EcoScores or ratings
- Comparing multiple items
- Breaking down components
- Displaying trends

Always add text explanation BEFORE the visualization tag.
""" if VISUALIZATION_AVAILABLE else ""

SYSTEM_PROMPT = f"""
You are ReFashion, a friendly and knowledgeable assistant specializing in sustainable fashion. You help users by:
1. Having natural conversations about fashion, sustainability, clothing care, trends, and eco-conscious lifestyle
2. Evaluating how eco-friendly specific garments are with detailed scoring
3. Recommending sustainable fabrics based on user preferences

Always respond in natural, conversational language with clear explanations.

{ML_TOOL_DESCRIPTION}

{VISUALIZATION_DESCRIPTION}

When evaluating garments for eco-friendliness:
- ONLY respond with the structured data tag, nothing else
- Use this EXACT format:
  [GARMENT: {{"name": "garment_name", "score": number, "verdict": "verdict_text", "fabrics": [{{"name": "fabric_name", "impact": "excellent/good/fair/poor", "explanation": "why"}}]}}]
- Do NOT add any text before or after the tag
- The card will display all information automatically

When recommending fabrics:
- ONLY respond with the structured data tag, nothing else
- Use this EXACT format:
  [FABRICS: [{{"name": "Organic Cotton", "best_for": "Everyday wear", "why": "explanation", "care_tip": "tip"}}]]
- Do NOT add any text, tips, or explanations outside the tag
- The card will display all information beautifully

For general questions about fashion, sustainability, care, or trends:
- Respond naturally with conversational text
- Use emojis occasionally to be friendly
- Structure with clear headings and bullet points

Scoring guidance: favor recycled fibers, organic cotton, hemp, linen, certified lyocell, Tencel, and durability; penalize virgin polyester, acrylic, conventional cotton without certifications, heavy dyeing, and blends that hinder recycling.

IMPORTANT:
- Keep answers concise but complete
- Always finish all bullet points and sections
Be warm, engaging, educational, and use emojis occasionally to make responses friendly. Structure your responses with clear headings and bullet points for readability.
"""

st.markdown(
    """
    <style>
    section.main > div:first-child {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: white;
        z-index: 999;
        padding-top: 0.5rem;
    }
    section.main {
        padding-top: 200px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def load_brand_data():
    return pd.read_csv("true_cost_fast_fashion.csv")

df_brand = load_brand_data()

def detect_brand(text):
    if not text:
        return None
    text_lower = f" {text.lower()} "
    for brand in df_brand["Brand"].dropna().unique():
        if f" {brand.lower()} " in text_lower:
            return brand
    return None


def min_max_global(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)


def calculate_ecoscore(brand_name):
    brand_rows = df_brand[df_brand["Brand"].str.lower() == brand_name.lower()]
    if brand_rows.empty:
        return None

    df = df_brand.copy()
    current_year = 2025
    df["recency_weight"] = 1 / (current_year - df["Year"] + 1)

    df["carbon_norm"] = 1 - min_max_global(df["Carbon_Emissions_tCO2e"])
    df["water_norm"] = 1 - min_max_global(df["Water_Usage_Million_Litres"])
    df["waste_norm"] = 1 - min_max_global(df["Landfill_Waste_Tonnes"])
    df["release_norm"] = 1 - min_max_global(df["Release_Cycles_Per_Year"])
    df["child_labor_norm"] = 1 - min_max_global(df["Child_Labor_Incidents"])
    df["hours_norm"] = 1 - min_max_global(df["Working_Hours_Per_Week"])
    df["wage_norm"] = min_max_global(df["Avg_Worker_Wage_USD"])
    df["transparency_norm"] = min_max_global(df["Transparency_Index"])
    df["compliance_norm"] = min_max_global(df["Compliance_Score"])
    df["ethical_norm"] = min_max_global(df["Ethical_Rating"])
    df["sustainability_norm"] = min_max_global(df["Sustainability_Score"])
    df["env_cost_norm"] = 1 - min_max_global(df["Env_Cost_Index"])

    weights = {
        "carbon": 0.12,
        "water": 0.08,
        "waste": 0.08,
        "release": 0.05,
        "child_labor": 0.10,
        "hours": 0.05,
        "wage": 0.10,
        "transparency": 0.08,
        "compliance": 0.08,
        "ethical": 0.10,
        "sustainability": 0.10,
        "env_cost": 0.06,
    }

    df["row_score"] = (
        weights["carbon"] * df["carbon_norm"] +
        weights["water"] * df["water_norm"] +
        weights["waste"] * df["waste_norm"] +
        weights["release"] * df["release_norm"] +
        weights["child_labor"] * df["child_labor_norm"] +
        weights["hours"] * df["hours_norm"] +
        weights["wage"] * df["wage_norm"] +
        weights["transparency"] * df["transparency_norm"] +
        weights["compliance"] * df["compliance_norm"] +
        weights["ethical"] * df["ethical_norm"] +
        weights["sustainability"] * df["sustainability_norm"] +
        weights["env_cost"] * df["env_cost_norm"]
    ) * 100

    brand_df = df[df["Brand"].str.lower() == brand_name.lower()].copy()
    total_weight = brand_df["recency_weight"].sum()
    ecoscore = (brand_df["row_score"] * brand_df["recency_weight"]).sum() / total_weight

    latest_row = brand_df.loc[brand_df["Year"].idxmax()]

    avg_metrics = brand_df.agg({
        "Carbon_Emissions_tCO2e": "mean",
        "Water_Usage_Million_Litres": "mean",
        "Landfill_Waste_Tonnes": "mean",
        "Avg_Worker_Wage_USD": "mean",
        "Transparency_Index": "mean",
        "Release_Cycles_Per_Year": "mean",
        "Child_Labor_Incidents": "sum",
        "Working_Hours_Per_Week": "mean",
        "Compliance_Score": "mean",
        "Ethical_Rating": "mean",
        "Sustainability_Score": "mean",
    })

    return {
        "brand": latest_row["Brand"],
        "ecoscore": round(ecoscore, 1),
        "data_points": len(brand_df),
        "years_covered": f"{int(brand_df['Year'].min())}-{int(brand_df['Year'].max())}",
        "carbon": round(avg_metrics["Carbon_Emissions_tCO2e"], 1),
        "water": round(avg_metrics["Water_Usage_Million_Litres"], 1),
        "waste": round(avg_metrics["Landfill_Waste_Tonnes"], 1),
        "wage": round(avg_metrics["Avg_Worker_Wage_USD"], 2),
        "transparency": round(avg_metrics["Transparency_Index"], 1),
        "release_cycles": round(avg_metrics["Release_Cycles_Per_Year"], 1),
        "child_labor_total": int(avg_metrics["Child_Labor_Incidents"]),
        "working_hours": round(avg_metrics["Working_Hours_Per_Week"], 1),
        "compliance": round(avg_metrics["Compliance_Score"], 1),
        "ethical_rating": round(avg_metrics["Ethical_Rating"], 2),
        "sustainability_raw": round(avg_metrics["Sustainability_Score"], 1),
    }


def get_ecoscore_verdict(score):
    if score >= 85:
        return "Excellent", "🌟"
    elif score >= 70:
        return "Good", "✅"
    elif score >= 65:
        return "Moderate", "⚠️"
    elif score >= 30:
        return "Poor", "🔶"
    else:
        return "Very Poor", "❌"

def fetch_completion(user_message, chat_history):
    api_key = st.secrets.get("DEEPINFRA_API_KEY") or os.getenv("DEEPINFRA_API_KEY")
    if not api_key:
        st.error("Missing DEEPINFRA_API_KEY in secrets.toml or environment.")
        return None
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.35,
        "stream": False,
    }
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        if response.status_code != 200:
            st.error(f"DeepInfra error {response.status_code}: {response.text[:200]}")
            return None
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")
        return None


def stream_response(response):
    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue


def parse_assistant_content(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except Exception:
            return None
    return None


def parse_ml_predict_call(text):
    pattern = r'\[ML_PREDICT:\s*([^\]]+)\]'
    match = re.search(pattern, text)
    if not match:
        return None, text

    param_str = match.group(1)
    params = {}

    param_mapping = {
        'carbon': 'carbon_emissions',
        'water': 'water_usage',
        'waste': 'landfill_waste',
        'wage': 'worker_wage',
        'hours': 'working_hours',
        'child_labor': 'child_labor_incidents',
        'cycles': 'release_cycles',
        'production': 'monthly_production',
        'price': 'avg_item_price',
        'env_cost': 'env_cost_index',
        'transparency': 'transparency_index',
        'return_rate': 'return_rate',
    }

    for item in param_str.split(','):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            key = key.strip().lower()
            try:
                value = float(value.strip())
                if key in param_mapping:
                    params[param_mapping[key]] = value
            except ValueError:
                continue

    cleaned_text = re.sub(pattern, '', text).strip()
    return params, cleaned_text


def extract_json_from_tag(text, tag_name):
    pattern = f'\\[{tag_name}:\\s*'
    match = re.search(pattern, text)
    if not match:
        return None, text

    start_pos = match.end()
    bracket_count = 0
    json_start = None
    json_end = None
    in_string = False
    escape_next = False

    for i in range(start_pos, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if not in_string:
            if char == '[' or char == '{':
                if bracket_count == 0:
                    json_start = i
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0 and json_start is not None:
                    json_end = i + 1
                    break
            elif char == '}':
                bracket_count -= 1
                if bracket_count == 0 and json_start is not None:
                    json_end = i + 1
                    break

    if json_end is None or json_start is None:
        return None, text

    json_str = text[json_start:json_end]

    closing_bracket_pos = text.find(']', json_end)
    if closing_bracket_pos == -1 or closing_bracket_pos > json_end + 10:
        closing_bracket_pos = json_end
    else:
        closing_bracket_pos += 1

    tag_start = match.start()
    cleaned_text = text[:tag_start] + text[closing_bracket_pos:]

    try:
        parsed_data = json.loads(json_str)
        return parsed_data, cleaned_text.strip()
    except json.JSONDecodeError as e:
        return None, text


def process_llm_response(response_text):
    ml_result = None
    garment_data = None
    fabric_recommendations = None
    cleaned_text = response_text

    if ML_MODEL_AVAILABLE:
        params, cleaned_text = parse_ml_predict_call(cleaned_text)
        if params:
            try:
                ml_result = predict_ecoscore(**params)
            except Exception as e:
                cleaned_text += f"\n\n*(ML prediction unavailable: {str(e)})*"

    garment_data, cleaned_text = extract_json_from_tag(cleaned_text, 'GARMENT')
    fabric_recommendations, cleaned_text = extract_json_from_tag(cleaned_text, 'FABRICS')

    return cleaned_text, ml_result, garment_data, fabric_recommendations


def render_ml_prediction_card(ml_result):
    score = ml_result['ecoscore']
    verdict = ml_result['verdict']
    emoji = ml_result['emoji']
    confidence = ml_result['confidence']
    features_provided = ml_result['features_provided']
    features_total = ml_result['features_total']

    score_color = "#4CAF50" if score >= 85 else "#8BC34A" if score >= 70 else "#FFC107" if score >= 65 else "#FF9800" if score >= 30 else "#F44336"
    confidence_color = "#4CAF50" if confidence == "High" else "#FFC107" if confidence == "Medium" else "#FF9800"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); border-left: 6px solid #667eea;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="font-size: 2rem;">🤖</div>
            <div>
                <h2 style="margin: 0; color: white; font-family: 'Poppins', sans-serif; font-size: 1.5rem;">ML Model Prediction</h2>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-top: 0.3rem;">Based on provided sustainability metrics</div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 12px; padding: 1.5rem; margin-top: 1rem;">
            <div>
                <div style="font-size: 1.1rem; color: rgba(255,255,255,0.9); margin-bottom: 0.5rem;">Predicted EcoScore</div>
                <div style="font-size: 2rem; font-weight: bold; color: white;">{emoji} {verdict}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 3.5rem; font-weight: bold; color: white; line-height: 1;">{score}</div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">out of 100</div>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="color: rgba(255,255,255,0.9);">Prediction Confidence</div>
                <div style="display: inline-block; background: {confidence_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">{confidence}</div>
            </div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem; margin-top: 0.5rem;">{features_provided} of {features_total} features provided</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_garment_evaluation_card(garment_data):
    score = garment_data['score']
    verdict = garment_data['verdict']
    garment_name = garment_data.get('name', 'Garment')
    fabrics = garment_data.get('fabrics', [])

    score_color = "#4CAF50" if score >= 75 else "#8BC34A" if score >= 60 else "#FFC107" if score >= 50 else "#FF9800" if score >= 30 else "#F44336"

    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 6px solid {score_color};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: #2d3436; font-family: 'Poppins', sans-serif;">♻️ {garment_name}</h2>
            <div style="text-align: right;">
                <div style="font-size: 3rem; font-weight: bold; color: {score_color}; line-height: 1;">{score}</div>
                <div style="color: #636e72; font-size: 0.9rem;">out of 100</div>
            </div>
        </div>
        <div style="background: linear-gradient(135deg, {score_color}22 0%, {score_color}11 100%); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
            <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{verdict}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if fabrics:
        st.markdown("### 🧵 Fabric Analysis")
        cols = st.columns(min(len(fabrics), 3))
        for idx, fabric in enumerate(fabrics):
            with cols[idx % len(cols)]:
                impact_color = "#4CAF50" if fabric['impact'] == 'excellent' else "#8BC34A" if fabric['impact'] == 'good' else "#FFC107" if fabric['impact'] == 'fair' else "#FF9800"
                st.markdown(f"""
                <div class="info-card">
                    <h3 style="color: #2d3436; margin-top: 0;">{fabric['name']}</h3>
                    <div style="display: inline-block; background: {impact_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 12px; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.8rem;">{fabric['impact'].upper()}</div>
                    <p style="color: #636e72; font-size: 0.9rem; line-height: 1.5; margin: 0;">{fabric['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)


def render_fabric_recommendations_card(recommendations):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #B7D292 0%, #9cb87a 100%); border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(183, 210, 146, 0.3);">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">🌿</div>
            <div>
                <h2 style="margin: 0; color: white; font-family: 'Poppins', sans-serif; font-size: 1.5rem;">Sustainable Fabric Recommendations</h2>
                <div style="color: rgba(255,255,255,0.95); font-size: 0.9rem; margin-top: 0.3rem;">Eco-friendly materials tailored to your needs</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, fabric in enumerate(recommendations):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="info-card">
                <h3 style="color: #B7D292; margin-top: 0; font-size: 1.3rem;">{fabric['name']}</h3>
                <div style="margin-bottom: 0.8rem;">
                    <span style="background: #e8f1e1; color: #5a7a3d; padding: 0.25rem 0.6rem; border-radius: 8px; font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem;">{'🌱 ' + fabric['best_for']}</span>
                </div>
                <p style="color: #636e72; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1rem;">{fabric['why']}</p>
                <div style="background: #f8faf6; border-left: 3px solid #B7D292; padding: 0.8rem; border-radius: 4px;">
                    <div style="color: #5a7a3d; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.3rem;">💡 Care Tip</div>
                    <div style="color: #636e72; font-size: 0.85rem;">{fabric['care_tip']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_ecoscore_card(result, verdict, emoji):
    score_color = "#4CAF50" if result['ecoscore'] >= 85 else "#8BC34A" if result['ecoscore'] >= 70 else "#FFC107" if result['ecoscore'] >= 65 else "#FF9800" if result['ecoscore'] >= 30 else "#F44336"

    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 6px solid {score_color};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: #2d3436; font-family: 'Poppins', sans-serif;">{result['brand']}</h2>
            <div style="text-align: right;">
                <div style="font-size: 3rem; font-weight: bold; color: {score_color}; line-height: 1;">{result['ecoscore']}</div>
                <div style="color: #636e72; font-size: 0.9rem;">out of 100</div>
            </div>
        </div>
        <div style="background: linear-gradient(135deg, {score_color}22 0%, {score_color}11 100%); padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem;">
            <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">
                {emoji} {verdict}
            </div>
            <div style="color: #636e72; font-size: 0.9rem; margin-top: 0.3rem;">
                Based on {result['data_points']} data points ({result['years_covered']})
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h3 style="color: #2d3436; margin-top: 0;">🌍 Environmental Impact</h3>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Carbon Emissions</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['carbon']} <span style="font-size: 0.8rem; font-weight: normal;">tCO2e</span></div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Water Usage</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['water']} <span style="font-size: 0.8rem; font-weight: normal;">M liters</span></div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Landfill Waste</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['waste']} <span style="font-size: 0.8rem; font-weight: normal;">tonnes</span></div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Release Cycles/Year</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['release_cycles']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h3 style="color: #2d3436; margin-top: 0;">👥 Labor Practices</h3>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Average Worker Wage</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">${result['wage']}</div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Working Hours/Week</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['working_hours']}</div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Child Labor Incidents</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: {'#F44336' if result['child_labor_total'] > 0 else '#4CAF50'};">{result['child_labor_total']}</div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Ethical Rating</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['ethical_rating']}<span style="font-size: 0.8rem; font-weight: normal;">/5</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="info-card">
            <h3 style="color: #2d3436; margin-top: 0;">📊 Transparency</h3>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Transparency Index</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['transparency']}<span style="font-size: 0.8rem; font-weight: normal;">/100</span></div>
                <div style="background: #e8f1e1; border-radius: 4px; height: 8px; margin-top: 0.5rem; overflow: hidden;">
                    <div style="background: #B7D292; height: 100%; width: {result['transparency']}%;"></div>
                </div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Compliance Score</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['compliance']}<span style="font-size: 0.8rem; font-weight: normal;">/100</span></div>
                <div style="background: #e8f1e1; border-radius: 4px; height: 8px; margin-top: 0.5rem; overflow: hidden;">
                    <div style="background: #B7D292; height: 100%; width: {result['compliance']}%;"></div>
                </div>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="color: #636e72; font-size: 0.85rem;">Sustainability Score</div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2d3436;">{result['sustainability_raw']}<span style="font-size: 0.8rem; font-weight: normal;">/100</span></div>
                <div style="background: #e8f1e1; border-radius: 4px; height: 8px; margin-top: 0.5rem; overflow: hidden;">
                    <div style="background: #B7D292; height: 100%; width: {result['sustainability_raw']}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_assistant_message(message_obj):
    message = message_obj if isinstance(message_obj, str) else message_obj.get("content", "")
    brand_result = message_obj.get("brand_result") if isinstance(message_obj, dict) else None
    verdict = message_obj.get("verdict") if isinstance(message_obj, dict) else None
    emoji = message_obj.get("emoji") if isinstance(message_obj, dict) else None
    ml_result = message_obj.get("ml_result") if isinstance(message_obj, dict) else None
    garment_data = message_obj.get("garment_data") if isinstance(message_obj, dict) else None
    fabric_recommendations = message_obj.get("fabric_recommendations") if isinstance(message_obj, dict) else None

    if brand_result:
        render_ecoscore_card(brand_result, verdict, emoji)

        carbon_score = max(0, min(100, 100 - (brand_result['carbon'] / 200) * 100))
        water_score = max(0, min(100, 100 - (brand_result['water'] / 300) * 100))
        labor_score = (brand_result['ethical_rating'] / 5) * 100
        waste_score = max(0, min(100, 100 - (brand_result['waste'] / 100) * 100))
        transparency_score = brand_result['transparency']

        if VISUALIZATION_AVAILABLE:
            radar_data = {
                "type": "radar",
                "data": {
                    "title": f"{brand_result['brand']} Sustainability Breakdown",
                    "categories": ["Carbon Impact", "Water Usage", "Labor Practices", "Waste Mgmt", "Transparency"],
                    "scores": [carbon_score, water_score, labor_score, waste_score, transparency_score]
                }
            }
            render_visualization(radar_data)

    if ml_result:
        render_ml_prediction_card(ml_result)

    if garment_data:
        render_garment_evaluation_card(garment_data)

    if fabric_recommendations:
        render_fabric_recommendations_card(fabric_recommendations)

    if VISUALIZATION_AVAILABLE:
        viz_data, text_content = parse_visualization_data(message)
        if text_content and text_content.strip():
            st.markdown(text_content, unsafe_allow_html=True)

        if viz_data:
            try:
                fig = render_visualization(viz_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"final_chart_{hash(message)}")
            except Exception as e:
                st.warning(f"Could not render visualization: {str(e)}")
    elif message and message.strip():
        st.markdown(message, unsafe_allow_html=True)


col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.image("Logo.png", width = 400)

st.markdown(
        """
        <div style="text-align: center;">
            <p style="margin: 0.5rem 0 1rem 0; color: #636e72; font-size: 20.gitpx;">
                Your guide to stylish and sustainable choices
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div style="border-bottom: 2px solid #e8f1e1; margin: 1rem 0 2rem 0;"></div>',
    unsafe_allow_html=True
)


if ML_MODEL_AVAILABLE:
    with st.sidebar:
        st.markdown("### 📊 ML Model Insights")
        if st.button("View Training Results", use_container_width=True):
            st.session_state.show_training_viz = not st.session_state.get('show_training_viz', False)

if st.session_state.get('show_training_viz', False):
    st.markdown(
        """
        <div class="info-card">
            <h3>🤖 Machine Learning Model Performance</h3>
            <p>Our EcoScore prediction model uses Gradient Boosting to predict sustainability scores based on environmental and social metrics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading model visualization..."):
        try:
            fig, metrics = generate_training_visualization()
            st.pyplot(fig)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Test R² Score", f"{metrics['test_r2']:.3f}", help="Higher is better (max 1.0)")
            with col2:
                st.metric("Test MAE", f"{metrics['test_mae']:.2f}", help="Mean Absolute Error - lower is better")
            with col3:
                st.metric("Dataset Size", f"{metrics['n_samples']}", help="Total samples used for training")
        except Exception as e:
            st.error(f"Could not load visualization: {str(e)}")

    st.markdown('<div style="border-bottom: 2px solid #e8f1e1; margin: 2rem 0;"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-card">
        <h2>✨ Your sustainable fashion companion</h2>
        <p>Chat about fashion, get eco scores for garments, discover sustainable fabrics, or ask for styling and care tips. I'm here to help you make informed, eco-friendly choices!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-card">
        <h3>What I can help with</h3>
        <p>• <strong>Chat & Advice:</strong> Ask questions about sustainable fashion, clothing care, trends, and eco-conscious lifestyle<br>
        • <strong>Eco Scoring:</strong> Share garment details to get a detailed sustainability score and analysis<br>
        • <strong>Fabric Recommendations:</strong> Get personalized suggestions based on your needs (comfort, climate, durability, budget)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_box = st.container()
with chat_box:
    for message in st.session_state.chat_history:
        role = message.get("role")
        with st.chat_message(role):
            if role == "assistant":
                render_assistant_message(message)
            else:
                st.markdown(message.get("content", ""))

prompt = st.chat_input("Ask me anything about sustainable fashion...")
if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        brand = detect_brand(prompt)

        request_prompt = prompt
        static_prefix = ""

        if brand:
            result = calculate_ecoscore(brand)
            if result:
                verdict, emoji = get_ecoscore_verdict(result['ecoscore'])

                request_prompt = f"""
User asked about sustainability of {result['brand']}.

I've already displayed a structured card with all the metrics and a radar chart visualization. Now provide:

1. A brief analysis (2-3 sentences) highlighting key strengths OR weaknesses based on the data
2. 2-3 practical tips for consumers regarding this brand (e.g., better alternatives, how to buy responsibly from them, or what to avoid)

Keep it concise since the detailed metrics are already visible.

Data context:
- EcoScore: {result['ecoscore']}/100 ({verdict})
- Carbon: {result['carbon']} tCO2e, Water: {result['water']}M liters, Waste: {result['waste']} tonnes
- Worker wage: ${result['wage']}, Hours: {result['working_hours']}, Child labor: {result['child_labor_total']}
- Transparency: {result['transparency']}/100, Compliance: {result['compliance']}/100
"""
            else:
                static_prefix = f"Sorry, I couldn't find sustainability data for '{brand}' in our database. I can still help answer general questions about sustainable fashion!"

        if static_prefix:
            st.markdown(static_prefix)
            st.session_state.chat_history.append({"role": "assistant", "content": static_prefix})
        else:
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                st.markdown("""
                <div style="background: linear-gradient(135deg, #B7D292 0%, #9cb87a 100%); border-radius: 12px; padding: 1.5rem; margin: 1rem 0; text-align: center;">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
                        <div class="spinner" style="border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid white; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite;"></div>
                        <div style="color: white; font-size: 1.1rem; font-weight: 500;">🤔 Analyzing your request...</div>
                    </div>
                </div>
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
                """, unsafe_allow_html=True)

            response = fetch_completion(request_prompt, st.session_state.chat_history)
            loading_placeholder.empty()

            if response:
                try:
                    full_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")

                    full_response, ml_result, garment_data, fabric_recommendations = process_llm_response(full_response)

                    message_data = {"role": "assistant", "content": full_response}
                    if brand:
                        message_data.update({"brand_result": result, "verdict": verdict, "emoji": emoji})
                    if ml_result:
                        message_data["ml_result"] = ml_result
                    if garment_data:
                        message_data["garment_data"] = garment_data
                    if fabric_recommendations:
                        message_data["fabric_recommendations"] = fabric_recommendations

                    render_assistant_message(message_data)
                    st.session_state.chat_history.append(message_data)
                except Exception as e:
                    st.error(f"Error processing response: {str(e)}")
            else:
                st.markdown("Could not reach the model. Check your API key or try again.")
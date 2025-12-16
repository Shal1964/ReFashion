import json
import os
import re
import requests
import streamlit as st
import pandas as pd

try:
    from regression.ml_predictor import predict_ecoscore, load_model
    ML_MODEL_AVAILABLE = True
    try:
        load_model()
    except Exception:
        ML_MODEL_AVAILABLE = False
except ImportError:
    ML_MODEL_AVAILABLE = False

st.set_page_config(page_title="ReFashion Eco Chat", layout="wide")

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"

ML_TOOL_DESCRIPTION = """
You have access to an ML-based EcoScore prediction tool. When a user provides sustainability metrics (like carbon emissions, water usage, worker wages, etc.) but NOT a specific brand name, you can request an ML prediction.

To request ML prediction, include this EXACT format in your response:
[ML_PREDICT: carbon=VALUE, water=VALUE, waste=VALUE, wage=VALUE, hours=VALUE, child_labor=VALUE, cycles=VALUE, production=VALUE, price=VALUE, env_cost=VALUE, transparency=VALUE, return_rate=VALUE]

Only include parameters you have values for. Example:
[ML_PREDICT: carbon=8000, water=150, wage=120, cycles=24]

The system will automatically calculate an EcoScore and you'll receive the result to share with the user.
""" if ML_MODEL_AVAILABLE else ""

SYSTEM_PROMPT = f"""
You are ReFashion, a friendly and knowledgeable assistant specializing in sustainable fashion. You help users by:
1. Having natural conversations about fashion, sustainability, clothing care, trends, and eco-conscious lifestyle
2. Evaluating how eco-friendly specific garments are with detailed scoring
3. Recommending sustainable fabrics based on user preferences

Always respond in natural, conversational language. Never use JSON format - write in a friendly, readable way.

{ML_TOOL_DESCRIPTION}

When evaluating garments for eco-friendliness:
- Provide a clear score out of 100 (higher is better, 50 is average)
- Give a verdict headline (e.g., "Moderately Sustainable Choice" or "Highly Eco-Friendly")
- Analyze each fabric mentioned, rating impact as excellent/good/fair/poor with explanation
- Summarize the overall sustainability
- Offer 2-3 practical tips for the consumer

When recommending fabrics:
- Suggest 2-4 eco-friendly fabrics matching their needs
- Explain why each fabric suits their requirements
- Mention what each fabric is best for
- Include care tips where relevant

Scoring guidance: favor recycled fibers, organic cotton, hemp, linen, certified lyocell, Tencel, and durability; penalize virgin polyester, acrylic, conventional cotton without certifications, heavy dyeing, and blends that hinder recycling.

IMPORTANT:
- Keep answers concise but complete
- Always finish all bullet points and sections
Be warm, engaging, educational, and use emojis occasionally to make responses friendly. Structure your responses with clear headings and bullet points for readability.
"""


def themed_container():
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <style>
        :root {
            --primary: #B7D292;
            --primary-dark: #9cb87a;
            --background: #fafcf8;
            --card-bg: #ffffff;
            --text: #2d3436;
            --text-light: #636e72;
            --border: #e8f1e1;
            --shadow: rgba(183, 210, 146, 0.15);
        }
        body { background: var(--background); }
        .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1200px; }
        h1, h2, h3 { font-family: 'Poppins', sans-serif; color: var(--text); font-weight: 600; }
        p, li, label, span, div { font-family: 'Inter', sans-serif; color: var(--text); }
        .header-container { display: flex; align-items: center; gap: 1rem; padding: 1rem 0 2rem 0; border-bottom: 2px solid var(--border); margin-bottom: 2rem; }
        .logo-img { width: 120px; height: auto; }
        .header-text { flex: 1; }
        .header-text h1 { margin: 0; font-size: 2rem; color: var(--text); }
        .header-text p { margin: 0.5rem 0 0 0; color: var(--text-light); font-size: 1rem; }
        .hero-card { background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; padding: 1.5rem 2rem; border-radius: 16px; box-shadow: 0 8px 24px var(--shadow); margin-bottom: 2rem; }
        .hero-card h2 { color: white; margin: 0 0 0.5rem 0; font-size: 1.5rem; }
        .hero-card p { color: rgba(255,255,255,0.95); margin: 0; line-height: 1.6; }
        .info-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .info-card h3 { font-size: 1.1rem; margin-top: 0; color: var(--primary-dark); }
        .score-badge { display: inline-block; background: var(--primary); color: white; padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; font-size: 0.95rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

#eco-score
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
        "max_tokens": 512,
    }
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            st.error(f"DeepInfra error {response.status_code}: {response.text[:200]}")
            return None
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")
        return None


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
    """Extract ML prediction parameters from LLM response."""
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


def process_llm_response(response_text):
    """Process LLM response, handle ML calls if present."""
    if not ML_MODEL_AVAILABLE:
        return response_text

    params, cleaned_text = parse_ml_predict_call(response_text)

    if params:
        try:
            ml_result = predict_ecoscore(**params)

            ml_summary = f"""

**🤖 ML Model Prediction**

Based on the metrics provided, our machine learning model predicts:

- **EcoScore: {ml_result['ecoscore']}/100** {ml_result['emoji']} ({ml_result['verdict']})
- Confidence: {ml_result['confidence']} ({ml_result['features_provided']}/{ml_result['features_total']} features provided)

"""
            return cleaned_text + ml_summary
        except Exception as e:
            return cleaned_text + f"\n\n*(ML prediction unavailable: {str(e)})*"

    return response_text


def render_assistant_message(message):
    st.markdown(message, unsafe_allow_html=True)
themed_container()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("Logo.png", use_container_width=True)
    st.markdown(
        """
        <div style="text-align: center;">
            <p style="margin: 0.5rem 0 1rem 0; color: #636e72; font-size: 1rem;">Your guide to stylish and sustainable choices</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div style="border-bottom: 2px solid #e8f1e1; margin: 1rem 0 2rem 0;"></div>', unsafe_allow_html=True)

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
        content = message.get("content", "")
        with st.chat_message(role):
            if role == "assistant":
                render_assistant_message(content)
            else:
                st.markdown(content)

prompt = st.chat_input("Ask me anything about sustainable fashion...")
if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            brand = detect_brand(prompt)

        if brand:
            result = calculate_ecoscore(brand)

            if result:
                verdict, emoji = get_ecoscore_verdict(result['ecoscore'])
                enriched_prompt = f"""
User asked about sustainability of {result['brand']}.

Here is the factual sustainability data based on {result['data_points']} data points from {result['years_covered']} (DO NOT CHANGE THESE NUMBERS - use them exactly):

**EcoScore: {result['ecoscore']}/100** ({verdict} {emoji})

Environmental Impact (averages):
- Carbon emissions: {result['carbon']} tCO2e
- Water usage: {result['water']} million liters
- Landfill waste: {result['waste']} tonnes
- Environmental cost index contribution: included in score
- Release cycles per year: {result['release_cycles']} (higher = more fast fashion)

Social & Labor Practices:
- Average worker wage: ${result['wage']}
- Working hours per week: {result['working_hours']}
- Child labor incidents (total reported): {result['child_labor_total']}
- Ethical rating: {result['ethical_rating']}/5

Transparency & Compliance:
- Transparency index: {result['transparency']}/100
- Compliance score: {result['compliance']}/100
- Raw sustainability score from audits: {result['sustainability_raw']}/100

Explain this EcoScore clearly using the verdict "{verdict}". Analyze key strengths and weaknesses based on the data above. Highlight any concerning metrics (like child labor or low wages). Provide 2-3 practical tips for consumers who want to buy from this brand more responsibly or find better alternatives.
"""
                reply = fetch_completion(enriched_prompt, st.session_state.chat_history)
            else:
                reply = f"Sorry, I couldn't find sustainability data for '{brand}' in our database. I can still help answer general questions about sustainable fashion!"
        else:
            reply = fetch_completion(prompt, st.session_state.chat_history)

        if reply:
            reply = process_llm_response(reply)
            render_assistant_message(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
        else:
            st.markdown("Could not reach the model. Check your API key or try again.")

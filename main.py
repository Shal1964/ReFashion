import json
import os
import requests
import streamlit as st

st.set_page_config(page_title="ReFashion Eco Chat", layout="wide")

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"
SYSTEM_PROMPT = """
You are ReFashion, a friendly and knowledgeable assistant specializing in sustainable fashion. You can:
1. Have natural conversations about fashion, sustainability, clothing care, trends, shopping tips, and eco-conscious lifestyle
2. Evaluate how eco-friendly specific garments are
3. Recommend sustainable fabrics based on user preferences

Response Format:
- For GENERAL QUESTIONS, CONVERSATIONS, or ADVICE: Respond naturally in plain text without JSON. Be conversational, helpful, and informative.
- For ECO SCORING REQUESTS (when user asks to rate/score a specific garment or asks "how eco-friendly is X"): Respond with JSON:
{
  "eco_score": integer 0-100 where higher is better and 50 is average,
  "verdict": short headline verdict,
  "fabrics": list of {"name": str, "impact": one of ["excellent","good","fair","poor"], "notes": str},
  "summary": one-sentence summary,
  "tips": array of up to 3 concise improvement tips for consumers
}
- For FABRIC RECOMMENDATION REQUESTS: Respond with JSON including optional "recommendations" field:
{
  "recommendations": array of {"fabric": str, "reason": str, "best_for": str},
  "summary": overview of recommendations,
  "tips": array of practical advice
}

Scoring guidance: favor recycled fibers, organic cotton, hemp, linen, certified lyocell, Tencel, and durability; penalize virgin polyester, acrylic, conventional cotton without certifications, heavy dyeing, and blends that hinder recycling.

Be warm, engaging, and educational. Help users make better fashion choices while building a sustainable wardrobe.
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


def render_assistant_message(message):
    parsed = parse_assistant_content(message)

    if not parsed:
        st.markdown(message)
        return

    has_score = "eco_score" in parsed
    has_recommendations = "recommendations" in parsed

    score = parsed.get("eco_score")
    verdict = parsed.get("verdict", "")
    summary = parsed.get("summary", "")
    tips = parsed.get("tips", [])
    fabrics = parsed.get("fabrics", [])
    recommendations = parsed.get("recommendations", [])

    if has_score or has_recommendations or fabrics:
        if verdict:
            st.markdown(f"### {verdict}")

        if isinstance(score, (int, float)):
            score_color = "#88c988" if score >= 70 else "#e3c85a" if score >= 40 else "#c45252"
            st.markdown(
                f'<div style="background: #f0f0f0; border-radius: 20px; height: 12px; overflow: hidden; margin: 1rem 0;">'
                f'<div style="background: {score_color}; width: {min(max(score, 0), 100)}%; height: 100%;"></div></div>'
                f'<p style="text-align: center; font-weight: 600; color: {score_color}; font-size: 1.1rem;">Eco Score: {score}/100</p>',
                unsafe_allow_html=True
            )

        if summary:
            st.info(summary)

        if fabrics:
            st.markdown("#### 📋 Fabric Analysis")
            for fabric in fabrics:
                name = fabric.get("name", "Fabric")
                impact = fabric.get("impact", "")
                notes = fabric.get("notes", "")
                impact_emoji = {"excellent": "🌟", "good": "✅", "fair": "⚠️", "poor": "❌"}.get(impact.lower(), "")
                st.markdown(f"**{impact_emoji} {name}** — _{impact}_")
                st.markdown(f"> {notes}")

        if recommendations:
            st.markdown("#### 🌿 Recommended Fabrics")
            for rec in recommendations:
                fabric_name = rec.get("fabric", "")
                reason = rec.get("reason", "")
                best_for = rec.get("best_for", "")
                st.markdown(f"**{fabric_name}**")
                if reason:
                    st.markdown(f"_{reason}_")
                if best_for:
                    st.markdown(f"Best for: {best_for}")
                st.markdown("---")

        if tips:
            st.markdown("#### 💡 Tips for You")
            for tip in tips:
                st.markdown(f"- {tip}")
    else:
        if summary:
            st.markdown(summary)
        else:
            st.markdown(message)
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
            reply = fetch_completion(prompt, st.session_state.chat_history)
        if reply:
            render_assistant_message(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
        else:
            st.markdown("Could not reach the model. Check your API key or try again.")

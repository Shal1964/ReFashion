import os
import streamlit as st
from core.data_layer import DataLayer
from core.llm_formatter import LLMFormatter
from features.ecoscore_calculator import EcoScoreCalculator
from features.product_advisor import ProductSustainabilityAdvisor
from features.impact_awareness import FashionImpactAwareness
from features.shopping_assistant import ConsciousShoppingAssistant
from features.qa_chat import QuestionAnswerChat

st.set_page_config(
    page_title="ReFashion - Sustainable Fashion System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.feature-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-left: 4px solid #4caf50;
    margin-bottom: 1rem;
}
.metric-card {
    background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
    padding: 1rem;
    border-radius: 8px;
    color: white;
    text-align: center;
}
.info-box {
    background: #f1f8f4;
    padding: 1rem;
    border-radius: 8px;
    border-left: 3px solid #4caf50;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_system():
    data_layer = DataLayer("true_cost_fast_fashion.csv")

    api_key = st.secrets.get("DEEPINFRA_API_KEY") or os.getenv("DEEPINFRA_API_KEY")
    if not api_key:
        st.error("Missing DEEPINFRA_API_KEY in secrets.toml or environment.")
        st.stop()

    llm_formatter = LLMFormatter(
        api_key=api_key,
        api_url="https://api.deepinfra.com/v1/openai/chat/completions",
        model_name="deepseek-ai/DeepSeek-V3.2"
    )

    ecoscore_calc = EcoScoreCalculator(data_layer, llm_formatter)
    product_advisor = ProductSustainabilityAdvisor(data_layer, llm_formatter)
    impact_awareness = FashionImpactAwareness(data_layer, llm_formatter)
    shopping_assistant = ConsciousShoppingAssistant(data_layer, llm_formatter)
    qa_chat = QuestionAnswerChat(llm_formatter)

    return data_layer, ecoscore_calc, product_advisor, impact_awareness, shopping_assistant, qa_chat

data_layer, ecoscore_calc, product_advisor, impact_awareness, shopping_assistant, qa_chat = initialize_system()

# Display logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("Logo.png", use_container_width=True)

st.markdown("""
<div class="main-header">
    <h1>🌿 ReFashion - Sustainable Fashion System</h1>
    <p>Data-driven sustainability insights with structured AI assistance</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 System Features")
    feature = st.radio(
        "Select Feature:",
        [
            "1️⃣ Eco Score Calculator",
            "2️⃣ Product Sustainability Advisor",
            "3️⃣ Fashion Impact Awareness",
            "4️⃣ Conscious Shopping Assistant",
            "💬 More Questions? Ask Our Chatbot"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        <h4>🤖 AI Assistant Scope</h4>
        <p style="font-size: 0.85rem; margin: 0;">
        • EcoScore explanations<br>
        • Fast fashion summaries<br>
        • Structured recommendations<br>
        • Formatted output only
        </p>
    </div>
    """, unsafe_allow_html=True)

if "1️⃣" in feature:
    st.markdown("## 1️⃣ Eco Score Calculator")
    st.markdown("Calculate and explain sustainability scores for fashion brands.")

    tab1, tab2 = st.tabs(["Single Brand Analysis", "Brand Comparison"])

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            brand_input = st.selectbox(
                "Select Brand:",
                [""] + data_layer.get_brand_list(),
                key="ecoscore_brand"
            )
        with col2:
            calculate_btn = st.button("Calculate EcoScore", type="primary", use_container_width=True)

        if calculate_btn and brand_input:
            with st.spinner("Calculating EcoScore..."):
                result = ecoscore_calc.get_explanation(brand_input)

                if result["success"]:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{result['emoji']}</h3>
                            <h2>{result['score']}/100</h2>
                            <p>{result['verdict']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%);">
                            <h4>Carbon Emissions</h4>
                            <h3>{result['raw_data']['carbon']} tCO2e</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%);">
                            <h4>Transparency</h4>
                            <h3>{result['raw_data']['transparency']}/100</h3>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("### 📊 Detailed Analysis")
                    st.markdown(result['explanation'])

                    with st.expander("View Raw Data"):
                        st.json(result['raw_data'])
                else:
                    st.error(result['message'])

    with tab2:
        st.markdown("Compare sustainability scores across multiple brands")
        brands_to_compare = st.multiselect(
            "Select 2-5 brands to compare:",
            data_layer.get_brand_list(),
            key="compare_brands"
        )

        if st.button("Compare Brands", type="primary") and len(brands_to_compare) >= 2:
            with st.spinner("Comparing brands..."):
                result = ecoscore_calc.compare_brands(brands_to_compare)

                if result["success"]:
                    st.markdown("### Comparison Results")
                    st.markdown(result['formatted_comparison'])
                else:
                    st.error(result['message'])

elif "2️⃣" in feature:
    st.markdown("## 2️⃣ Product Sustainability Advisor")
    st.markdown("Get structured advice on sustainable product choices.")

    tab1, tab2, tab3 = st.tabs(["Analyze Product", "Material Guide", "🤖 ML Prediction"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            product_type = st.selectbox(
                "Product Type:",
                ["T-shirt", "Jeans", "Jacket", "Dress", "Shoes", "Sweater"],
                key="product_type"
            )
            brand = st.selectbox(
                "Brand (optional):",
                [""] + data_layer.get_brand_list(),
                key="product_brand"
            )

        with col2:
            materials = st.multiselect(
                "Materials:",
                ["Organic Cotton", "Recycled Polyester", "Hemp", "Linen",
                 "Tencel", "Recycled Cotton", "Virgin Polyester",
                 "Conventional Cotton", "Acrylic", "Nylon"],
                key="product_materials"
            )

        if st.button("Analyze Product", type="primary"):
            with st.spinner("Analyzing product..."):
                result = product_advisor.analyze_product(
                    product_type,
                    brand if brand else None,
                    materials if materials else None
                )

                if result["success"]:
                    if result['overall_score']:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>Overall Sustainability Score</h3>
                            <h2>{result['overall_score']}/100</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("### 📋 Structured Advice")
                    st.markdown(result['structured_advice'])

                    if result['material_analysis']:
                        st.markdown("### 🧵 Material Analysis")
                        for mat in result['material_analysis']:
                            color = "#4CAF50" if mat['verdict'] == "recommended" else "#F44336"
                            st.markdown(f"""
                            <div class="feature-card" style="border-left-color: {color};">
                                <h4>{mat['name']} - {mat['score']}/100</h4>
                                <p><strong>{mat['verdict'].upper()}</strong></p>
                                <p>{mat['impact']}</p>
                            </div>
                            """, unsafe_allow_html=True)

    with tab2:
        use_case = st.text_input("What will you use it for?", placeholder="e.g., everyday wear, workout, formal events")

        if st.button("Get Material Recommendations", type="primary") and use_case:
            with st.spinner("Generating recommendations..."):
                result = product_advisor.get_material_recommendations(use_case)

                if result["success"]:
                    st.markdown("### Material Guide")
                    st.markdown(result['formatted_guide'])

    with tab3:
        st.markdown("### 🤖 Machine Learning EcoScore Prediction")
        st.info("Don't have brand data? Provide custom metrics and our ML model will predict the EcoScore!")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Environmental Metrics**")
            carbon = st.number_input("Carbon Emissions (tCO2e)", min_value=0.0, value=None, step=100.0)
            water = st.number_input("Water Usage (Million Liters)", min_value=0.0, value=None, step=10.0)
            waste = st.number_input("Landfill Waste (Tonnes)", min_value=0.0, value=None, step=10.0)
            env_cost = st.slider("Environmental Cost Index", 0.0, 1.0, None, 0.1)
            release_cycles = st.number_input("Release Cycles per Year", min_value=1, max_value=52, value=None, step=1)

        with col2:
            st.markdown("**Labor & Business Metrics**")
            wage = st.number_input("Avg Worker Wage (USD)", min_value=0.0, value=None, step=10.0)
            hours = st.number_input("Working Hours per Week", min_value=1.0, max_value=168.0, value=None, step=1.0)
            child_labor = st.number_input("Child Labor Incidents", min_value=0, value=None, step=1)
            transparency = st.slider("Transparency Index", 0, 100, None, 5)
            price = st.number_input("Avg Item Price (USD)", min_value=0.0, value=None, step=5.0)

        if st.button("🔮 Predict EcoScore with ML", type="primary"):
            metrics = {}
            if carbon is not None: metrics['carbon_emissions'] = carbon
            if water is not None: metrics['water_usage'] = water
            if waste is not None: metrics['landfill_waste'] = waste
            if env_cost is not None: metrics['env_cost_index'] = env_cost
            if release_cycles is not None: metrics['release_cycles'] = release_cycles
            if wage is not None: metrics['worker_wage'] = wage
            if hours is not None: metrics['working_hours'] = hours
            if child_labor is not None: metrics['child_labor_incidents'] = child_labor
            if transparency is not None: metrics['transparency_index'] = transparency
            if price is not None: metrics['avg_item_price'] = price

            if not metrics:
                st.warning("Please provide at least one metric for prediction.")
            else:
                with st.spinner("Running ML prediction..."):
                    result = product_advisor.predict_custom_product(**metrics)

                    if result["success"]:
                        ml_result = result['ml_prediction']

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>{ml_result['emoji']}</h3>
                                <h2>{ml_result['ecoscore']}/100</h2>
                                <p>{ml_result['verdict']}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            confidence_color = "#4CAF50" if ml_result['confidence'] == "high" else "#FFC107" if ml_result['confidence'] == "medium" else "#FF9800"
                            st.markdown(f"""
                            <div class="metric-card" style="background: {confidence_color};">
                                <h4>Confidence</h4>
                                <h3>{ml_result['confidence'].upper()}</h3>
                            </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%);">
                                <h4>Metrics Used</h4>
                                <h3>{result['metrics_provided']}/{result['total_metrics']}</h3>
                            </div>
                            """, unsafe_allow_html=True)

                        st.success("✨ **ML Model Analysis**")
                        st.markdown(f"""
                        The machine learning model analyzed your inputs and predicted an EcoScore of **{ml_result['ecoscore']}/100**.

                        - **Verdict**: {ml_result['emoji']} {ml_result['verdict']}
                        - **Prediction Confidence**: {ml_result['confidence'].upper()} ({result['metrics_provided']} out of {result['total_metrics']} metrics provided)
                        - **Recommendation**: {"This score is based on limited data. Provide more metrics for better accuracy." if ml_result['confidence'] == "low" else "Good data coverage for reliable prediction." if ml_result['confidence'] == "high" else "Moderate data coverage. Consider adding more metrics."}
                        """)
                    else:
                        st.error(result['message'])

elif "3️⃣" in feature:
    st.markdown("## 3️⃣ Fashion Impact Awareness")
    st.markdown("Learn about fashion industry impacts through structured data.")

    tab1, tab2 = st.tabs(["Fast Fashion Impact", "Industry Topics"])

    with tab1:
        if st.button("Get Fast Fashion Summary", type="primary", use_container_width=True):
            with st.spinner("Analyzing fast fashion impacts..."):
                result = impact_awareness.get_fast_fashion_summary()

                if result["success"]:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Carbon (tCO2e)", f"{result['data']['total_carbon']:,.0f}")
                    with col2:
                        st.metric("Total Water (M liters)", f"{result['data']['total_water']:,.0f}")
                    with col3:
                        st.metric("Child Labor Incidents", f"{result['data']['total_child_labor_incidents']}")

                    st.markdown("### 📊 Impact Summary")
                    st.markdown(result['structured_summary'])

    with tab2:
        topics_result = impact_awareness.get_available_topics()

        topic_names = [t['id'] for t in topics_result['topics']]
        topic_descriptions = {t['id']: t['description'] for t in topics_result['topics']}

        selected_topic = st.selectbox(
            "Select Topic:",
            topic_names,
            format_func=lambda x: f"{x.replace('_', ' ').title()} - {topic_descriptions[x]}"
        )

        if st.button("Learn About This Topic", type="primary"):
            with st.spinner("Loading topic information..."):
                result = impact_awareness.get_topic_info(selected_topic)

                if result["success"]:
                    st.markdown(f"### {result['topic'].replace('_', ' ').title()}")
                    st.markdown(result['structured_info'])

elif "4️⃣" in feature:
    st.markdown("## 4️⃣ Conscious Shopping Assistant")
    st.markdown("Make informed shopping decisions with structured recommendations.")

    tab1, tab2, tab3 = st.tabs(["Find Sustainable Brands", "Get Alternatives", "Shopping Checklist"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            min_score = st.slider("Minimum EcoScore:", 0, 100, 70, 5)
        with col2:
            max_results = st.slider("Max results:", 3, 20, 10)

        if st.button("Find Recommendations", type="primary", use_container_width=True):
            with st.spinner("Finding sustainable brands..."):
                result = shopping_assistant.get_brand_recommendations(min_score, max_results)

                if result["success"]:
                    st.success(f"Found {result['count']} brands matching criteria")
                    st.markdown("### Recommended Brands")
                    st.markdown(result['formatted_table'])

    with tab2:
        current_brand = st.selectbox(
            "I'm considering buying from:",
            data_layer.get_brand_list(),
            key="alternative_brand"
        )

        if st.button("Show Better Alternatives", type="primary"):
            with st.spinner("Finding alternatives..."):
                result = shopping_assistant.get_alternatives_for_brand(current_brand)

                if result["success"]:
                    st.markdown(f"**Current Brand:** {result['current_brand']} (Score: {result['current_score']}/100)")
                    st.markdown("### Better Alternatives")

                    for alt in result['alternatives']:
                        st.markdown(f"""
                        <div class="feature-card">
                            <h4>{alt['brand']} - {alt['ecoscore']}/100</h4>
                            <p><strong>+{alt['improvement']} points improvement</strong> ({alt['verdict']})</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("### Recommendations")
                    st.markdown(result['structured_recommendations'])
                else:
                    st.error(result['message'])

    with tab3:
        category = st.selectbox(
            "Shopping for:",
            ["Basics", "Workwear", "Activewear", "Formal", "Casual"],
            key="checklist_category"
        )

        if st.button("Generate Checklist", type="primary"):
            with st.spinner("Creating checklist..."):
                result = shopping_assistant.get_shopping_checklist(category)

                if result["success"]:
                    st.markdown(f"### {result['category']} Shopping Checklist")
                    st.markdown(result['checklist'])

elif "💬" in feature:
    st.markdown("## 💬 More Questions? Ask Our Chatbot")
    st.markdown("Still confused about sustainable fashion? Ask me anything and I'll help explain!")

    # Initialize chat history in session state
    if "qa_messages" not in st.session_state:
        st.session_state.qa_messages = []

    # Suggested questions
    with st.expander("💡 Suggested Questions", expanded=False):
        suggested = qa_chat.get_suggested_questions()
        cols = st.columns(2)
        for idx, question in enumerate(suggested):
            with cols[idx % 2]:
                if st.button(question, key=f"suggest_{idx}", use_container_width=True):
                    st.session_state.qa_messages.append({"role": "user", "content": question})
                    with st.spinner("Thinking..."):
                        result = qa_chat.ask_question(question, include_history=True)
                        if result["success"]:
                            st.session_state.qa_messages.append({"role": "assistant", "content": result["answer"]})
                    st.rerun()

    # Display chat history
    for message in st.session_state.qa_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about sustainable fashion..."):
        st.session_state.qa_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = qa_chat.ask_question(prompt, include_history=True)

                if result["success"]:
                    st.markdown(result["answer"])
                    st.session_state.qa_messages.append({"role": "assistant", "content": result["answer"]})
                else:
                    error_msg = result.get("message", "Sorry, I couldn't process that. Please try again.")
                    st.error(error_msg)

    # Clear chat button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.qa_messages = []
            qa_chat.clear_history()
            st.rerun()

st.markdown("---")
st.markdown("""
<div class="info-box">
    <p style="margin: 0; text-align: center; color: #666;">
        🌍 ReFashion System - Structured sustainability insights powered by data and constrained AI
    </p>
</div>
""", unsafe_allow_html=True)

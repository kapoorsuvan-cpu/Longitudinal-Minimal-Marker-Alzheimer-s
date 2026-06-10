
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Alzheimer's Minimal Marker Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

CHART_COLORS = {
    "primary": "#60A5FA",
    "secondary": "#A78BFA",
    "green": "#34D399",
    "orange": "#FBBF24",
    "red": "#F87171",
    "muted": "#94A3B8",
    "border": "#374151",
    "bg": "#0B0F19",
    "card": "#111827",
    "text": "#F9FAFB",
}

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0B0F19;
    color: #F9FAFB;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #374151;
}

.hero {
    padding: 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(96,165,250,0.16), rgba(167,139,250,0.16));
    border: 1px solid #374151;
    margin-bottom: 2rem;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 900;
    color: #F9FAFB;
    line-height: 1.05;
    letter-spacing: -2.5px;
    max-width: 1500px;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: #D1D5DB;
    margin-top: 1rem;
    line-height: 1.75;
    max-width: 1100px;
}

.metric-card {
    background: rgba(17,24,39,0.85);
    border: 1px solid #374151;
    border-radius: 20px;
    padding: 1.25rem;
    transition: 0.3s;
    backdrop-filter: blur(12px);
    text-align: center;
    min-height: 125px;
}

.metric-card:hover {
    transform: translateY(-5px);
    border: 1px solid #60A5FA;
    box-shadow: 0px 0px 20px rgba(96,165,250,0.25);
}

.metric-title {
    color: #9CA3AF;
    font-size: 0.9rem;
    line-height: 1.4;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #60A5FA;
    margin-top: 0.5rem;
}

.glass-card {
    background: rgba(17,24,39,0.8);
    border: 1px solid #374151;
    border-radius: 22px;
    padding: 1.5rem;
    height: 100%;
    transition: 0.3s;
    backdrop-filter: blur(12px);
}

.glass-card:hover {
    transform: scale(1.015);
    border: 1px solid #A78BFA;
    box-shadow: 0px 0px 18px rgba(167,139,250,0.22);
}

.card-icon {
    font-size: 2rem;
}

.card-title {
    font-size: 1.15rem;
    font-weight: 750;
    margin-top: 0.8rem;
    color: white;
}

.card-text {
    color: #D1D5DB;
    margin-top: 0.7rem;
    line-height: 1.6;
}

.section-header {
    font-size: 2rem;
    font-weight: 850;
    margin-top: 2rem;
    margin-bottom: 0.5rem;
    color: white;
}

.section-sub {
    color: #9CA3AF;
    margin-bottom: 1.6rem;
    line-height: 1.65;
}

.callout {
    background: rgba(96,165,250,0.10);
    border: 1px solid rgba(96,165,250,0.35);
    border-radius: 18px;
    padding: 1.25rem;
    color: #DBEAFE;
    line-height: 1.65;
}

.warning-callout {
    background: rgba(251,191,36,0.10);
    border: 1px solid rgba(251,191,36,0.35);
    border-radius: 18px;
    padding: 1.25rem;
    color: #FEF3C7;
    line-height: 1.65;
}

hr {
    border: none;
    border-top: 1px solid #374151;
    margin-top: 2rem;
    margin-bottom: 2rem;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #374151;
    border-radius: 16px;
    overflow: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

def section_header(title, subtitle=""):
    st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)

def metric_card(title, value):
    st.markdown(
        f"""
    <div class='metric-card'>
        <div class='metric-title'>{title}</div>
        <div class='metric-value'>{value}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

def glass_card(icon, title, text):
    st.markdown(
        f"""
    <div class='glass-card'>
        <div class='card-icon'>{icon}</div>
        <div class='card-title'>{title}</div>
        <div class='card-text'>{text}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

def plotly_layout(fig, title=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CHART_COLORS["bg"],
        plot_bgcolor=CHART_COLORS["bg"],
        font=dict(color=CHART_COLORS["text"], family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        title=dict(text=title if title else None, font=dict(size=24)),
        margin=dict(l=30, r=30, t=70, b=40),
    )
    return fig

# ============================================================
# EMBEDDED SUMMARY RESULTS FROM NOTEBOOK
# ============================================================

@st.cache_data
def load_results():
    baseline = pd.DataFrame({
        "Feature Set": [
            "Clinical + genetic",
            "Clinical only",
            "Full multimodal",
            "Clinical + MRI",
            "MRI only",
        ],
        "Model": ["Logistic L1"] * 5,
        "ROC-AUC": [0.801236, 0.791777, 0.753800, 0.744330, 0.637567],
        "PR-AUC": [0.569382, 0.568445, 0.534846, 0.532702, 0.397891],
        "Balanced Accuracy": [0.742287, 0.724454, 0.691006, 0.686559, 0.593786],
        "Sensitivity": [0.716328, 0.685849, 0.590348, 0.590493, 0.364586],
        "Specificity": [0.768245, 0.763059, 0.791665, 0.782625, 0.822986],
    })

    full_models = pd.DataFrame({
        "Feature Set": [
            "Clinical + genetic",
            "Clinical + MRI",
            "Clinical + genetic + MRI",
            "Clinical only",
            "MRI only",
            "Genetic only",
        ],
        "Best Model": [
            "Random Forest",
            "Random Forest",
            "Random Forest",
            "Random Forest",
            "Random Forest",
            "Random Forest",
        ],
        "ROC-AUC": [0.820148, 0.816034, 0.815191, 0.814675, 0.674090, 0.631065],
    })

    minimal = pd.DataFrame({
        "Panel": [
            "Best 1-marker clinical",
            "Best 2-marker clinical",
            "Best 3-marker clinical",
            "Best 5-marker clinical/APOE",
            "Best 2-marker multimodal",
            "Best 3-marker multimodal",
            "Best 5-marker multimodal",
            "MRI-only 5-marker",
        ],
        "Feature Group": [
            "Clinical/APOE",
            "Clinical/APOE",
            "Clinical/APOE",
            "Clinical/APOE",
            "Clinical/APOE/MRI",
            "Clinical/APOE/MRI",
            "Clinical/APOE/MRI",
            "MRI only",
        ],
        "Number of Features": [1, 2, 3, 5, 2, 3, 5, 5],
        "Features": [
            "NEUROBAT__LDELTOTAL",
            "NEUROBAT__LDELTOTAL | UWNPSYCHSUM__ADNI_MEM",
            "NEUROBAT__LDELTOTAL | UWNPSYCHSUM__ADNI_MEM | GDSCALE__GDHOME",
            "NEUROBAT__LDELTOTAL | UWNPSYCHSUM__ADNI_MEM | GDSCALE__GDHOME | UWNPSYCHSUM__ADNI_EF2 | APOERES__GENOTYPE",
            "NEUROBAT__LDELTOTAL | UCSFFSX7__ST99TA",
            "NEUROBAT__LDELTOTAL | UCSFFSX7__ST99TA | UWNPSYCHSUM__ADNI_MEM",
            "NEUROBAT__LDELTOTAL | UCSFFSX7__ST99TA | UWNPSYCHSUM__ADNI_MEM | UCSFFSX7__ST88SV | UCSFFSX7__ST13TA",
            "UCSFFSX7__ST99TA | UCSFFSX7__ST29SV | UCSFFSX7__ST89SV | UCSFFSX7__ST31TA | UCSFFSX7__ST111TA",
        ],
        "ROC-AUC": [0.756262, 0.792197, 0.800189, 0.815647, 0.799252, 0.814900, 0.819361, 0.744321],
        "PR-AUC": [0.501717, 0.579156, 0.592933, 0.627894, 0.602354, 0.628473, 0.627292, 0.542907],
        "Sensitivity": [0.716546, 0.762627, 0.762627, 0.743324, 0.743687, 0.743759, 0.732221, 0.525544],
        "Specificity": [0.678482, 0.731805, 0.716187, 0.740871, 0.748773, 0.776097, 0.772193, 0.785298],
        "Burden Score": [1.0, 2.0, 3.0, 4.5, 6.0, 7.0, 17.0, 25.0],
    })

    ablation = pd.DataFrame({
        "Removed Feature": [
            "None, full panel",
            "NEUROBAT__LDELTOTAL",
            "UCSFFSX7__ST99TA",
            "UWNPSYCHSUM__ADNI_MEM",
            "UCSFFSX7__ST88SV",
            "UCSFFSX7__ST13TA",
        ],
        "ROC-AUC": [0.819361, 0.783858, 0.810016, 0.802175, 0.818154, 0.818300],
        "AUC Drop": [0.000000, 0.035504, 0.009346, 0.017186, 0.001208, 0.001061],
    })

    stability = pd.DataFrame({
        "Feature": [
            "NEUROBAT__LDELTOTAL",
            "UCSFFSX7__ST99TA",
            "UWNPSYCHSUM__ADNI_MEM",
            "UCSFFSX7__ST29SV",
            "UCSFFSX7__ST31TA",
            "UCSFFSX7__ST40TA",
            "UCSFFSX7__ST90TA",
            "UWNPSYCHSUM__ADNI_EF",
            "UCSFFSX7__ST52TA",
            "APOERES__GENOTYPE",
        ],
        "Selection Count": [24, 11, 10, 8, 5, 5, 5, 4, 4, 4],
    })

    holdout = pd.DataFrame({
        "Metric": ["ROC-AUC", "PR-AUC", "Balanced accuracy", "Sensitivity", "Specificity", "F1"],
        "Value": [0.805739, 0.610668, 0.755480, 0.692308, 0.818653, 0.620690],
    })

    feature_dictionary = pd.DataFrame({
        "Feature": [
            "NEUROBAT__LDELTOTAL",
            "UWNPSYCHSUM__ADNI_MEM",
            "UWNPSYCHSUM__ADNI_EF",
            "UWNPSYCHSUM__ADNI_EF2",
            "GDSCALE__GDHOME",
            "APOERES__GENOTYPE",
            "UCSFFSX7__ST99TA",
            "UCSFFSX7__ST88SV",
            "UCSFFSX7__ST13TA",
        ],
        "Plain-English Meaning": [
            "Delayed logical memory total score",
            "ADNI memory composite score",
            "ADNI executive function composite score",
            "Second ADNI executive function composite",
            "Depression scale item related to staying home",
            "APOE genotype",
            "FreeSurfer structural MRI marker, code ST99TA",
            "FreeSurfer structural MRI marker, code ST88SV",
            "FreeSurfer structural MRI marker, code ST13TA",
        ],
        "Biological Interpretation": [
            "Delayed recall is strongly affected by early Alzheimer’s-related memory-system decline.",
            "Summarizes memory performance across tasks; memory decline is central to progression.",
            "Reflects executive functioning and broader cognitive network impairment.",
            "Adds another executive-function signal related to planning, attention, and flexibility.",
            "May capture functional or behavioral changes associated with progression.",
            "Captures inherited risk, especially APOE ε4-associated Alzheimer’s vulnerability.",
            "MRI marker; map to FreeSurfer lookup table before making region-specific claims.",
            "MRI marker; contributed little after memory features were included.",
            "MRI marker; contributed little after memory features were included.",
        ],
    })

    return baseline, full_models, minimal, ablation, stability, holdout, feature_dictionary

baseline, full_models, minimal, ablation, stability, holdout, feature_dictionary = load_results()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    # 🧠 Alzheimer’s Minimal Markers

    ### 2-year MCI-to-dementia progression

    Dashboard for a longitudinal ADNI machine learning project focused on minimal marker discovery.
    """)

    page = st.radio(
        "Navigation",
        ["Home", "Methods", "Model Results", "Minimal Panels", "Biology", "Replicate"],
    )

    st.markdown("---")
    st.markdown("**Target variable**")
    st.markdown("`0 = stable MCI`")
    st.markdown("`1 = converted to dementia within 2 years`")

# ============================================================
# HOME
# ============================================================

if page == "Home":
    st.markdown("""
    <div class="hero">
        <div class="hero-title">
            Minimal Clinical and Imaging Markers for Alzheimer’s Progression Prediction
        </div>
        <div class="hero-subtitle">
            This project asks whether a small set of clinical, cognitive, genetic, and MRI markers can predict 2-year MCI-to-dementia progression nearly as well as larger multimodal models.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("MCI patients", "1,029")
    with c2: metric_card("2-year converters", "261")
    with c3: metric_card("Best CV AUC", "0.819")
    with c4: metric_card("Holdout AUC", "0.806")

    st.markdown("<hr>", unsafe_allow_html=True)

    section_header("Research Question", "How much information is actually necessary to predict short-term Alzheimer’s progression?")

    st.markdown("""
    <div class="callout">
    The central question is simple: <b>Can a small, low-burden marker panel predict 2-year MCI-to-dementia progression almost as well as a large clinical + MRI model?</b><br><br>
    This matters because cognitive testing, genetic testing, and MRI scans differ in cost, availability, and patient burden.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    cards = [
        ("🧪", "Clinical/Cognitive", "Memory, executive function, demographics, and depression-scale variables."),
        ("🧬", "Genetic", "APOE genotype was included because APOE ε4 is a major Alzheimer’s risk factor."),
        ("🧠", "MRI", "FreeSurfer structural MRI variables were tested as higher-burden biomarkers."),
        ("📉", "Minimal Panels", "The analysis searched for 1-, 2-, 3-, and 5-feature panels.")
    ]
    cols = st.columns(4)
    for col, card in zip(cols, cards):
        with col:
            glass_card(*card)

    st.markdown("<hr>", unsafe_allow_html=True)

    section_header("Main Result")
    st.markdown("""
    <div class="callout">
    The best 5-feature clinical/APOE panel achieved <b>AUC = 0.816</b>, nearly matching the best 5-feature clinical + MRI panel at <b>AUC = 0.819</b>.
    The difference was only <b>0.003 AUC</b>, suggesting that MRI added only marginal predictive value once strong cognitive markers were included.
    </div>
    """, unsafe_allow_html=True)

    fig = px.bar(
        pd.DataFrame({
            "Panel": ["Clinical/APOE 5-marker", "Clinical/MRI 5-marker", "Holdout best panel"],
            "ROC-AUC": [0.815647, 0.819361, 0.805739]
        }),
        x="Panel",
        y="ROC-AUC",
        text="ROC-AUC",
        color_discrete_sequence=[CHART_COLORS["primary"]]
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_yaxes(range=[0.70, 0.85], gridcolor="rgba(148,163,184,0.12)")
    fig.update_xaxes(showgrid=False)
    plotly_layout(fig, "Key performance comparison")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# METHODS
# ============================================================

elif page == "Methods":
    section_header("Methods", "What the code does, what each modeling decision tests, and why it was used.")

    stages = [
        ("1. Build the cohort", "Filtered ADNI to MCI patients and constructed a 2-year progression label.", "Predicting MCI-to-dementia conversion is more clinically meaningful than separating patients who already have dementia.", "DXSUM diagnosis history and visit timing."),
        ("2. Create the target", "Assigned y = 1 if an MCI patient converted to dementia within 2 years, otherwise y = 0.", "This turns the project into a binary supervised learning problem.", "1,029 MCI patients: 768 stable and 261 converters."),
        ("3. Merge features", "Joined clinical/cognitive, APOE, and FreeSurfer MRI features by patient ID and visit.", "Progression risk may be reflected in cognition, genetics, and brain structure.", "PTDEMOG, NEUROBAT, UWNPSYCHSUM, GDSCALE, APOERES, UCSFFSX6, UCSFFSX7."),
        ("4. Remove leakage", "Removed MMSE, MoCA, CDR, FAQ, ADAS, diagnosis codes, and future conversion variables.", "Leakage would make the model artificially strong by giving it diagnosis-like information.", "Feature columns were filtered before training."),
        ("5. Test full feature groups", "Compared clinical-only, genetic-only, MRI-only, clinical + genetic, clinical + MRI, and full multimodal feature sets.", "This tests whether MRI adds value beyond lower-burden clinical/cognitive markers.", "108 clinical features, 1 APOE feature, and 650 MRI features."),
        ("6. Compare models", "Tested Logistic Regression L1/L2, Random Forest, and Extra Trees.", "Logistic models are interpretable; tree models test nonlinear patterns.", "Grouped 5-fold cross-validation."),
        ("7. Minimal-marker search", "Used L1 Logistic Regression to evaluate 1-, 2-, 3-, and 5-marker panels.", "LASSO shrinks weak coefficients toward zero and supports sparse feature selection.", "Candidate clinical, genetic, and MRI features."),
        ("8. Burden analysis", "Assigned testing burden scores and plotted AUC versus burden.", "A small performance gain may not justify much higher testing burden.", "Clinical/APOE lower burden; MRI higher burden."),
        ("9. Ablation and stability", "Removed one feature at a time and counted feature selection frequency.", "This tests which markers are actually carrying model performance.", "Top minimal panels."),
        ("10. Holdout validation", "Tested the best minimal panel on unseen patients.", "This checks if the model generalizes beyond cross-validation.", "771 training patients and 258 test patients."),
    ]

    for title, what, why, data in stages:
        with st.expander(title):
            st.markdown(f"**What it does:** {what}")
            st.markdown(f"**Why this matters:** {why}")
            st.markdown(f"**Data used:** {data}")

    st.markdown("<hr>", unsafe_allow_html=True)
    section_header("Modeling choices in simple words")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Logistic Regression
        Predicts the probability of conversion and is easier to interpret.

        ### L1 Logistic Regression / LASSO
        Shrinks weak features to zero. Useful for finding small marker panels.

        ### L2 Logistic Regression
        Shrinks coefficients but usually keeps most features. Helps reduce overfitting.
        """)
    with col2:
        st.markdown("""
        ### Random Forest
        Builds many decision trees and can capture nonlinear relationships.

        ### Extra Trees
        Similar to Random Forest but adds more randomness.

        ### Grouped Cross-Validation
        Keeps the same patient out of both train and test folds to avoid leakage.
        """)

# ============================================================
# MODEL RESULTS
# ============================================================

elif page == "Model Results":
    section_header("Full Model Results", "Baseline models show how different data modalities perform before minimal-marker selection.")

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Best full model AUC", "0.820")
    with c2: metric_card("Best LASSO AUC", "0.801")
    with c3: metric_card("MRI-only LASSO AUC", "0.638")
    with c4: metric_card("Clinical+APOE features", "109")

    fig = px.bar(
        baseline.sort_values("ROC-AUC"),
        x="ROC-AUC",
        y="Feature Set",
        orientation="h",
        color_discrete_sequence=[CHART_COLORS["primary"]],
        text="ROC-AUC"
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_xaxes(range=[0.55, 0.83], gridcolor="rgba(148,163,184,0.12)")
    fig.update_yaxes(showgrid=False)
    plotly_layout(fig, "Interpretable LASSO baseline results")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="callout">
    Clinical + APOE features performed best among the interpretable LASSO feature groups.
    MRI-only performance was much lower, suggesting structural MRI alone was weaker than cognitive and genetic information for this task.
    </div>
    """, unsafe_allow_html=True)

    section_header("Best model by feature group")
    fig2 = px.bar(
        full_models.sort_values("ROC-AUC"),
        x="ROC-AUC",
        y="Feature Set",
        orientation="h",
        color_discrete_sequence=[CHART_COLORS["secondary"]],
        text="ROC-AUC"
    )
    fig2.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig2.update_xaxes(range=[0.58, 0.84], gridcolor="rgba(148,163,184,0.12)")
    fig2.update_yaxes(showgrid=False)
    plotly_layout(fig2, "Best full model performance by modality")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(baseline.style.format({
        "ROC-AUC": "{:.3f}",
        "PR-AUC": "{:.3f}",
        "Balanced Accuracy": "{:.3f}",
        "Sensitivity": "{:.3f}",
        "Specificity": "{:.3f}"
    }), use_container_width=True)

# ============================================================
# MINIMAL PANELS
# ============================================================

elif page == "Minimal Panels":
    section_header("Minimal Marker Panels", "How close small marker panels get to full multimodal models.")

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Best 1-marker AUC", "0.756")
    with c2: metric_card("Best 2-marker AUC", "0.799")
    with c3: metric_card("Best 3-marker AUC", "0.815")
    with c4: metric_card("Best 5-marker AUC", "0.819")

    selected_groups = st.multiselect(
        "Select feature groups to show",
        options=sorted(minimal["Feature Group"].unique()),
        default=sorted(minimal["Feature Group"].unique())
    )
    filtered = minimal[minimal["Feature Group"].isin(selected_groups)].copy()

    fig = px.scatter(
        filtered,
        x="Burden Score",
        y="ROC-AUC",
        size="Number of Features",
        color="Feature Group",
        hover_data=["Panel", "Features", "PR-AUC", "Sensitivity", "Specificity"],
        color_discrete_sequence=[CHART_COLORS["primary"], CHART_COLORS["secondary"], CHART_COLORS["green"]]
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.12)")
    fig.update_yaxes(range=[0.62, 0.84], gridcolor="rgba(148,163,184,0.12)")
    plotly_layout(fig, "Predictive performance vs testing burden")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="callout">
    The clinical/APOE 5-marker panel reached AUC = 0.816 with a burden score of 4.5.
    The best 5-marker MRI-containing panel reached AUC = 0.819 with a burden score of 17.
    MRI improved AUC by only 0.003 while requiring much higher testing burden.
    </div>
    """, unsafe_allow_html=True)

    fig2 = px.line(
        minimal.sort_values(["Feature Group", "Number of Features"]),
        x="Number of Features",
        y="ROC-AUC",
        color="Feature Group",
        markers=True,
        color_discrete_sequence=[CHART_COLORS["primary"], CHART_COLORS["secondary"], CHART_COLORS["green"]]
    )
    fig2.update_xaxes(dtick=1, gridcolor="rgba(148,163,184,0.12)")
    fig2.update_yaxes(range=[0.62, 0.84], gridcolor="rgba(148,163,184,0.12)")
    plotly_layout(fig2, "AUC gained by adding markers")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        minimal.sort_values("ROC-AUC", ascending=False).style.format({
            "ROC-AUC": "{:.3f}",
            "PR-AUC": "{:.3f}",
            "Sensitivity": "{:.3f}",
            "Specificity": "{:.3f}",
            "Burden Score": "{:.1f}"
        }),
        use_container_width=True
    )

    section_header("Ablation: which features actually matter?")
    fig3 = px.bar(
        ablation.sort_values("AUC Drop"),
        x="AUC Drop",
        y="Removed Feature",
        orientation="h",
        color_discrete_sequence=[CHART_COLORS["orange"]],
        text="AUC Drop"
    )
    fig3.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig3.update_xaxes(gridcolor="rgba(148,163,184,0.12)")
    fig3.update_yaxes(showgrid=False)
    plotly_layout(fig3, "AUC drop after removing each feature")
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# BIOLOGY
# ============================================================

elif page == "Biology":
    section_header("Biological Interpretation", "What the selected features suggest about Alzheimer’s progression.")

    st.markdown("""
    <div class="callout">
    The strongest and most stable predictors were memory-related cognitive features.
    This is biologically plausible because Alzheimer’s disease often affects memory systems early.
    </div>
    """, unsafe_allow_html=True)

    fig = px.bar(
        stability.sort_values("Selection Count"),
        x="Selection Count",
        y="Feature",
        orientation="h",
        color_discrete_sequence=[CHART_COLORS["primary"]],
        text="Selection Count"
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.12)")
    fig.update_yaxes(showgrid=False)
    plotly_layout(fig, "Feature stability across top panels")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="callout">
    NEUROBAT__LDELTOTAL was selected far more often than any other feature.
    This means delayed memory was repeatedly useful across top-performing minimal panels.
    </div>
    """, unsafe_allow_html=True)

    section_header("Feature dictionary")
    st.dataframe(feature_dictionary, use_container_width=True)

    st.markdown("""
    <div class="warning-callout">
    Important note: MRI variables such as UCSFFSX7__ST99TA are FreeSurfer-coded structural markers.
    They should be mapped to actual brain-region names using the ADNI/FreeSurfer lookup table before making strong region-specific biological claims.
    </div>
    """, unsafe_allow_html=True)

    section_header("Final holdout validation")
    c1, c2 = st.columns([1.1, 1])

    with c1:
        fig2 = px.bar(
            holdout,
            x="Metric",
            y="Value",
            color_discrete_sequence=[CHART_COLORS["green"]],
            text="Value"
        )
        fig2.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig2.update_yaxes(range=[0, 0.9], gridcolor="rgba(148,163,184,0.12)")
        fig2.update_xaxes(showgrid=False)
        plotly_layout(fig2, "Held-out test performance")
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        cm = np.array([[158, 35], [20, 45]])
        fig3 = px.imshow(
            cm,
            text_auto=True,
            labels=dict(x="Predicted", y="Actual", color="Count"),
            x=["Stable", "Converter"],
            y=["Stable", "Converter"],
            color_continuous_scale="Blues"
        )
        plotly_layout(fig3, "Confusion matrix")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="callout">
    On the held-out test set, the best minimal panel achieved AUC = 0.806.
    It correctly identified 45 of 65 converters and 158 of 193 stable patients.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# REPLICATE
# ============================================================

elif page == "Replicate":
    section_header("How to Replicate", "What files are needed and how to run the analysis.")

    st.markdown("""
    ### Your current GitHub structure should be:

    ```text
    project/
    ├── README.md
    ├── app.py
    ├── requirements.txt
    ├── longitudinal_minimal_marker_pipeline.ipynb
    ├── Parse_R_Files_Longitudinal_Minimal_Markers.R
    ├── csvs/
    │   ├── APOERES.csv
    │   ├── DXSUM.csv
    │   ├── GDSCALE.csv
    │   ├── NEUROBAT.csv
    │   ├── PTDEMOG.csv
    │   ├── UCSFFSX6.csv
    │   ├── UCSFFSX7.csv
    │   └── UWNPSYCHSUM.csv
    └── .streamlit/
        └── config.toml
    ```
    """)

    st.markdown("""
    ### Run order

    1. Put the Streamlit files from the ZIP into your repo root.
    2. Make sure your CSVs are inside the `csvs/` folder.
    3. Install dependencies.
    4. Run the app.
    """)

    st.code("pip install -r requirements.txt", language="bash")
    st.code("streamlit run app.py", language="bash")

    st.markdown("""
    ### What to check

    - Target distribution should be approximately 768 stable and 261 converters.
    - Clinical/APOE LASSO AUC should be around 0.80.
    - Best 5-feature minimal panel should be around 0.82 cross-validated AUC.
    - Holdout AUC should be around 0.81.
    """)

    st.markdown("""
    <div class="warning-callout">
    This dashboard uses embedded summary results from your completed notebook. It does not need the raw ADNI CSVs to render.
    If you want a dynamic dashboard later, replace the hardcoded result tables in load_results() with CSV reads from your outputs folder.
    </div>
    """, unsafe_allow_html=True)

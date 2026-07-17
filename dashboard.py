import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

try:
    import streamlit.runtime as _st_runtime
    if not _st_runtime.exists():
        print("\n" + "=" * 70)
        print("ERROR: Don't run this file with 'python dashboard.py'.")
        print("Streamlit apps must be launched like this instead:")
        print(f"\n    streamlit run {os.path.basename(__file__)}\n")
        print("=" * 70 + "\n")
        sys.exit(1)
except ImportError:
    pass

# Primary/default dataset filename — the app will look for this first.
DATA_PATH = "AI.csv"

SCRIPT_DIR = Path(__file__).resolve().parent


# All the filenames the app will try automatically, in order of priority.
CANDIDATE_NAMES = [
    DATA_PATH,
    "AI.csv",
    "ai.csv",
    "ai_student_impact_dataset.csv",
    "ai_student_impact_dataset__1_.csv",
]

st.set_page_config(
    page_title="AI Student Impact Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
import base64


def get_base64_image(image_path: Path) -> str | None:
    """Return the base64-encoded contents of an image, or None if it's missing."""
    if not image_path.exists():
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def set_background():
    # Looks for images/ai_background.jpg next to dashboard.py, regardless of
    # what folder Streamlit was launched from.
    img_path = SCRIPT_DIR / "images" / "ai_background.jpg"
    encoded = get_base64_image(img_path)
    if encoded is None:
        return  # No background image found — skip silently instead of crashing.

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(rgba(4,8,28,.93), rgba(4,8,28,.93)),
                url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Streamlit's own toolbar is opaque white by default — make it blend in */
        header[data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0) !important;
        }}
        [data-testid="stToolbar"] {{
            right: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


set_background()

st.markdown(
    """
    <style>
    /* Overall page padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(5, 12, 34, .96) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 229, 255, .15);
    }
    section[data-testid="stSidebar"] * {
        color: #E6ECFF !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(12, 20, 48, .92) !important;
        border-radius: 16px;
        border: 1px solid rgba(0, 229, 255, .30);
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 24px rgba(0, 0, 0, .35), 0 0 20px rgba(0, 229, 255, .12);
    }
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] * {
        color: #9DB2E8 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        color: #FFFFFF !important;
    }
    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] * {
        color: #00E5FF !important;
    }

    /* Chart / dataframe containers */
    div[data-testid="stPyplot"],
    div[data-testid="stDataFrame"] {
        background: rgba(12, 20, 48, .92) !important;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid rgba(0, 229, 255, .18);
        box-shadow: 0 4px 24px rgba(0, 0, 0, .35);
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background: #00E5FF;
        color: #04081C;
        border-radius: 10px;
        border: none;
        font-weight: 700;
    }

    /* Titles */
    h1, h2, h3 {
        color: #00E5FF !important;
        text-shadow: 0 0 18px rgba(0, 229, 255, .25);
    }

    p, label, span, .stMarkdown, .stCaption {
        color: #E6ECFF;
    }

    /* About / info boxes */
    .section-note {
        background: rgba(12, 20, 48, .92);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(0, 229, 255, .25);
        color: #E6ECFF;
        box-shadow: 0 4px 24px rgba(0, 0, 0, .35), 0 0 15px rgba(0, 229, 255, .12);
        line-height: 1.6;
    }

    /* Multiselect / input widgets */
    div[data-baseweb="select"] > div,
    div[data-baseweb="tag"] {
        background: rgba(12, 20, 48, .92) !important;
        border-color: rgba(0, 229, 255, .30) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

plt.rcParams["figure.dpi"] = 120
plt.style.use("seaborn-v0_8-whitegrid") if "seaborn-v0_8-whitegrid" in plt.style.available else None

# Make every matplotlib chart match the dark dashboard theme automatically —
# this affects all st.pyplot() figures created below without touching each one.
CHART_BG = "#101a37"
plt.rcParams.update({
    "figure.facecolor": CHART_BG,
    "axes.facecolor": CHART_BG,
    "savefig.facecolor": CHART_BG,
    "axes.edgecolor": "#2a3a66",
    "axes.labelcolor": "#E6ECFF",
    "text.color": "#E6ECFF",
    "xtick.color": "#B7C3E6",
    "ytick.color": "#B7C3E6",
    "grid.color": "#22335e",
    "grid.alpha": 0.6,
    "legend.facecolor": CHART_BG,
    "legend.edgecolor": "#2a3a66",
    "legend.labelcolor": "#E6ECFF",
    "axes.titlecolor": "#00E5FF",
})

YEAR_ORDER = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
SKILL_ORDER = ["Beginner", "Intermediate", "Advanced"]
BURNOUT_ORDER = ["Low", "Medium", "High"]
BURNOUT_COLORS = {"Low": "#55A868", "Medium": "#DD8452", "High": "#C44E52"}
POLICY_ORDER = ["Strict_Ban", "Allowed_With_Citation", "Actively_Encouraged"]



@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["GPA_Change"] = df["Post_Semester_GPA"] - df["Pre_Semester_GPA"]
    return df

def find_csv() -> Path | None:
    """Look for the dataset next to app.py (and in the current working
    directory) under a few likely filenames, case-insensitively. Falls
    back to any CSV in those folders whose name contains 'ai'."""
    search_dirs = [SCRIPT_DIR, Path.cwd()]

    # 1) Exact/known candidate names (case variations included).
    for directory in search_dirs:
        for name in CANDIDATE_NAMES:
            candidate = directory / name
            if candidate.exists():
                return candidate

    # 2) Case-insensitive match against every CSV in the folder.
    for directory in search_dirs:
        if not directory.exists():
            continue
        for csv_file in directory.glob("*.csv"):
            if csv_file.name.lower() in {n.lower() for n in CANDIDATE_NAMES}:
                return csv_file

    # 3) Last resort: any csv with "ai" in the name.
    for directory in search_dirs:
        if not directory.exists():
            continue
        for csv_file in directory.glob("*.csv"):
            if "ai" in csv_file.name.lower():
                return csv_file

    return None

def get_data() -> pd.DataFrame:
    """Load the dataset automatically by looking for AI.csv (no upload
    option — the file must be present next to app.py or in the working
    directory)."""
    found_path = find_csv()
    if found_path is not None:
        return load_data(str(found_path))

    # st.title("🤖 AI Student Impact Dashboard")
    st.error(
        f"Couldn't find **AI.csv** automatically.\n\n"
        f"Looked in:\n- `{SCRIPT_DIR}`\n- `{Path.cwd()}`\n\n"
        f"Make sure your dataset CSV is named `AI.csv` and placed in the same "
        f"folder as `app.py`, then reload the app."
    )
    st.stop()


def add_ai_hours_bucket(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["AI_Hours_Bucket"] = pd.cut(
        df["Weekly_GenAI_Hours"], bins=[0, 5, 10, 20, 30, 40],
        labels=["0-5", "5-10", "10-20", "20-30", "30-40"],
    )
    return df



def render_sidebar(df: pd.DataFrame):
    st.sidebar.title("🤖 AI Student Impact")
    st.sidebar.caption("Explore how GenAI tools affect student performance & wellbeing.")

    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Home", "📄 Dataset", "🧠 AI Usage", "🎓 Academic Performance",
         "😰 Burnout & Wellbeing", "🔍 Insights"],
    )

    NAV_DESCRIPTIONS = {
        "🏠 Home": "High-level overview: key metrics and top-line charts at a glance.",
        "📄 Dataset": "Browse, search, and download the raw (filtered) student records.",
        "🧠 AI Usage": "How students use GenAI tools — hours, skill level, use cases, tool diversity.",
        "🎓 Academic Performance": "GPA trends before/after AI adoption, by major and policy.",
        "😰 Burnout & Wellbeing": "Relationship between AI usage, burnout risk, and exam anxiety.",
        "🔍 Insights": "Correlations across all variables and key takeaways from the data.",
    }
    st.sidebar.info(NAV_DESCRIPTIONS[page])

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")

    majors = sorted(df["Major_Category"].unique())
    selected_majors = st.sidebar.multiselect("Major", majors, default=majors)

    years = [y for y in YEAR_ORDER if y in df["Year_of_Study"].unique()]
    selected_years = st.sidebar.multiselect("Year of Study", years, default=years)

    policies = sorted(df["Institutional_Policy"].unique())
    selected_policies = st.sidebar.multiselect("Institutional Policy", policies, default=policies)

    filtered = df[
        df["Major_Category"].isin(selected_majors)
        & df["Year_of_Study"].isin(selected_years)
        & df["Institutional_Policy"].isin(selected_policies)
    ]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** students")

    return page, filtered



def page_home(df: pd.DataFrame):
    st.title("🤖 AI Student Impact Dashboard")
    st.title("🏠 Overview")
    st.caption("A quick snapshot of GenAI usage across the student population.")

    st.markdown("""
    <div class="section-note">
    <b>About this project:</b> This dashboard analyzes survey data from 50,000 college students
    on how they use Generative AI tools (like ChatGPT) for academic work. It explores four angles:
    how much and how students use AI, how AI use relates to changes in GPA, how it relates to
    burnout/anxiety, and what patterns emerge when everything is compared side by side.
    Use the sidebar to filter by Major, Year of Study, and Institutional Policy, then explore
    each section below.
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("No data matches the current filters.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", f"{len(df):,}")
    col2.metric("Avg Weekly GenAI Hours", f"{df['Weekly_GenAI_Hours'].mean():.1f} hrs")
    col3.metric("Avg GPA Change", f"{df['GPA_Change'].mean():+.2f}")
    high_burnout_pct = (df["Burnout_Risk_Level"] == "High").mean() * 100
    col4.metric("High Burnout Risk", f"{high_burnout_pct:.0f}%")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(df["Weekly_GenAI_Hours"], bins=40, color="#4C72B0", edgecolor="white")
        ax.set_title("Distribution of Weekly GenAI Hours")
        ax.set_xlabel("Weekly GenAI Hours")
        ax.set_ylabel("Students")
        st.pyplot(fig)

    with c2:
        counts = df["Burnout_Risk_Level"].value_counts().reindex(BURNOUT_ORDER)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(
            counts.values, labels=counts.index, autopct="%1.0f%%",
            colors=[BURNOUT_COLORS[c] for c in counts.index],
        )
        ax.set_title("Burnout Risk Breakdown")
        st.pyplot(fig)

    c3, c4 = st.columns(2)

    with c3:
        counts = df["Primary_Use_Case"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(counts.index, counts.values, color="#8172B2")
        ax.set_title("Primary GenAI Use Case")
        ax.set_ylabel("Students")
        ax.tick_params(axis="x", rotation=30)
        st.pyplot(fig)

    with c4:
        dfb = add_ai_hours_bucket(df)
        avg_gpa = dfb.groupby("AI_Hours_Bucket", observed=True)["GPA_Change"].mean()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(avg_gpa.index.astype(str), avg_gpa.values, color="#4C72B0")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Avg GPA Change by Weekly AI Hours")
        ax.set_xlabel("Weekly GenAI Hours")
        ax.set_ylabel("Avg GPA Change")
        st.pyplot(fig)



def page_dataset(df: pd.DataFrame):
    st.title("📄 Dataset")
    st.caption("Full dataset with the sidebar filters applied.")
    st.markdown("""
    <div class="section-note">
    This table shows every student record matching your current sidebar filters.
    Use the search box to look up a specific Student ID, or download the filtered
    slice as a CSV for offline analysis.
    </div>
    """, unsafe_allow_html=True)
    st.write(f"**Rows:** {df.shape[0]:,}  |  **Columns:** {df.shape[1]}")

    search = st.text_input("Search by Student ID")
    view_df = df.copy()
    if search:
        view_df = view_df[view_df["Student_ID"].astype(str).str.contains(search)]

    st.dataframe(view_df, use_container_width=True, height=500)

    csv = view_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=csv,
        file_name="filtered_ai_student_data.csv",
        mime="text/csv",
    )

    with st.expander("Column summary statistics"):
        st.dataframe(view_df.describe(include="all").T, use_container_width=True)



def page_ai_usage(df: pd.DataFrame):
    st.title("🧠 AI Usage")
    st.caption("How students are using GenAI tools.")
    st.markdown("""
    <div class="section-note">
    This section breaks down <b>how</b> students engage with GenAI tools — usage hours by
    major, self-reported prompt-engineering skill, number of distinct tools used, and
    whether they pay for premium access.
    </div>
    """, unsafe_allow_html=True)
    if df.empty:
        st.info("No data matches the current filters.")
        return

    c1, c2 = st.columns(2)

    with c1:
        majors = sorted(df["Major_Category"].unique())
        data = [df.loc[df["Major_Category"] == m, "Weekly_GenAI_Hours"].values for m in majors]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(data, tick_labels=majors)
        ax.set_title("Weekly GenAI Hours by Major")
        ax.set_ylabel("Weekly GenAI Hours")
        ax.tick_params(axis="x", rotation=20)
        st.pyplot(fig)

    with c2:
        counts = df["Prompt_Engineering_Skill"].value_counts().reindex(SKILL_ORDER)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%")
        ax.set_title("Prompt Engineering Skill Level")
        st.pyplot(fig)

    c3, c4 = st.columns(2)

    with c3:
        counts = df["Tool_Diversity"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(counts.index.astype(str), counts.values, color="#8172B2")
        ax.set_title("Tool Diversity (Number of Distinct Tools Used)")
        ax.set_xlabel("Tools Used")
        ax.set_ylabel("Students")
        st.pyplot(fig)

    with c4:
        counts = df["Paid_Subscription"].value_counts()
        labels = ["Paid" if v else "Free" for v in counts.index]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(counts.values, labels=labels, autopct="%1.0f%%", colors=["#4C72B0", "#DD8452"])
        ax.set_title("Paid vs Free Subscription")
        st.pyplot(fig)

        st.markdown("---")
    use_cases = sorted(df["Primary_Use_Case"].unique())
    data = [df.loc[df["Primary_Use_Case"] == u, "Weekly_GenAI_Hours"].values for u in use_cases]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.boxplot(data, tick_labels=use_cases)
    ax.set_title("Weekly GenAI Hours by Primary Use Case")
    ax.set_ylabel("Weekly GenAI Hours")
    st.pyplot(fig)



def page_academic(df: pd.DataFrame):
    st.title("🎓 Academic Performance")
    st.caption("Pre/post-semester GPA trends and what predicts GPA change.")
    st.markdown("""
    <div class="section-note">
    Here we compare each student's GPA before and after the semester of AI-assisted study,
    and see how that change varies by major, institutional AI policy, and traditional
    (non-AI) study hours.
    </div>
    """, unsafe_allow_html=True)
    if df.empty:
        st.info("No data matches the current filters.")
        return

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(df["Pre_Semester_GPA"], bins=30, alpha=0.6, label="Pre-Semester GPA", color="#4C72B0")
        ax.hist(df["Post_Semester_GPA"], bins=30, alpha=0.6, label="Post-Semester GPA", color="#DD8452")
        ax.set_title("Pre vs Post Semester GPA Distribution")
        ax.legend()
        st.pyplot(fig)

    with c2:
        avg_by_major = df.groupby("Major_Category")["GPA_Change"].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(avg_by_major.index, avg_by_major.values, color="#4C72B0")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Avg GPA Change by Major")
        ax.set_ylabel("Avg GPA Change")
        ax.tick_params(axis="x", rotation=20)
        st.pyplot(fig)

    c3, c4 = st.columns(2)

    with c3:
        policy_order = [p for p in POLICY_ORDER if p in df["Institutional_Policy"].unique()]
        avg_by_policy = df.groupby("Institutional_Policy")["GPA_Change"].mean().reindex(policy_order)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(avg_by_policy.index, avg_by_policy.values, color="#C44E52")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Avg GPA Change by Institutional Policy")
        ax.set_ylabel("Avg GPA Change")
        ax.tick_params(axis="x", rotation=15)
        st.pyplot(fig)

    with c4:
        sample = df.sample(min(3000, len(df)), random_state=1)
        x = sample["Traditional_Study_Hours"].values
        y = sample["GPA_Change"].values
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(x, y, alpha=0.2, s=10, color="#55A868")
        # trend line using numpy polyfit
        coeffs = np.polyfit(x, y, 1)
        trend_x = np.linspace(x.min(), x.max(), 100)
        trend_y = np.polyval(coeffs, trend_x)
        ax.plot(trend_x, trend_y, color="red", linewidth=2)
        ax.set_title("Traditional Study Hours vs GPA Change")
        ax.set_xlabel("Traditional Study Hours")
        ax.set_ylabel("GPA Change")
        st.pyplot(fig)



def page_burnout(df: pd.DataFrame):
    st.title("😰 Burnout & Wellbeing")
    st.caption("How AI usage relates to burnout risk and exam anxiety.")
    st.markdown("""
    <div class="section-note">
    Heavy AI reliance isn't free of cost. This section looks at how weekly AI usage
    correlates with burnout risk, exam anxiety, and perceived dependency on AI tools.
    </div>
    """, unsafe_allow_html=True)
    if df.empty:
        st.info("No data matches the current filters.")
        return

    dfb = add_ai_hours_bucket(df)
    ct = pd.crosstab(dfb["AI_Hours_Bucket"], dfb["Burnout_Risk_Level"], normalize="index")
    ct = ct.reindex(columns=[c for c in BURNOUT_ORDER if c in ct.columns])

    fig, ax = plt.subplots(figsize=(9, 4))
    bottom = np.zeros(len(ct))
    for level in ct.columns:
        ax.bar(ct.index.astype(str), ct[level].values, bottom=bottom,
               label=level, color=BURNOUT_COLORS[level])
        bottom += ct[level].values
    ax.set_title("Burnout Risk Distribution by Weekly GenAI Usage")
    ax.set_xlabel("Weekly GenAI Hours")
    ax.set_ylabel("Proportion of Students")
    ax.legend(title="Burnout Risk")
    st.pyplot(fig)

    c1, c2 = st.columns(2)

    with c1:
        order_use = df.groupby("Primary_Use_Case")["Anxiety_Level_During_Exams"].mean().sort_values(
            ascending=False
        )
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(order_use.index, order_use.values, color="#DD8452")
        ax.set_title("Avg Exam Anxiety by Primary Use Case")
        ax.set_ylabel("Avg Anxiety Level")
        ax.tick_params(axis="x", rotation=25)
        st.pyplot(fig)

    with c2:
        data = [df.loc[df["Burnout_Risk_Level"] == b, "Perceived_AI_Dependency"].values
                for b in BURNOUT_ORDER if b in df["Burnout_Risk_Level"].unique()]
        labels = [b for b in BURNOUT_ORDER if b in df["Burnout_Risk_Level"].unique()]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(data, tick_labels=labels)
        ax.set_title("Perceived AI Dependency by Burnout Risk")
        ax.set_ylabel("Perceived AI Dependency")
        st.pyplot(fig)



def page_insights(df: pd.DataFrame):
    st.title("🔍 Insights")
    st.caption("Correlations and key takeaways from the (filtered) data.")
    st.markdown("""
    <div class="section-note">
    A correlation matrix across all numeric variables, plus a plain-language summary
    of the most notable patterns found in the (filtered) dataset.
    </div>
    """, unsafe_allow_html=True)
    if df.empty:
        st.info("No data matches the current filters.")
        return

    num_cols = [
        "Pre_Semester_GPA", "Weekly_GenAI_Hours", "Tool_Diversity",
        "Traditional_Study_Hours", "Perceived_AI_Dependency",
        "Anxiety_Level_During_Exams", "Post_Semester_GPA",
        "Skill_Retention_Score", "GPA_Change",
    ]
    corr = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(num_cols)))
    ax.set_xticklabels(num_cols, rotation=45, ha="right")
    ax.set_yticks(range(len(num_cols)))
    ax.set_yticklabels(num_cols)
    for i in range(len(num_cols)):
        for j in range(len(num_cols)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center",
                    color="black", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Correlation Matrix")
    fig.tight_layout()
    st.pyplot(fig)

    st.markdown("### Key Takeaways")
    st.markdown(
        """
- **More AI hours doesn't mean more GPA gain.** The biggest GPA improvements
  cluster around 5–10 hrs/week of GenAI use; beyond 20 hrs/week, gains taper off.
- **Burnout scales sharply with usage.** Students using GenAI over 30 hrs/week
  show dramatically higher rates of high burnout risk than light users.
- **Traditional study hours remain the strongest predictor** of GPA change —
  more so than any AI-usage variable in this dataset.
- **Institutional policy shows a comparatively small effect** on GPA outcomes
  between strict bans and active encouragement.
        """
    )



def main():
    df_full = get_data()
    page, df_filtered = render_sidebar(df_full)

    if page == "🏠 Home":
        page_home(df_filtered)
    elif page == "📄 Dataset":
        page_dataset(df_filtered)
    elif page == "🧠 AI Usage":
        page_ai_usage(df_filtered)
    elif page == "🎓 Academic Performance":
        page_academic(df_filtered)
    elif page == "😰 Burnout & Wellbeing":
        page_burnout(df_filtered)
    elif page == "🔍 Insights":
        page_insights(df_filtered)


if __name__ == "__main__":
    main()
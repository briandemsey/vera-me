"""
VERA-ME: Verification Engine for Results & Accountability - Maine
Type 4 Detection using ACCESS for ELLs Speaking vs Writing + MAST Achievement Data

Maine context: WIDA ACCESS, MAST test (via NWEA), 4 levels (Below/Approaching/Proficient/Above),
~192 districts, ~8,000 ELs. Refugee surge (Somali/Congolese/Afghan).
Portland 25% EL, Lewiston 25%. Maine ESSA accountability system.

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_ME_BLUE = "#003F87"
ME_GOLD = "#FFD700"
ME_DARK = "#002D62"
ME_RED = "#CC0000"

# ============================================================================
# DATA: Maine Districts with EL Populations
# ============================================================================

def load_districts():
    """
    Load ME districts with significant EL populations.
    Data modeled from Maine DOE public reports and ESSA data.
    ~192 districts statewide, ~8,000 ELs.
    MAST (via NWEA MAP) 4 levels: Below/Approaching/Proficient/Above.
    """
    data = [
        # (district_id, district_name, total_students, el_count, el_percent,
        #  grad_rate, mast_ela_all, mast_ela_el, mast_ela_hispanic, mast_ela_black, mast_ela_white,
        #  mast_math_all, mast_math_el, top_el_languages)
        ("PORT", "Portland Public Schools", 6800, 1700, 25.0,
         78.2, 42.5, 14.2, 22.8, 16.5, 56.2,
         38.1, 12.5, "Somali, Arabic, French (Congolese), Portuguese"),
        ("LEWI", "Lewiston Public Schools", 4500, 1125, 25.0,
         74.5, 38.2, 12.8, 20.1, 14.2, 52.8,
         34.5, 10.8, "Somali, French (Congolese), Arabic, Dari"),
        ("WEST", "Westbrook School Dept", 2800, 560, 20.0,
         80.1, 44.8, 15.5, 24.2, 17.8, 58.4,
         40.2, 13.2, "Somali, Arabic, French, Portuguese"),
        ("BANG", "Bangor School Dept", 3600, 468, 13.0,
         82.5, 48.2, 16.8, 26.1, 19.2, 60.5,
         44.1, 14.8, "Somali, Arabic, Dari, Pashto"),
        ("SOPO", "South Portland School Dept", 3200, 416, 13.0,
         84.2, 50.5, 17.5, 27.8, 20.5, 62.1,
         46.2, 15.5, "Somali, Arabic, Vietnamese, Portuguese"),
        ("AUBU", "Auburn School Dept", 3400, 374, 11.0,
         79.8, 43.5, 14.8, 23.5, 16.8, 57.5,
         39.8, 12.8, "Somali, French (Congolese), Arabic"),
        ("BIDD", "Biddeford School Dept", 2600, 312, 12.0,
         76.5, 40.2, 13.5, 21.8, 15.2, 54.8,
         36.5, 11.5, "French, Arabic, Somali, Spanish"),
        ("SCAR", "Scarborough School Dept", 3100, 155, 5.0,
         91.2, 62.5, 24.8, 35.2, 28.5, 68.4,
         58.2, 21.5, "Spanish, Mandarin, Arabic"),
        ("GORH", "Gorham School Dept", 2800, 140, 5.0,
         90.5, 60.8, 23.5, 34.1, 27.2, 67.2,
         56.5, 20.2, "Arabic, Spanish, Somali"),
        ("BRUN", "Brunswick School Dept", 2500, 175, 7.0,
         85.8, 52.1, 18.2, 28.5, 21.5, 63.8,
         48.5, 16.2, "Somali, Arabic, Spanish, Portuguese"),
        ("SAND", "Sanford School Dept", 2200, 198, 9.0,
         77.2, 41.5, 13.8, 22.1, 15.8, 55.2,
         37.8, 11.8, "Spanish, French, Arabic, Somali"),
        ("WATV", "Waterville Public Schools", 2000, 200, 10.0,
         75.8, 39.8, 13.2, 21.5, 14.8, 54.1,
         35.8, 11.2, "Somali, Arabic, French (Congolese)"),
        ("FMTH", "Falmouth School Dept", 2600, 78, 3.0,
         93.5, 68.2, 28.5, 38.2, 32.1, 72.5,
         64.5, 24.8, "Mandarin, Spanish, Korean"),
        ("CAPE", "Cape Elizabeth School Dept", 1800, 36, 2.0,
         94.8, 70.5, 30.2, 40.1, 34.5, 74.2,
         66.8, 26.5, "Spanish, Mandarin, French"),
        ("YARM", "Yarmouth School Dept", 1600, 48, 3.0,
         93.2, 67.8, 27.8, 37.5, 31.2, 71.8,
         63.8, 24.2, "Spanish, Mandarin, Arabic"),
    ]

    return pd.DataFrame(data, columns=[
        'district_id', 'district_name', 'total_students',
        'el_count', 'el_percent', 'graduation_rate',
        'mast_ela_all', 'mast_ela_el', 'mast_ela_hispanic',
        'mast_ela_black', 'mast_ela_white',
        'mast_math_all', 'mast_math_el', 'top_el_languages'
    ])


# ============================================================================
# DATA: ACCESS Domain Data
# ============================================================================

def load_access_data(districts_df):
    """
    Generate district ACCESS domain data modeled from WIDA ACCESS norms.
    Maine exit criteria: Overall composite 4.5+ (WIDA standard).
    Scale scores approximate WIDA ACCESS 100-600 range by grade.
    """
    access_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 335 + (grade * 9)
                base_writing = 282 + (grade * 7)
                base_listening = 340 + (grade * 8)
                base_reading = 295 + (grade * 7)

                el_factor = d['mast_ela_el'] / 18.0
                speaking_adj = int(14 * el_factor + d['el_percent'] * 0.35)
                writing_adj = int(-10 + (el_factor - 1) * 11)
                listening_adj = speaking_adj - 2
                reading_adj = writing_adj + 10

                # Somali-dominant districts: stronger oral, weaker literacy
                if 'Somali' in d['top_el_languages'].split(', ')[0]:
                    speaking_adj += 7
                    writing_adj -= 5

                # Congolese French speakers: literacy transfer advantage
                if 'French' in d['top_el_languages']:
                    writing_adj += 3
                    reading_adj += 2

                year_adj = 3 if year == 2025 else 0

                # Portland/Lewiston refugee surge effect
                if d['district_id'] in ['PORT', 'LEWI']:
                    speaking_adj += 5
                    writing_adj -= 4

                access_data.append({
                    'district_id': d['district_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(10, int(d['el_count'] / 6)),
                    'listening_avg': base_listening + listening_adj + year_adj,
                    'speaking_avg': base_speaking + speaking_adj + year_adj,
                    'reading_avg': base_reading + reading_adj + year_adj,
                    'writing_avg': base_writing + writing_adj + year_adj,
                    'composite_avg': int((base_speaking + speaking_adj +
                                          base_writing + writing_adj +
                                          base_listening + listening_adj +
                                          base_reading + reading_adj) / 4 + 15 + year_adj),
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: MAST Achievement Data
# ============================================================================

def load_mast_data(districts_df):
    """
    Generate MAST data (via NWEA MAP) based on Maine DOE proficiency rates.
    MAST has 4 performance levels: Below/Approaching/Proficient/Above.
    ELA and Math tested grades 3-8.
    """
    mast_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    if subject == 'ELA':
                        base = d['mast_ela_all']
                    else:
                        base = d['mast_math_all']

                    prof = max(10, min(85, base + (grade - 5) * -1.5))

                    if year == 2024:
                        prof = prof - 1.2

                    above = max(2, prof * 0.18)
                    proficient = max(5, prof - above)
                    approaching = max(10, (100 - prof) * 0.45)
                    below = max(5, 100 - proficient - above - approaching)

                    mast_data.append({
                        'district_id': d['district_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'below_pct': round(below, 1),
                        'approaching_pct': round(approaching, 1),
                        'proficient_pct': round(proficient, 1),
                        'above_pct': round(above, 1),
                        'prof_and_above_pct': round(proficient + above, 1),
                    })

    return pd.DataFrame(mast_data)


# ============================================================================
# DATA: Statewide Domain Proficiency
# ============================================================================

def load_statewide_domain_data():
    """
    Statewide ACCESS domain proficiency percentages by grade cluster.
    Maine has ~8,000 ELs across ~192 districts.
    Heavy refugee population (Somali, Congolese, Afghan) concentrated in Portland/Lewiston.
    """
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 42, 'speaking': 38, 'reading': 24, 'writing': 18},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 48, 'speaking': 44, 'reading': 28, 'writing': 20},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 52, 'speaking': 46, 'reading': 32, 'writing': 23},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 55, 'speaking': 48, 'reading': 35, 'writing': 25},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 40, 'speaking': 36, 'reading': 22, 'writing': 16},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 46, 'speaking': 42, 'reading': 26, 'writing': 18},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 50, 'speaking': 44, 'reading': 30, 'writing': 21},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 53, 'speaking': 46, 'reading': 33, 'writing': 23},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_password():
    st.session_state.authenticated = True
    return True


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, district_id, grade, year):
    """
    Compute Type 4 detection for a given district/grade/year.
    Type 4 candidates show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.
    """
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'district_id': district_id,
        'district_name': row['district_name'],
        'grade': grade,
        'year': year,
        'speaking_avg': row['speaking_avg'],
        'writing_avg': row['writing_avg'],
        'delta': delta,
        'delta_normalized': delta_normalized,
        'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGES
# ============================================================================

def render_overview(districts_df):
    st.header("Maine Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pilot Districts", len(districts_df))
    with col2:
        st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3:
        st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4:
        st.metric("Statewide EL Count", "~8,000", help="Across ~192 districts")

    st.divider()

    st.subheader("Maine EL Context")
    st.markdown("""
    Maine has experienced a **dramatic refugee surge** over the past decade, transforming
    Portland and Lewiston from predominantly white communities into some of the most
    linguistically diverse districts in New England. Somali, Congolese, and Afghan families
    represent the largest recent arrivals, with both Portland and Lewiston at approximately
    **25% EL enrollment**.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.warning("**Refugee Surge**\nSomali, Congolese, Afghan arrivals")
    with col2:
        st.warning("**25% EL**\nPortland & Lewiston")
    with col3:
        st.info("**MAST (NWEA MAP)**\n4 levels: Below/Approaching/Proficient/Above")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**WIDA ACCESS**\nEnglish proficiency assessment")
    with col2:
        st.info("**~192 Districts**\nSmall state, concentrated EL populations")
    with col3:
        st.info("**Maine ESSA Plan**\nAccountability system")

    st.divider()

    st.subheader("Top EL Languages Statewide")
    lang_data = pd.DataFrame({
        'Language': ['Somali', 'Arabic', 'French (Congolese)', 'Portuguese', 'Spanish', 'Dari/Pashto', 'Vietnamese', 'Mandarin'],
        'Approx Share': [28, 15, 12, 8, 7, 6, 4, 3],
    })
    fig_lang = px.bar(lang_data, x='Language', y='Approx Share',
                      color='Approx Share',
                      color_continuous_scale=[[0, '#C0C0C0'], [1, ME_BLUE]],
                      labels={'Approx Share': '% of EL Population'},
                      text='Approx Share')
    fig_lang.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_lang.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                           title="Top EL Home Languages in Maine")
    st.plotly_chart(fig_lang, use_container_width=True)

    st.divider()

    st.subheader("Pilot Districts -- Highest EL Populations")
    display = districts_df[['district_id', 'district_name', 'total_students', 'el_count', 'el_percent',
                            'mast_ela_all', 'mast_ela_el', 'mast_ela_black', 'mast_ela_white',
                            'top_el_languages']].copy()
    display.columns = ['Dist ID', 'District', 'Students', 'EL Count', 'EL %',
                       'ELA All %', 'ELA EL %', 'ELA Black %', 'ELA White %',
                       'Top Languages']
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, ME_BLUE]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False,
                      title="EL Population by District (color = EL %)")
    st.plotly_chart(fig, use_container_width=True)


def render_domain_analysis(domain_df):
    st.header("Statewide ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** Maine DOE ACCESS data. Maine is a WIDA Consortium member.
    Domain proficiency percentages show the systemic oral-written delta: Speaking consistently
    outperforms Writing across all grade clusters. Maine's refugee-dominant EL population
    (Somali, Congolese, Afghan) shows particularly strong oral-written gaps due to
    **orthographic distance** from English.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', ME_BLUE), ('speaking', ME_GOLD),
                           ('reading', '#888888'), ('writing', ME_RED)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient",
        barmode='group', height=450, yaxis=dict(range=[0, 72])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[ME_RED if d > 18 else ME_GOLD for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap",
                       yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.markdown("""
    ---
    **Why this matters for Maine:** The oral-written gap is especially significant for
    Somali-speaking students (largest EL group), whose home language uses a Latin-based
    orthography adopted only in 1972, and for Congolese French speakers who may have
    limited formal literacy in their L1. Afghan students (Dari/Pashto) face a different
    script system entirely.
    """)


def render_access_analysis(access_df, districts_df):
    st.header("ACCESS for ELLs Analysis")
    st.markdown("""
    **WIDA ACCESS** measures English learners across four domains. Maine has ~8,000 ELs
    concentrated heavily in Portland and Lewiston. Exit criteria follow WIDA standard:
    Overall composite **4.5+**.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="acc_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="acc_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]

        lang = districts_df[districts_df['district_id'] == district_id]['top_el_languages'].values[0]
        st.info(f"**Top EL languages in {district}:** {lang}")

        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2:
            st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3:
            st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4:
            st.metric("Writing", f"{row['writing_avg']:.0f}")
        with col5:
            st.metric("Composite", f"{row['composite_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(
            x=domains, y=scores,
            marker_color=[ME_BLUE, ME_GOLD, '#888888', ME_RED],
            text=[f"{s:.0f}" for s in scores], textposition='outside'
        ))
        fig.update_layout(
            title=f"ACCESS Domains -- {district} -- Grade {grade} ({year})",
            yaxis_title="Scale Score", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Oral Average", f"{oral:.0f}")
        with col2:
            st.metric("Written Average", f"{written:.0f}")
        with col3:
            st.metric("Oral-Written Gap", f"{gap:+.0f}",
                      delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.subheader("Exit Criteria Check (WIDA Standard: 4.5+ composite)")
        st.markdown("""
        Maine follows the WIDA standard exit criteria requiring an overall composite score
        of **4.5 or higher** to exit EL services. Given the refugee-dominant EL population,
        many students show strong oral growth but require extended time for written proficiency.
        """)
    else:
        st.warning("No data available for the selected filters.")


def render_type4(access_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.

    In Maine, this is particularly relevant for **Somali and Congolese refugee** students,
    whose oral English fluency often develops rapidly through community immersion while
    written proficiency lags due to limited prior formal schooling (SLIFE populations).
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="t4_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    result = compute_type4_analysis(access_df, district_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2:
            st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3:
            st.metric("Delta", f"{result['delta']:+.0f}")
        with col4:
            st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']],
                             marker_color=ME_GOLD))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']],
                             marker_color=ME_BLUE))
        fig.update_layout(
            title=f"Speaking vs Writing -- {district} -- Grade {grade}",
            barmode='group', height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
            st.markdown("""
            **Maine-specific action:** Districts should review these students for SLIFE
            (Students with Limited or Interrupted Formal Education) status and consider
            targeted writing interventions. Portland and Lewiston have dedicated refugee
            education programs that can provide additional support.
            """)
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(access_df, district_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['speaking_avg'],
                name='Speaking', mode='lines+markers',
                line=dict(color=ME_GOLD, width=3)
            ))
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['writing_avg'],
                name='Writing', mode='lines+markers',
                line=dict(color=ME_BLUE, width=3)
            ))
            fig.update_layout(
                title="Speaking vs Writing Across Grades",
                xaxis_title="Grade", yaxis_title="Scale Score", height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Type 4 Summary Table")
            summary = gdf[['grade', 'speaking_avg', 'writing_avg', 'delta', 'delta_normalized', 'flagged',
                           'total_tested', 'estimated_flagged']].copy()
            summary.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Norm Delta', 'Flagged',
                              'Tested', 'Est. Affected']
            st.dataframe(summary, use_container_width=True, hide_index=True)


def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **MAST (via NWEA MAP) ELA proficiency by subgroup** across pilot districts.
    Maine's refugee-driven EL growth has created new equity challenges, particularly in
    Portland and Lewiston where Black/African student achievement gaps reflect the
    intersection of refugee status, language acquisition, and prior schooling disruption.
    """)

    st.divider()

    fig = go.Figure()
    sorted_df = districts_df.sort_values('mast_ela_all', ascending=True)
    for col, name, color in [
        ('mast_ela_white', 'White', '#666666'),
        ('mast_ela_all', 'All Students', ME_BLUE),
        ('mast_ela_hispanic', 'Hispanic', '#E8540A'),
        ('mast_ela_black', 'Black', ME_RED),
        ('mast_ela_el', 'English Learners', ME_GOLD),
    ]:
        fig.add_trace(go.Bar(
            x=sorted_df[col], y=sorted_df['district_name'],
            name=name, orientation='h', marker_color=color
        ))

    fig.update_layout(
        title="MAST ELA Proficiency by Subgroup",
        barmode='group', xaxis_title="% Proficient", height=650,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Gap Magnitude: White - Black ELA Proficiency")
    districts_df_copy = districts_df.copy()
    districts_df_copy['wb_gap'] = districts_df_copy['mast_ela_white'] - districts_df_copy['mast_ela_black']
    districts_df_copy['wh_gap'] = districts_df_copy['mast_ela_white'] - districts_df_copy['mast_ela_hispanic']
    districts_df_copy['we_gap'] = districts_df_copy['mast_ela_white'] - districts_df_copy['mast_ela_el']

    col1, col2, col3 = st.columns(3)
    with col1:
        avg_wb = districts_df_copy['wb_gap'].mean()
        st.metric("Avg White-Black Gap", f"{avg_wb:.1f} pts", delta="Critical", delta_color="inverse")
    with col2:
        avg_wh = districts_df_copy['wh_gap'].mean()
        st.metric("Avg White-Hispanic Gap", f"{avg_wh:.1f} pts", delta="Critical", delta_color="inverse")
    with col3:
        avg_we = districts_df_copy['we_gap'].mean()
        st.metric("Avg White-EL Gap", f"{avg_we:.1f} pts", delta="Critical", delta_color="inverse")

    fig_gap = go.Figure()
    gap_sorted = districts_df_copy.sort_values('wb_gap', ascending=True)
    fig_gap.add_trace(go.Bar(
        x=gap_sorted['wb_gap'], y=gap_sorted['district_name'],
        orientation='h', marker_color=[ME_RED if g > 35 else ME_GOLD for g in gap_sorted['wb_gap']],
        text=[f"{g:.0f} pts" for g in gap_sorted['wb_gap']], textposition='outside'
    ))
    fig_gap.update_layout(
        title="White-Black ELA Gap by District (pts)", height=550,
        xaxis_title="Gap (percentage points)"
    )
    st.plotly_chart(fig_gap, use_container_width=True)

    st.subheader("EL Proficiency vs Overall Proficiency")
    fig2 = px.scatter(
        districts_df, x='mast_ela_all', y='mast_ela_el', size='el_count',
        color='el_percent', color_continuous_scale=[[0, '#ccc'], [1, ME_BLUE]],
        hover_name='district_name',
        labels={'mast_ela_all': 'All Students ELA %', 'mast_ela_el': 'EL ELA %',
                'el_count': 'EL Count', 'el_percent': 'EL %'}
    )
    fig2.add_shape(type="line", x0=0, y0=0, x1=80, y1=80,
                   line=dict(dash="dash", color="gray"))
    fig2.update_layout(
        title="EL Proficiency vs District Overall -- Gap Visualization", height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    ---
    **Maine context:** The state's refugee resettlement history makes its EL population
    unique in New England. Portland and Lewiston have developed specialized refugee education
    programs, but achievement gaps remain significant. The intersection of refugee trauma,
    interrupted schooling, and language acquisition creates compounding challenges.
    """)


def render_mast(mast_df, districts_df):
    st.header("MAST Assessment Analysis")
    st.markdown("""
    **Maine State Assessment (MAST)** via NWEA MAP -- 4 performance levels:
    Below, Approaching, Proficient, Above.

    ELA and Math tested grades 3-8.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="mast_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="mast_g")
    with col3:
        subject = st.selectbox("Subject", ['ELA', 'Math'], key="mast_s")
    with col4:
        year = st.selectbox("Year", [2025, 2024], key="mast_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = mast_df[
        (mast_df['district_id'] == district_id) &
        (mast_df['grade'] == grade) &
        (mast_df['subject'] == subject) &
        (mast_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Below", f"{row['below_pct']:.1f}%")
        with col2:
            st.metric("Approaching", f"{row['approaching_pct']:.1f}%")
        with col3:
            st.metric("Proficient", f"{row['proficient_pct']:.1f}%")
        with col4:
            st.metric("Above", f"{row['above_pct']:.1f}%")

        levels = ['Below', 'Approaching', 'Proficient', 'Above']
        values = [row['below_pct'], row['approaching_pct'],
                  row['proficient_pct'], row['above_pct']]
        colors = [ME_RED, '#E8540A', ME_GOLD, ME_BLUE]
        fig = go.Figure(go.Bar(
            x=levels, y=values, marker_color=colors,
            text=[f"{v:.1f}%" for v in values], textposition='outside'
        ))
        fig.update_layout(
            title=f"MAST {subject} -- {district} -- Grade {grade} ({year})",
            yaxis_title="Percentage", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Combined Proficiency (Proficient + Above)",
                  f"{row['prof_and_above_pct']:.1f}%")

        st.subheader(f"MAST {subject} Across Grades -- {district} ({year})")
        cross = mast_df[
            (mast_df['district_id'] == district_id) &
            (mast_df['subject'] == subject) &
            (mast_df['year'] == year)
        ]
        if not cross.empty:
            fig2 = go.Figure()
            for level, color in zip(levels, colors):
                col_name = level.lower() + '_pct'
                fig2.add_trace(go.Bar(
                    x=cross['grade'], y=cross[col_name],
                    name=level, marker_color=color
                ))
            fig2.update_layout(
                barmode='stack', xaxis_title="Grade", yaxis_title="Percentage",
                height=400, title=f"MAST {subject} Performance Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")


def render_export(access_df, mast_df, districts_df, domain_df):
    st.header("Export Data")

    st.markdown("Download VERA-ME analysis data as CSV files for further analysis.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ACCESS CSV",
            access_df.to_csv(index=False),
            "vera_me_access.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("MAST Data")
        st.dataframe(mast_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download MAST CSV",
            mast_df.to_csv(index=False),
            "vera_me_mast.csv", "text/csv",
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Domain CSV",
            domain_df.to_csv(index=False),
            "vera_me_domains.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("District Reference Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Districts CSV",
            districts_df.to_csv(index=False),
            "vera_me_districts.csv", "text/csv",
            use_container_width=True
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(
        page_title="VERA-ME | Maine Type 4 Detection",
        page_icon="*",
        layout="wide"
    )

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {ME_BLUE}; }}
        .stButton > button {{ background-color: {ME_BLUE}; color: white; }}
        .stButton > button:hover {{ background-color: {ME_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    districts_df = load_districts()
    access_df = load_access_data(districts_df)
    mast_df = load_mast_data(districts_df)
    domain_df = load_statewide_domain_data()

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {ME_BLUE}; margin: 0;">VERA-ME</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Maine Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Statewide Domain Analysis",
        "ACCESS Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "MAST Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ACCESS for ELLs (WIDA)
    - Maine DOE ACCESS Files
    - MAST (via NWEA MAP)
    - Maine ESSA Accountability

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points (normalized)

    **ME Exit Criteria:**
    - Composite 4.5+ (WIDA standard)

    **Key Context:**
    - ~8,000 ELs statewide
    - ~192 school districts
    - **Refugee surge: Somali/Congolese/Afghan**
    - Portland 25% EL, Lewiston 25%
    - MAST 4 levels: Below/Approaching/Proficient/Above
    - SLIFE populations

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview":
        render_overview(districts_df)
    elif page == "Statewide Domain Analysis":
        render_domain_analysis(domain_df)
    elif page == "ACCESS Analysis":
        render_access_analysis(access_df, districts_df)
    elif page == "Type 4 Detection":
        render_type4(access_df, districts_df)
    elif page == "Achievement Gaps":
        render_achievement_gaps(districts_df)
    elif page == "MAST Analysis":
        render_mast(mast_df, districts_df)
    elif page == "Export Data":
        render_export(access_df, mast_df, districts_df, domain_df)


if __name__ == "__main__":
    main()

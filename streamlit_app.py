import json
from typing import Dict
from dataclasses import dataclass

import streamlit as st

# ─── Data Classes & Calculator Logic ──────────────────────────────────────────

@dataclass
class RiskScores:
    operational: float
    technical: float
    climate: float
    overall: float

class SolarRiskCalculator:
    def __init__(self):
        # Risk category weights
        self.weights = {
            "operational": 0.30,
            "technical": 0.40,
            "climate": 0.30,
        }

        # Operational risk factor weights
        self.operational_weights = {
            "grid_connection": 0.30,
            "om_provider": 0.25,
            "regulatory": 0.25,
            "site_access": 0.20,
        }

        # Technical risk factor weights
        self.technical_weights = {
            "panel_tech": 0.25,
            "inverter_tech": 0.25,
            "system_design": 0.25,
            "installation": 0.25,
        }

        # Climate risk factor weights
        self.climate_weights = {
            "weather_variability": 0.35,
            "extreme_weather": 0.35,
            "resource_stability": 0.30,
        }

    def calculate_risk_scores(
        self,
        operational: Dict[str, int],
        technical: Dict[str, int],
        climate: Dict[str, int],
    ) -> RiskScores:
        """Calculate weighted risk scores."""
        op_score = sum(
            operational[f] * self.operational_weights[f] for f in operational
        )
        tech_score = sum(
            technical[f] * self.technical_weights[f] for f in technical
        )
        climate_score = sum(
            climate[f] * self.climate_weights[f] for f in climate
        )
        overall_score = (
            op_score * self.weights["operational"]
            + tech_score * self.weights["technical"]
            + climate_score * self.weights["climate"]
        )
        return RiskScores(
            operational=op_score,
            technical=tech_score,
            climate=climate_score,
            overall=overall_score,
        )

    def get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level."""
        if score >= 4.5:
            return "VERY LOW RISK"
        elif score >= 3.5:
            return "LOW RISK"
        elif score >= 2.5:
            return "MEDIUM RISK"
        elif score >= 1.5:
            return "HIGH RISK"
        else:
            return "VERY HIGH RISK"

    def get_risk_color(self, score: float) -> str:
        """Return an emoji-based color indicator."""
        if score >= 4.5:
            return "🟢"
        elif score >= 3.5:
            return "🟡"
        elif score >= 2.5:
            return "🟠"
        elif score >= 1.5:
            return "🔴"
        else:
            return "⚫"

    def risk_interpretation(self, overall: float) -> str:
        """Return interpretative text based on overall score."""
        if overall >= 4.0:
            return "✅ Excellent risk profile. Very attractive investment."
        elif overall >= 3.0:
            return "✅ Good risk profile. Solid investment opportunity."
        elif overall >= 2.0:
            return "⚠️  Moderate risk. Consider risk mitigation strategies."
        else:
            return "❌ High risk profile. Significant concerns identified."

    def recommendations(self, scores: RiskScores) -> str:
        """Generate simple recommendations based on sub-scores."""
        recs = []
        if scores.operational < 3.0:
            recs.append(
                "🔧 **Operational:** Consider upgrading O&M provider or improving grid connection."
            )
        if scores.technical < 3.0:
            recs.append(
                "⚙️  **Technical:** Review equipment selection and contractor experience."
            )
        if scores.climate < 3.0:
            recs.append(
                "🌦️  **Climate:** Evaluate insurance options and weather risk mitigation."
            )
        return "\n\n".join(recs) if recs else "No specific recommendations—sub-scores are all ≥ 3.0."


# ─── Streamlit App “Wizard” ───────────────────────────────────────────────────

st.set_page_config(page_title="Sunereum Solar Risk Calculator", layout="wide")
st.title("🔆 Sunereum Solar Risk Calculator")

calculator = SolarRiskCalculator()

# Initialize “step” in session state if not already there
if "step" not in st.session_state:
    st.session_state.step = 0

# Show progress indicator
total_steps = 6  # Profile, Site, Operational, Technical, Climate, Results
st.markdown(f"**Step {st.session_state.step + 1} of {total_steps}**")


# ─── Utility to move forward ───────────────────────────────────────────────────
def _go_to_next():
    st.session_state.step += 1


# ───— Step 0: Profile (Name & Email) ───────────────────────────────────────────
if st.session_state.step == 0:
    st.header("👤 1. User Profile")
    st.markdown("Please enter your name and email to proceed.")

    # Bind to session_state so values persist across reruns
    name = st.text_input("Name", key="profile_name")
    email = st.text_input("Email Address", key="profile_email")

    # “Next” button (only advances when valid)
    if st.button("Next ➡️", key="next_profile"):
        if not name.strip() or not email.strip():
            st.warning("Please fill in both **Name** and **Email** to continue.")
        else:
            _go_to_next()


# ───— Step 1: Site Information ────────────────────────────────────────────────
elif st.session_state.step == 1:
    st.header("🏷️ 2. Site Information")
    st.markdown("Provide basic details about the solar site. “Site Name” and “Location” are required.")

    site_name = st.text_input("Site Name", key="site_name")
    location = st.text_input("Location (City, State)", key="location")
    capacity_mw = st.number_input(
        "Capacity (MW)", min_value=0.0, step=0.1, value=0.0, key="capacity_mw"
    )
    cod_year = st.number_input(
        "Commercial Operation Date (Year)",
        min_value=1900,
        max_value=2100,
        value=2024,
        key="cod_year",
    )

    if st.button("Next ➡️", key="next_site"):
        if not site_name.strip() or not location.strip():
            st.warning("Please fill in both **Site Name** and **Location** to continue.")
        else:
            _go_to_next()


# ───— Step 2: Operational Risk Factors ─────────────────────────────────────────
elif st.session_state.step == 2:
    st.header("⚙️ 3. Operational Risk Factors")
    st.markdown("Rate each factor from 1 (worst) to 5 (best). Once you’re satisfied, click Next.")

    grid_connection = st.slider(
        "Grid Connection",
        min_value=1,
        max_value=5,
        value=3,
        key="grid_connection",
        help="""
        5: Direct connection to major transmission  
        4: Strong distribution network connection  
        3: Standard grid, occasional constraints  
        2: Weak grid, regular curtailment  
        1: Remote/unstable grid, frequent outages
        """,
    )
    om_provider = st.slider(
        "O&M Provider Experience",
        min_value=1,
        max_value=5,
        value=3,
        key="om_provider",
        help="""
        5: Tier 1 provider (Fluence, First Solar, etc.)  
        4: Established regional provider (5+ years)  
        3: Mid-tier provider, decent track record  
        2: New provider or limited solar experience  
        1: Self-operated or unproven contractor
        """,
    )
    regulatory = st.slider(
        "Regulatory Environment",
        min_value=1,
        max_value=5,
        value=3,
        key="regulatory",
        help="""
        5: Streamlined permitting, supportive policies  
        4: Standard regulatory process  
        3: Moderate bureaucracy, some delays  
        2: Complex permitting, changing regulations  
        1: Hostile regulatory environment
        """,
    )
    site_access = st.slider(
        "Site Accessibility",
        min_value=1,
        max_value=5,
        value=3,
        key="site_access",
        help="""
        5: Easy road access, near population centers  
        4: Good access roads, moderate distance  
        3: Standard rural access  
        2: Difficult terrain or remote location  
        1: Very remote, challenging logistics
        """,
    )

    if st.button("Next ➡️", key="next_operational"):
        # sliders always have a value 1–5, so we consider them “filled”
        _go_to_next()


# ───— Step 3: Technical Risk Factors ──────────────────────────────────────────
elif st.session_state.step == 3:
    st.header("🔧 4. Technical Risk Factors")
    st.markdown("Rate each factor from 1 (worst) to 5 (best). When ready, click Next.")

    panel_tech = st.slider(
        "Panel Technology",
        min_value=1,
        max_value=5,
        value=3,
        key="panel_tech",
        help="""
        5: Tier 1 proven tech (JinkoSolar, LONGi, etc.)  
        4: Tier 1 with newer technology  
        3: Tier 2 established manufacturer  
        2: Tier 2 or newer technology  
        1: Unproven manufacturer or cutting-edge tech
        """,
    )
    inverter_tech = st.slider(
        "Inverter Technology",
        min_value=1,
        max_value=5,
        value=3,
        key="inverter_tech",
        help="""
        5: Tier 1 inverters (SMA, ABB, SolarEdge, etc.)  
        4: Established power electronics  
        3: Mid-tier proven technology  
        2: Newer technology or manufacturer  
        1: Unproven or experimental systems
        """,
    )
    system_design = st.slider(
        "System Design Complexity",
        min_value=1,
        max_value=5,
        value=3,
        key="system_design",
        help="""
        5: Simple fixed-tilt ground mount  
        4: Single-axis tracking, standard design  
        3: Complex tracking or mounting systems  
        2: Challenging site conditions (slopes, etc.)  
        1: Experimental design or extreme conditions
        """,
    )
    installation = st.slider(
        "Installation Quality",
        min_value=1,
        max_value=5,
        value=3,
        key="installation",
        help="""
        5: Tier 1 EPC contractor with proven record  
        4: Experienced regional EPC  
        3: Standard EPC contractor  
        2: Limited solar experience  
        1: New contractor or self-built
        """,
    )

    if st.button("Next ➡️", key="next_technical"):
        _go_to_next()


# ───— Step 4: Climate Risk Factors ─────────────────────────────────────────────
elif st.session_state.step == 4:
    st.header("🌦️ 5. Climate Risk Factors")
    st.markdown("Rate each factor from 1 (worst) to 5 (best). Then click Next.")

    weather_variability = st.slider(
        "Weather Variability",
        min_value=1,
        max_value=5,
        value=3,
        key="weather_variability",
        help="""
        5: Very stable climate (Phoenix, Las Vegas)  
        4: Generally stable with some variation  
        3: Moderate seasonal/yearly variation  
        2: Significant weather variability  
        1: Highly unpredictable climate patterns
        """,
    )
    extreme_weather = st.slider(
        "Extreme Weather Risk",
        min_value=1,
        max_value=5,
        value=3,
        key="extreme_weather",
        help="""
        5: Minimal extreme weather risk  
        4: Occasional severe weather  
        3: Moderate hail/wind/storm risk  
        2: Regular extreme weather events  
        1: High hurricane/tornado/severe hail risk
        """,
    )
    resource_stability = st.slider(
        "Long-term Resource Stability",
        min_value=1,
        max_value=5,
        value=3,
        key="resource_stability",
        help="""
        5: Consistent solar resource over decades  
        4: Very stable with minor variations  
        3: Generally stable solar resource  
        2: Some climate change impacts expected  
        1: Significant long-term uncertainty
        """,
    )

    if st.button("Next ➡️", key="next_climate"):
        _go_to_next()


# ───— Step 5: Results ──────────────────────────────────────────────────────────
elif st.session_state.step == 5:
    st.header("📊 6. Risk Assessment Results")

    # Gather everything from session_state
    name = st.session_state.profile_name
    email = st.session_state.profile_email
    site_name = st.session_state.site_name
    location = st.session_state.location
    capacity_mw = st.session_state.capacity_mw
    cod_year = st.session_state.cod_year

    operational_inputs = {
        "grid_connection": st.session_state.grid_connection,
        "om_provider": st.session_state.om_provider,
        "regulatory": st.session_state.regulatory,
        "site_access": st.session_state.site_access,
    }
    technical_inputs = {
        "panel_tech": st.session_state.panel_tech,
        "inverter_tech": st.session_state.inverter_tech,
        "system_design": st.session_state.system_design,
        "installation": st.session_state.installation,
    }
    climate_inputs = {
        "weather_variability": st.session_state.weather_variability,
        "extreme_weather": st.session_state.extreme_weather,
        "resource_stability": st.session_state.resource_stability,
    }

    # Compute scores
    scores = calculator.calculate_risk_scores(
        operational_inputs, technical_inputs, climate_inputs
    )

    # Display user + site info
    st.subheader("📝 User & Site Info")
    st.markdown(f"**Name:** {name}")
    st.markdown(f"**Email:** {email}")
    st.markdown(f"**Site Name:** {site_name}")
    st.markdown(f"**Location:** {location}")
    st.markdown(f"**Capacity (MW):** {capacity_mw:.2f}")
    st.markdown(f"**COD Year:** {cod_year}")

    st.markdown("---")
    st.subheader("📈 Risk Scores")

    # Four columns: Category, Score, Level, Indicator
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**Category**")
        st.markdown("Operational")
        st.markdown("Technical")
        st.markdown("Climate")
        st.markdown("Overall")
    with col2:
        st.markdown("**Score**")
        st.markdown(f"{scores.operational:.2f}")
        st.markdown(f"{scores.technical:.2f}")
        st.markdown(f"{scores.climate:.2f}")
        st.markdown(f"{scores.overall:.2f}")
    with col3:
        st.markdown("**Level**")
        st.markdown(calculator.get_risk_level(scores.operational))
        st.markdown(calculator.get_risk_level(scores.technical))
        st.markdown(calculator.get_risk_level(scores.climate))
        st.markdown(calculator.get_risk_level(scores.overall))
    with col4:
        st.markdown("**Indicator**")
        st.markdown(calculator.get_risk_color(scores.operational))
        st.markdown(calculator.get_risk_color(scores.technical))
        st.markdown(calculator.get_risk_color(scores.climate))
        st.markdown(calculator.get_risk_color(scores.overall))

    st.markdown("---")
    st.subheader("🔍 Interpretation")
    st.markdown(calculator.risk_interpretation(scores.overall))

    st.markdown("---")
    st.subheader("🛠️ Recommendations")
    st.markdown(calculator.recommendations(scores), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("💾 Export to JSON")
    filename = f"{site_name.replace(' ', '_')}_risk_assessment.json"
    payload = {
        "user": {"name": name, "email": email},
        "site_info": {
            "site_name": site_name,
            "location": location,
            "capacity_mw": capacity_mw,
            "cod_year": cod_year,
        },
        "risk_scores": {
            "operational": scores.operational,
            "technical": scores.technical,
            "climate": scores.climate,
            "overall": scores.overall,
        },
        "risk_levels": {
            "operational": calculator.get_risk_level(scores.operational),
            "technical": calculator.get_risk_level(scores.technical),
            "climate": calculator.get_risk_level(scores.climate),
            "overall": calculator.get_risk_level(scores.overall),
        },
    }
    json_str = json.dumps(payload, indent=2)
    st.download_button(
        label="⬇️ Download Results as JSON",
        data=json_str,
        file_name=filename,
        mime="application/json",
        key="download_json",
    )

    # Optional: allow user to restart the wizard
    if st.button("🔄 Start Over", key="restart"):
        # Reset everything
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.step = 0
        st.experimental_rerun()

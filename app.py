import pandas as pd
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="ESG Supply Chain Risk Dashboard", layout="wide"
)

st.title("🌱 Enterprise ESG Supply Chain Risk & Compliance Dashboard")
st.markdown(
    "A decision-support tool for evaluating tier-1 supplier sustainability and"
    " regulatory risk."
)

# 2. Initial Supplier Dataset in Session State (Core metrics out of 100)
if "supplier_data" not in st.session_state:
  st.session_state.supplier_data = pd.DataFrame({
      "Supplier_ID": ["SUP_001", "SUP_002", "SUP_003", "SUP_004", "SUP_005"],
      "Supplier_Name": [
          "Apex Textiles Ltd.",
          "Vanguard Garments",
          "EcoThread Solutions",
          "Metro Dyeing Works",
          "Highland Weavers",
      ],
      "Location": ["India", "Bangladesh", "Vietnam", "India", "Pakistan"],
      "Category": [
          "Cotton Fabric",
          "Denim",
          "Organic Cotton",
          "Synthetic Dyes",
          "Wool & Cashmere",
      ],
      "Carbon_Footprint_Score": [75, 45, 90, 30, 65],
      "Waste_Management_Score": [80, 50, 95, 40, 70],
      "Labor_Wages_Score": [85, 60, 92, 45, 75],
      "Governance_Score": [90, 55, 88, 50, 80],
  })

# 3. Form-Based Live Data Editor
st.subheader("📝 Live Supplier Data Editor")
st.markdown(
    "Edit any scores (all rated out of 100) or add a new supplier row at the"
    " bottom, then click **'Save & Update Dashboard'**."
)

with st.form("editor_form"):
  edited_df = st.data_editor(
      st.session_state.supplier_data, num_rows="dynamic", key="grid_editor"
  )
  submit_button = st.form_submit_button("💾 Save & Update Dashboard")

if submit_button:
  st.session_state.supplier_data = edited_df
  st.success("Dashboard updated successfully!")

# 4. Automatic Calculation (All normalized / weighted out of 100)
df = st.session_state.supplier_data.copy()

# Environmental Sub-Score (Average of Carbon and Waste, both out of 100)
df["Environmental_Score"] = (
    df["Carbon_Footprint_Score"] + df["Waste_Management_Score"]
) / 2

# Social & Governance Sub-Score (Average of Labor and Governance, both out of 100)
df["Social_Governance_Score"] = (
    df["Labor_Wages_Score"] + df["Governance_Score"]
) / 2

# Total ESG Score (Weighted: 40% Environmental, 60% Social & Governance, final out of 100)
df["Total_ESG_Score"] = round(
    (df["Environmental_Score"] * 0.40)
    + (df["Social_Governance_Score"] * 0.60),
    2,
)


# 5. Risk Categorization Logic
def assign_risk(score):
  if score >= 80:
    return "Low Risk (Preferred)"
  elif score >= 50:
    return "Medium Risk (Audit Needed)"
  else:
    return "High Risk (Action Required)"


df["Risk_Category"] = df["Total_ESG_Score"].apply(assign_risk)

# 6. Dashboard Sidebar Filters
st.sidebar.header("Filter Suppliers")
locations = ["All"] + list(df["Location"].dropna().unique())
selected_location = st.sidebar.selectbox("Select Location", options=locations)

if selected_location != "All":
  df_filtered = df[df["Location"] == selected_location]
else:
  df_filtered = df

# 7. Display Key Metrics at the Top
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Total Suppliers Tracked", len(df_filtered))
avg_score = (
    round(df_filtered["Total_ESG_Score"].mean(), 2)
    if not df_filtered.empty
    else 0
)
col2.metric("Average ESG Score", avg_score)
high_risk_count = len(
    df_filtered[df_filtered["Risk_Category"].str.contains("High Risk", na=False)]
)
col3.metric("High-Risk Suppliers", high_risk_count)

# 8. Main Evaluated Matrix Display
st.subheader("Evaluated Supplier ESG Risk Matrix (All Scores Out of 100)")
st.dataframe(df_filtered)

# 9. Visual Breakdown
st.subheader("Supplier Risk Distribution")
if not df_filtered.empty:
  risk_counts = df_filtered["Risk_Category"].value_counts()
  st.bar_chart(risk_counts)
else:
  st.info("No data available to display chart.")
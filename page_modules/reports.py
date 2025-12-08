"""
Reports and Actionable Recommendations Page
Generate insights, action plans, and export data
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.kpi_calculator import calculate_country_kpis
from fpdf import FPDF


def build_report_pdf(
    report_title: str,
    selected_country: str,
    selected_domain: str,
    report_type: str,
    include_charts: bool,
    include_recommendations: bool,
    include_trends: bool,
    include_comparisons: bool,
    notes: str,
    performance_df: pd.DataFrame
) -> bytes:
    """Create a downloadable PDF summary based on the selected configuration."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    content_width = pdf.w - 2 * pdf.l_margin

    # === HEADER SECTION ===
    pdf.set_fill_color(28, 107, 160)  # Primary blue
    pdf.rect(10, 10, 190, 35, 'F')
    
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(15, 18)
    pdf.cell(0, 10, report_title, ln=False)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 32)
    pdf.cell(0, 6, f"Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %H:%M')}", ln=False)
    
    pdf.set_text_color(0, 0, 0)  # Back to black
    pdf.ln(40)

    # === REPORT METADATA ===
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Report Configuration", ln=True)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(50, 7, "Report Type:", 0)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, report_type, ln=True)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(50, 7, "Country Scope:", 0)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, selected_country, ln=True)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(50, 7, "Domain Focus:", 0)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, selected_domain, ln=True)
    pdf.ln(5)

    # === PERFORMANCE SNAPSHOT ===
    if not performance_df.empty:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, "Performance Snapshot", ln=True, fill=True)
        pdf.ln(2)
        
        # Table header
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(28, 107, 160)
        pdf.set_text_color(255, 255, 255)
        
        col_widths = [35, 22, 22, 22, 22, 30, 27]
        headers = ["Country", "Water %", "Sanit. %", "NRW %", "OCCR %", "Collection %", "Status"]
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Table data
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        
        for idx, row in performance_df.iterrows():
            # Determine overall status
            avg_score = (row['Water Coverage'] + row['Sanitation Coverage'] + 
                        (100 - row['NRW']) + row['OCCR'] + row['Collection Efficiency']) / 5
            
            if avg_score >= 70:
                status = "Good"
                color = (76, 175, 80)  # Green
            elif avg_score >= 50:
                status = "Acceptable"
                color = (255, 152, 0)  # Orange
            else:
                status = "Needs Attention"
                color = (244, 67, 54)  # Red
            
            # Alternating row colors
            if idx % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(245, 245, 245)
            
            pdf.cell(col_widths[0], 7, str(row['Country'])[:30], 1, 0, 'L', fill=True)
            pdf.cell(col_widths[1], 7, f"{row['Water Coverage']:.1f}", 1, 0, 'C', fill=True)
            pdf.cell(col_widths[2], 7, f"{row['Sanitation Coverage']:.1f}", 1, 0, 'C', fill=True)
            pdf.cell(col_widths[3], 7, f"{row['NRW']:.1f}", 1, 0, 'C', fill=True)
            pdf.cell(col_widths[4], 7, f"{row['OCCR']:.1f}", 1, 0, 'C', fill=True)
            pdf.cell(col_widths[5], 7, f"{row['Collection Efficiency']:.1f}", 1, 0, 'C', fill=True)
            
            # Status cell with color
            pdf.set_fill_color(color[0], color[1], color[2])
            pdf.set_text_color(255, 255, 255)
            pdf.cell(col_widths[6], 7, status, 1, 0, 'C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln()
        
        pdf.ln(5)

    # === KEY METRICS EXPLANATION ===
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "Key Performance Indicators", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 10)
    kpis = [
        ("Water Coverage", "Percentage of population with access to improved water sources", ">=80%"),
        ("Sanitation Coverage", "Percentage of population with access to improved sanitation", ">=80%"),
        ("Non-Revenue Water (NRW)", "Water losses due to leaks, theft, or metering inaccuracies", "<=25%"),
        ("O&M Cost Coverage (OCCR)", "Operating revenue as a percentage of O&M expenses", ">=100%"),
        ("Collection Efficiency", "Percentage of billed revenue successfully collected", ">=90%"),
    ]
    
    for kpi_name, description, benchmark in kpis:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"{kpi_name} (Target: {benchmark})", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(content_width, 5, description)
        pdf.ln(2)
    
    pdf.ln(3)

    # === TREND ANALYSIS ===
    if include_trends:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, "Trend Analysis", ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(
            content_width,
            6,
            "Performance trends reveal key patterns over time. Review the dashboard's interactive charts "
            "for detailed year-over-year comparisons, seasonal patterns, and forecasts."
        )
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Focus Areas:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        trends = [
            "Monitor NRW trends - decreasing values indicate improved leak management",
            "Track OCCR progression - values approaching 100% signal better cost recovery",
            "Observe coverage expansion rates in underserved regions",
            "Identify seasonal patterns affecting service delivery and revenue"
        ]
        for trend in trends:
            pdf.multi_cell(content_width, 5, f"  - {trend}")
        pdf.ln(3)

    # === CROSS-COUNTRY COMPARISONS ===
    if include_comparisons:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, "Cross-Country Comparisons", ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(
            content_width,
            6,
            "Comparative analysis identifies best performers and areas for knowledge exchange. "
            "Countries showing strong performance in specific indicators can serve as models for others."
        )
        pdf.ln(2)
        
        if not performance_df.empty and len(performance_df) > 1:
            # Find leaders (with safety checks for idxmax/idxmin)
            try:
                best_water = performance_df.loc[performance_df['Water Coverage'].idxmax()]
                best_nrw = performance_df.loc[performance_df['NRW'].idxmin()]
                best_occr = performance_df.loc[performance_df['OCCR'].idxmax()]
                
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, "Performance Leaders:", ln=True)
                pdf.set_font("Helvetica", "", 10)
                
                pdf.multi_cell(content_width, 5, 
                    f"  - Water Coverage: {best_water['Country']} ({best_water['Water Coverage']:.1f}%)")
                pdf.multi_cell(content_width, 5,
                    f"  - NRW Management: {best_nrw['Country']} ({best_nrw['NRW']:.1f}%)")
                pdf.multi_cell(content_width, 5,
                    f"  - Cost Recovery: {best_occr['Country']} ({best_occr['OCCR']:.1f}%)")
            except (ValueError, KeyError):
                # Handle case where data is insufficient for comparison
                pdf.set_font("Helvetica", "I", 10)
                pdf.multi_cell(content_width, 5, "Insufficient data for performance comparison.")
        
        pdf.ln(3)

    # === ACTIONABLE RECOMMENDATIONS ===
    if include_recommendations:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, "Priority Recommendations", ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "", 10)
        recommendations = [
            {
                "title": "1. Reduce Non-Revenue Water",
                "actions": [
                    "Deploy smart meters and pressure management systems",
                    "Implement district metered areas (DMAs) for leak detection",
                    "Train staff on active leak detection and rapid response"
                ]
            },
            {
                "title": "2. Improve Revenue Collection",
                "actions": [
                    "Introduce mobile payment options and automated billing",
                    "Implement payment reminders and disconnection policies",
                    "Establish customer service centers in underserved areas"
                ]
            },
            {
                "title": "3. Expand Service Coverage",
                "actions": [
                    "Prioritize pro-poor connections and subsidies",
                    "Develop masterplans for peri-urban and rural expansion",
                    "Partner with communities for last-mile infrastructure"
                ]
            },
            {
                "title": "4. Enhance Cost Recovery (OCCR)",
                "actions": [
                    "Review tariff structures to ensure they cover O&M costs",
                    "Reduce operational inefficiencies through energy audits",
                    "Diversify revenue streams (e.g., bulk sales, sanitation services)"
                ]
            }
        ]
        
        for rec in recommendations:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, rec["title"], ln=True)
            pdf.set_font("Helvetica", "", 9)
            for action in rec["actions"]:
                pdf.multi_cell(content_width, 5, f"   - {action}")
            pdf.ln(2)
        
        pdf.ln(3)

    # === STAKEHOLDER NOTES ===
    if notes:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, "Stakeholder Notes", ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "", 10)
        for line in notes.splitlines():
            pdf.multi_cell(content_width, 6, line if line.strip() else " ")
        pdf.ln(3)

    # === FOOTER ===
    pdf.ln(5)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(content_width, 5, 
        "Generated via WASH Performance Dashboard | "
        "For interactive analysis and real-time updates, visit the dashboard.")

    # fpdf2 returns bytearray, convert to bytes for Streamlit
    pdf_output = pdf.output()
    if isinstance(pdf_output, bytearray):
        pdf_bytes = bytes(pdf_output)
    else:
        pdf_bytes = pdf_output
    return pdf_bytes


def render_reports_page(data, countries_filter, date_range=None):
    """Render the reports and recommendations page"""
    
    st.title("📊 Actionable Reports & Recommendations")
    st.markdown("### Generate insights, action plans, and export data")
    
    st.markdown("---")
    
    # Filter selection
    st.header("🔧 Report Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        report_country = st.selectbox(
            "Select Country",
            ["All Countries"] + (countries_filter if countries_filter else 
                                list(data['production']['country'].unique())),
            help="Choose country for detailed report"
        )
    
    with col2:
        report_domain = st.selectbox(
            "Select Domain",
            ["All Domains", "Production", "Service", "Access", "Finance"],
            help="Focus area for the report"
        )
    
    with col3:
        report_type = st.selectbox(
            "Report Type",
            ["Executive Summary", "Detailed Analysis", "Action Plan"],
            help="Type of report to generate"
        )
    
    st.markdown("---")
    
    # Top Performers and Priority Actions
    st.header("🏆 Performance Rankings")
    
    # Determine countries to include based on sidebar filters and report selection
    available_countries = list(data['production']['country'].unique())
    if countries_filter:
        selected_countries = [c for c in countries_filter if c in available_countries]
    else:
        selected_countries = available_countries.copy()

    if report_country != "All Countries" and report_country in available_countries:
        selected_countries = [report_country]

    # Calculate KPIs for selected countries
    if not selected_countries:
        st.warning("No countries available for the current filter selection. Adjust the filters to continue.")
        return

    performance_data = []
    for country in selected_countries:
        kpis = calculate_country_kpis(data, country)
        performance_data.append({
            'Country': country,
            'Water Coverage': kpis['water_service_coverage'],
            'Sanitation Coverage': kpis['sanitation_coverage'],
            'NRW': kpis['nrw'],
            'OCCR': kpis['cost_recovery_ratio'],
            'Collection Efficiency': kpis['collection_efficiency']
        })
    
    performance_df = pd.DataFrame(performance_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Top Performers")
        
        if not performance_df.empty and len(performance_df) > 0:
            # Best in water coverage (with safety check)
            top_water_df = performance_df.nlargest(1, 'Water Coverage')
            if not top_water_df.empty:
                top_water = top_water_df.iloc[0]
                st.success(f"""
                **🥇 Best Water Coverage:** {top_water['Country']}  
                **Coverage:** {top_water['Water Coverage']:.1f}%
                
                *Best practices to replicate across other countries*
                """)
            
            # Best OCCR (with safety check)
            top_occr_df = performance_df.nlargest(1, 'OCCR')
            if not top_occr_df.empty:
                top_occr = top_occr_df.iloc[0]
                st.success(f"""
                **💰 Best Cost Recovery:** {top_occr['Country']}  
                **OCCR:** {top_occr['OCCR']:.1f}%
                
                *Financial sustainability model for others to follow*
                """)
            
            # Best collection efficiency (with safety check)
            top_coll_df = performance_df.nlargest(1, 'Collection Efficiency')
            if not top_coll_df.empty:
                top_coll = top_coll_df.iloc[0]
                st.success(f"""
                **💵 Best Collection Efficiency:** {top_coll['Country']}  
            **Efficiency:** {top_coll['Collection Efficiency']:.1f}%
            
            *Strong revenue collection practices*
            """)
    
    with col2:
        st.subheader("⚠️ Priority Action Items")
        
        if not performance_df.empty:
            # Show alerts for metrics below benchmark (factual data only)
            high_nrw = performance_df[performance_df['NRW'] > 25]
            if len(high_nrw) > 0:
                st.caption(f"⚠️ {len(high_nrw)} countries with NRW > 25%")
            
            low_occr = performance_df[performance_df['OCCR'] < 110]
            if len(low_occr) > 0:
                st.caption(f"⚠️ {len(low_occr)} countries with OCCR < 110%")
            
            low_coverage = performance_df[performance_df['Water Coverage'] < 80]
            if len(low_coverage) > 0:
                st.caption(f"⚠️ {len(low_coverage)} countries with Water Coverage < 80%")
    
    st.markdown("---")
    
    # Domain Status Summary (factual data only)
    st.header("📋 Domain Status Summary")
    
    # Production Domain Status
    with st.expander("🏭 Production Domain"):
        production_df = data['production']
        if countries_filter:
            production_df = production_df[production_df['country'].isin(countries_filter)]
        
        avg_service_hours = production_df['service_hours'].mean()
        sources_below_benchmark = len(production_df[production_df['service_hours'] < 20])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Service Hours", f"{avg_service_hours:.1f} hrs/day", delta="Benchmark: ≥20 hrs")
        with col2:
            st.metric("Sources Below Benchmark", sources_below_benchmark)
    
    # Service Domain Status
    with st.expander("🚰 Service Domain"):
        w_service = data['w_service']
        if countries_filter:
            w_service = w_service[w_service['country'].isin(countries_filter)]
        
        chlorine_rate = (w_service['test_passed_chlorine'].sum() / 
                        w_service['tests_conducted_chlorine'].sum() * 100) if w_service['tests_conducted_chlorine'].sum() > 0 else 0
        metering_rate = (w_service['metered'].sum() / 
                        w_service['total_consumption'].sum() * 100) if w_service['total_consumption'].sum() > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Water Quality Compliance", f"{chlorine_rate:.1f}%", delta="Benchmark: ≥95%")
        with col2:
            st.metric("Metering Ratio", f"{metering_rate:.1f}%", delta="Benchmark: ≥95%")
    
    # Access Domain Status
    with st.expander("🌍 Access Domain"):
        w_access = data['w_access']
        if countries_filter:
            w_access = w_access[w_access['country'].isin(countries_filter)]
        
        latest_year = w_access['year'].max()
        w_access_latest = w_access[w_access['year'] == latest_year]
        
        avg_coverage = ((w_access_latest['safely_managed'].sum() + 
                        w_access_latest['basic'].sum()) / 
                       w_access_latest['popn_total'].sum() * 100) if w_access_latest['popn_total'].sum() > 0 else 0
        underserved_zones = len(w_access_latest[
            ((w_access_latest['safely_managed'] + w_access_latest['basic']) / 
             w_access_latest['popn_total'].replace({0: np.nan}) * 100) < 50
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Water Coverage", f"{avg_coverage:.1f}%", delta="Target: 100%")
        with col2:
            st.metric("Zones with <50% Coverage", underserved_zones)
    
    # Finance Domain Status
    with st.expander("💰 Finance Domain"):
        finance = data['finance']
        if countries_filter:
            finance = finance[finance['country'].isin(countries_filter)]
        
        avg_occr = ((finance['sewer_revenue'].sum() / finance['opex'].sum()) * 100) if finance['opex'].sum() > 0 else 0
        collection_eff = ((finance['sewer_revenue'].sum() / 
                          finance['sewer_billed'].sum()) * 100) if finance['sewer_billed'].sum() > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average OCCR", f"{avg_occr:.1f}%", delta="Benchmark: ≥110%")
        with col2:
            st.metric("Collection Efficiency", f"{collection_eff:.1f}%", delta="Benchmark: ≥95%")
    
    st.markdown("---")
    
    # Data Export Section
    st.header("📥 Export Data")
    
    st.markdown("Download data for further analysis in Excel or other tools")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Performance Summary"):
            csv = performance_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="performance_summary.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("💧 Export Production Data"):
            production_export = data['production']
            if countries_filter:
                production_export = production_export[production_export['country'].isin(countries_filter)]
            
            csv = production_export.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="production_data.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("💰 Export Financial Data"):
            finance_export = data['finance']
            if countries_filter:
                finance_export = finance_export[finance_export['country'].isin(countries_filter)]
            
            csv = finance_export.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="financial_data.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    # Generate Custom Report
    st.header("📄 Generate Custom Report")
    
    with st.form("custom_report_form"):
        st.markdown("### Report Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_charts = st.checkbox("Include visualizations", value=True)
            include_recommendations = st.checkbox("Include recommendations", value=True)
        
        with col2:
            include_trends = st.checkbox("Include trend analysis", value=True)
            include_comparisons = st.checkbox("Include cross-country comparisons", value=True)
        
        report_title = st.text_input("Report Title", "Water Services Performance Report")
        report_notes = st.text_area("Additional Notes", "")
        
        submit_button = st.form_submit_button("Generate Report")
    
    # Download button OUTSIDE the form
    if submit_button:
        pdf_buffer = build_report_pdf(
            report_title=report_title,
            selected_country=report_country,
            selected_domain=report_domain,
            report_type=report_type,
            include_charts=include_charts,
            include_recommendations=include_recommendations,
            include_trends=include_trends,
            include_comparisons=include_comparisons,
            notes=report_notes,
            performance_df=performance_df
        )

        st.success("✅ Report generated successfully! Click below to download.")
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name=f"{report_title.replace(' ', '_').lower()}.pdf",
            mime="application/pdf"
        )
    


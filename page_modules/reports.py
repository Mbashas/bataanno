"""
Reports and Actionable Recommendations Page
Generate insights, action plans, and export data
"""

import streamlit as st
import pandas as pd
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
            # High NRW
            high_nrw = performance_df[performance_df['NRW'] > 25]
            if len(high_nrw) > 0:
                st.warning(f"""
                **💧 High Non-Revenue Water:**
                
                {chr(10).join([f"- **{row['Country']}**: {row['NRW']:.1f}% NRW" 
                               for _, row in high_nrw.iterrows()])}
                
                **Action:** Implement leak detection and metering programs
                """)
            
            # Low OCCR
            low_occr = performance_df[performance_df['OCCR'] < 110]
            if len(low_occr) > 0:
                st.warning(f"""
                **📉 Low Cost Recovery:**
                
                {chr(10).join([f"- **{row['Country']}**: {row['OCCR']:.1f}% OCCR" 
                               for _, row in low_occr.iterrows()])}
                
                **Action:** Review tariff structures and reduce operational costs
                """)
            
            # Low coverage
            low_coverage = performance_df[performance_df['Water Coverage'] < 80]
            if len(low_coverage) > 0:
                st.warning(f"""
                **🚰 Low Water Coverage:**
                
                {chr(10).join([f"- **{row['Country']}**: {row['Water Coverage']:.1f}% coverage" 
                               for _, row in low_coverage.iterrows()])}
                
                **Action:** Prioritize infrastructure expansion in underserved zones
                """)
    
    st.markdown("---")
    
    # Detailed Action Plans by Domain
    st.header("📋 Domain-Specific Action Plans")
    
    # Production Domain Actions
    with st.expander("🏭 Production Domain - Recommended Actions"):
        production_df = data['production']
        if countries_filter:
            production_df = production_df[production_df['country'].isin(countries_filter)]
        
        avg_service_hours = production_df['service_hours'].mean()
        low_service_sources = production_df[production_df['service_hours'] < 20].groupby('country')['source'].count()
        
        st.markdown(f"""
        ### Current Status
        - **Average service hours:** {avg_service_hours:.1f} hrs/day (Benchmark: ≥20 hrs/day)
        - **Sources below benchmark:** {len(production_df[production_df['service_hours'] < 20])}
        
        ### Priority Actions
        
        1. **Improve Service Continuity**
           - 🔧 Conduct infrastructure audits for sources with <20 hrs service
           - ⚡ Address power supply issues and backup systems
           - 💧 Optimize pumping schedules to maximize service hours
           - **Timeline:** 3-6 months
           - **Expected Impact:** Increase service hours by 15-20%
        
        2. **Optimize Production Capacity**
           - 📊 Analyze production vs demand patterns
           - 🔄 Balance load across multiple sources
           - 🛠️ Schedule preventive maintenance during low-demand periods
           - **Timeline:** Ongoing
           - **Expected Impact:** Reduce emergency breakdowns by 30%
        
        3. **Enhance Monitoring Systems**
           - 📱 Install SCADA systems for real-time monitoring
           - 📊 Implement dashboard for production tracking
           - 🚨 Set up alerts for low production or service interruptions
           - **Timeline:** 6-12 months
           - **Expected Impact:** Faster response to issues, 24/7 monitoring
        """)
    
    # Service Domain Actions
    with st.expander("🚰 Service Domain - Recommended Actions"):
        w_service = data['w_service']
        if countries_filter:
            w_service = w_service[w_service['country'].isin(countries_filter)]
        
        chlorine_rate = (w_service['test_passed_chlorine'].sum() / 
                        w_service['tests_conducted_chlorine'].sum() * 100)
        metering_rate = (w_service['metered'].sum() / 
                        w_service['total_consumption'].sum() * 100)
        
        st.markdown(f"""
        ### Current Status
        - **Water quality compliance:** {chlorine_rate:.1f}% (Benchmark: ≥95%)
        - **Metering ratio:** {metering_rate:.1f}% (Benchmark: ≥95%)
        
        ### Priority Actions
        
        1. **Improve Water Quality**
           - 🧪 Increase testing frequency in failing zones
           - 💊 Ensure adequate chlorine supply and dosing
           - 🔬 Train staff on water quality monitoring
           - **Timeline:** Immediate (0-3 months)
           - **Expected Impact:** Achieve 95%+ compliance
        
        2. **Expand Metering Coverage**
           - 📊 Prioritize zones with <50% metering ratio
           - 💳 Install smart meters with remote reading capability
           - 🔧 Replace non-functional meters
           - **Timeline:** 12-24 months
           - **Expected Impact:** Reduce commercial losses by 10-15%
        
        3. **Enhance Customer Service**
           - 📞 Establish 24/7 customer service hotline
           - 💻 Implement online complaint tracking system
           - 📱 Send SMS alerts for service interruptions
           - **Timeline:** 3-6 months
           - **Expected Impact:** Improve customer satisfaction by 25%
        """)
    
    # Access Domain Actions
    with st.expander("🌍 Access Domain - Recommended Actions"):
        w_access = data['w_access']
        if countries_filter:
            w_access = w_access[w_access['country'].isin(countries_filter)]
        
        latest_year = w_access['year'].max()
        w_access_latest = w_access[w_access['year'] == latest_year]
        
        avg_coverage = ((w_access_latest['safely_managed'].sum() + 
                        w_access_latest['basic'].sum()) / 
                       w_access_latest['popn_total'].sum() * 100)
        underserved_zones = len(w_access_latest[
            ((w_access_latest['safely_managed'] + w_access_latest['basic']) / 
             w_access_latest['popn_total'] * 100) < 50
        ])
        
        st.markdown(f"""
        ### Current Status
        - **Average water coverage:** {avg_coverage:.1f}% (Target: 100%)
        - **Zones with <50% coverage:** {underserved_zones}
        
        ### Priority Actions
        
        1. **Target Underserved Areas**
           - 🗺️ Map underserved zones and population density
           - 💰 Allocate budget proportional to coverage gap
           - 🏗️ Fast-track infrastructure projects in priority zones
           - **Timeline:** 18-36 months
           - **Expected Impact:** Increase coverage by 10-15 percentage points
        
        2. **Promote Alternative Service Providers**
           - 🤝 License and regulate Small-Scale Service Providers (SSSPs)
           - 💧 Provide technical support and quality monitoring
           - 📊 Track performance and coverage expansion
           - **Timeline:** 12-18 months
           - **Expected Impact:** Reach remote/rural areas faster
        
        3. **Implement Pro-Poor Strategies**
           - 💵 Introduce subsidized tariffs for low-income households
           - 🚰 Install public water points in informal settlements
           - 📚 Conduct awareness campaigns on water conservation
           - **Timeline:** 6-12 months
           - **Expected Impact:** Improve equity and affordability
        """)
    
    # Finance Domain Actions
    with st.expander("💰 Finance Domain - Recommended Actions"):
        finance = data['finance']
        if countries_filter:
            finance = finance[finance['country'].isin(countries_filter)]
        
        avg_occr = ((finance['sewer_revenue'].sum() / finance['opex'].sum()) * 100)
        collection_eff = ((finance['sewer_revenue'].sum() / 
                          finance['sewer_billed'].sum()) * 100)
        
        st.markdown(f"""
        ### Current Status
        - **Average OCCR:** {avg_occr:.1f}% (Benchmark: ≥110%)
        - **Collection efficiency:** {collection_eff:.1f}% (Benchmark: ≥95%)
        
        ### Priority Actions
        
        1. **Improve Revenue Collection**
           - 💳 Implement mobile payment platforms (M-Pesa, etc.)
           - 📊 Automate billing and reduce manual errors
           - 🚫 Enforce disconnection for chronic defaulters
           - **Timeline:** 3-6 months
           - **Expected Impact:** Increase collection efficiency to 95%+
        
        2. **Optimize Operating Costs**
           - ⚡ Conduct energy audits and optimize pumping schedules
           - 👥 Right-size staffing based on productivity benchmarks
           - 🔧 Implement preventive maintenance programs
           - **Timeline:** 6-12 months
           - **Expected Impact:** Reduce OpEx by 10-15%
        
        3. **Review Tariff Structures**
           - 💰 Ensure tariffs cover full O&M costs
           - 📊 Implement increasing block tariffs for equity
           - 🏢 Cross-subsidize with commercial/industrial tariffs
           - **Timeline:** 12-18 months (requires regulatory approval)
           - **Expected Impact:** Achieve OCCR >110%
        
        4. **Financial Management Capacity**
           - 📚 Train staff on financial planning and budgeting
           - 💻 Implement financial management software
           - 📊 Establish monthly financial reporting routines
           - **Timeline:** 3-6 months
           - **Expected Impact:** Better financial decision-making
        """)
    
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
    
    st.markdown("---")
    
    # Summary Insights
    st.header("💡 Key Takeaways")
    
    st.success("""
    ### Overall Performance Summary
    
    ✅ **Strengths:**
    - Strong regulatory frameworks in place
    - Improving water quality compliance
    - Increasing metering coverage
    
    ⚠️ **Areas for Improvement:**
    - Non-Revenue Water remains high (>25% in some countries)
    - Cost recovery below benchmark in several utilities
    - Coverage gaps persist in rural and underserved areas
    
    🎯 **Strategic Priorities (Next 12 Months):**
    1. Launch aggressive NRW reduction programs
    2. Improve revenue collection efficiency to 95%+
    3. Expand coverage in underserved zones
    4. Strengthen financial management capacity
    5. Enhance customer service and complaint resolution
    
    📊 **Expected Impact:**
    - 10-15% reduction in NRW
    - 5-10% improvement in OCCR
    - 100,000+ additional people with access to safe water
    - Enhanced financial sustainability across all countries
    """)


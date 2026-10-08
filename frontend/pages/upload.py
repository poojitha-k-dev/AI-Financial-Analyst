import streamlit as st
from frontend import api_client as api
from frontend.theme import page_header


def show():
    page_header("Upload Financial Statement", "Import PDF, CSV, or Excel financial data", "📤")

    companies = api.get_companies()
    if not companies:
        st.warning("Please add a company first under **Companies**.")
        if st.button("➕ Add Company"):
            st.session_state.current_page = "Companies"
            st.rerun()
        return

    company_map = {f"{c['name']} ({c['ticker'] or 'ID:'+str(c['id'])})": c["id"] for c in companies}

    col_form, col_guide = st.columns([3, 2])

    with col_form:
        st.markdown("<p class='section-title'>Upload Details</p>", unsafe_allow_html=True)
        with st.form("upload_form", clear_on_submit=False):
            company_key = st.selectbox("Company *", list(company_map.keys()))
            col1, col2 = st.columns(2)
            with col1:
                period = st.text_input(
                    "Period *", placeholder="e.g. 2023-FY  or  2023-Q3",
                    help="Use YYYY-FY for annual, YYYY-Q1/Q2/Q3/Q4 for quarterly",
                )
                period_type = st.selectbox("Period Type", ["annual", "quarterly"])
            with col2:
                statement_type = st.selectbox("Statement Type", [
                    "combined", "income_statement", "balance_sheet", "cash_flow",
                ])

            file = st.file_uploader(
                "Financial Statement *",
                type=["pdf", "csv", "xlsx", "xls"],
                help="Upload a PDF annual report, or CSV/Excel spreadsheet",
            )

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 Upload & Parse", use_container_width=True)

        if submitted:
            if not file:
                st.error("Please select a file to upload.")
            elif not period.strip():
                st.error("Please enter a period (e.g. 2023-FY).")
            else:
                company_id = company_map[company_key]
                with st.spinner(f"Parsing {file.name}..."):
                    result = api.upload_statement(
                        file_bytes=file.read(),
                        filename=file.name,
                        company_id=company_id,
                        period=period.strip(),
                        period_type=period_type,
                        statement_type=statement_type,
                    )

                if result:
                    st.success(f"✅ {result['message']}")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Fields Extracted", result.get("fields_extracted", 0))
                    c2.metric("KPIs Calculated", result.get("kpis_calculated", 0))
                    c3.metric("Periods Imported", len(result.get("periods_imported", [])))

                    preview = result.get("preview", {})
                    if preview:
                        st.markdown("<p class='section-title' style='margin-top:1rem;'>Quick Preview</p>",
                                    unsafe_allow_html=True)
                        pc1, pc2, pc3, pc4, pc5, pc6 = st.columns(6)
                        _fmt = lambda v: f"${v/1e9:.2f}B" if v and abs(v) >= 1e9 else f"${v/1e6:.1f}M" if v and abs(v) >= 1e6 else f"${v:,.0f}" if v else "—"
                        _pct = lambda v: f"{v:.1f}%" if v else "—"
                        pc1.metric("Revenue", _fmt(preview.get("revenue")))
                        pc2.metric("Net Income", _fmt(preview.get("net_income")))
                        pc3.metric("Total Assets", _fmt(preview.get("total_assets")))
                        pc4.metric("Gross Margin", _pct(preview.get("gross_margin")))
                        pc5.metric("Net Margin", _pct(preview.get("net_margin")))
                        pc6.metric("Current Ratio", f"{preview.get('current_ratio'):.2f}x" if preview.get("current_ratio") else "—")

                    periods = result.get("periods_imported", [])
                    if len(periods) > 1:
                        st.info(f"📅 Multi-period data detected. Imported: {', '.join(periods)}")

                    st.info("💡 Go to **AI Insights** to generate a full AI-powered analysis.")

    with col_guide:
        st.markdown("<p class='section-title'>Supported Formats</p>", unsafe_allow_html=True)

        with st.expander("📄 PDF Annual Reports", expanded=True):
            st.markdown("""
            - Annual reports, 10-K filings, investor presentations
            - Extracts financial tables automatically
            - Works with most structured PDFs
            """)

        with st.expander("📊 CSV / Excel Files", expanded=True):
            st.markdown("""
            **Two-column format:**
            ```
            Metric,Value
            Revenue,394328000000
            Net Income,99803000000
            ```

            **Multi-period (all years imported at once):**
            ```
            Metric,2021,2022,2023
            Revenue,365B,394B,383B
            ```
            """)

        with st.expander("💡 Tips for Best Results"):
            st.markdown("""
            - Use standard accounting terminology for field names
            - Numbers with `(parentheses)` are treated as negative
            - Suffixes `1.2B`, `350M`, `5K` are auto-converted
            - Upload the most recent year first
            - Multi-period CSVs import all years automatically
            """)

        st.markdown("<p class='section-title' style='margin-top:1rem;'>Sample Data</p>", unsafe_allow_html=True)
        st.markdown("""
        <div class="fin-card">
            <div style="font-size:0.82rem;color:var(--text-secondary);">
                Download sample CSV files to test the platform instantly.
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            try:
                with open("data/sample/apple_financials_2023.csv", "rb") as f:
                    st.download_button("⬇️ Apple CSV", f.read(), "apple_financials_2023.csv",
                                       use_container_width=True)
            except FileNotFoundError:
                pass
        with col_b:
            try:
                with open("data/sample/tesla_financials_2023.csv", "rb") as f:
                    st.download_button("⬇️ Tesla CSV", f.read(), "tesla_financials_2023.csv",
                                       use_container_width=True)
            except FileNotFoundError:
                pass

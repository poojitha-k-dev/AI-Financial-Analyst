import streamlit as st
from frontend import api_client as api
from frontend.theme import page_header, rating_badge


def show():
    page_header("Reports", "Export professional PDF and Excel financial reports", "📄")

    companies = api.get_companies()
    if not companies:
        st.warning("Add a company and upload data first.")
        return

    company_map = {c["name"]: c["id"] for c in companies}
    selected = st.selectbox("Company", list(company_map.keys()), label_visibility="collapsed")
    cid = company_map[selected]

    # ── Report history ──
    reports = api.list_reports(cid)

    if reports:
        st.markdown("<p class='section-title'>Analysis Report History</p>", unsafe_allow_html=True)
        for r in reports:
            rating = r.get("overall_rating", "")
            with st.expander(
                f"**{r['title']}** — {r.get('created_at','')[:10]} "
                f"{'| ' + rating if rating else ''}",
                expanded=False
            ):
                if r.get("executive_summary"):
                    st.markdown(r["executive_summary"])
                meta_cols = st.columns(4)
                meta_cols[0].caption(f"Model: {r.get('llm_provider','—')}")
                meta_cols[1].caption(f"Type: {r.get('report_type','—')}")
                if rating:
                    with meta_cols[2]:
                        st.markdown(f"Rating: {rating_badge(rating)}", unsafe_allow_html=True)
    else:
        st.info("No reports yet. Run AI Analysis first to generate reports.")

    # ── Export section ──
    st.markdown("---")
    st.markdown("<p class='section-title'>Export Report</p>", unsafe_allow_html=True)

    col_pdf, col_excel = st.columns(2)

    with col_pdf:
        st.markdown("""
        <div class="fin-card" style="border-top:3px solid #3b82f6;">
            <div style="font-size:1.5rem;margin-bottom:8px;">📋</div>
            <div style="font-weight:700;font-size:1rem;color:var(--text-primary);">PDF Report</div>
            <div style="font-size:0.8rem;color:var(--text-secondary);margin:8px 0;">
                Professional A4 PDF with cover page, KPI tables, risk model scores,
                composite health scores, and full AI-generated narrative analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📥 Generate & Download PDF", use_container_width=True, key="pdf_btn"):
            with st.spinner("Generating PDF..."):
                pdf_bytes = api.export_pdf_bytes(cid)
            if pdf_bytes:
                # Find the company name for filename
                co_name = next((c["name"] for c in companies if c["id"] == cid), "report")
                st.download_button(
                    "⬇️ Download PDF Now",
                    data=pdf_bytes,
                    file_name=f"{co_name}_financial_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    with col_excel:
        st.markdown("""
        <div class="fin-card" style="border-top:3px solid #10b981;">
            <div style="font-size:1.5rem;margin-bottom:8px;">📊</div>
            <div style="font-weight:700;font-size:1rem;color:var(--text-primary);">Excel Report</div>
            <div style="font-size:0.8rem;color:var(--text-secondary);margin:8px 0;">
                Multi-sheet Excel workbook: Summary, Profitability, Liquidity, Leverage,
                Efficiency, Cash Flow, and Growth KPI sheets — fully formatted.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📥 Generate & Download Excel", use_container_width=True, key="excel_btn"):
            with st.spinner("Generating Excel..."):
                xl_bytes = api.export_excel_bytes(cid)
            if xl_bytes:
                co_name = next((c["name"] for c in companies if c["id"] == cid), "report")
                st.download_button(
                    "⬇️ Download Excel Now",
                    data=xl_bytes,
                    file_name=f"{co_name}_financial_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    # ── Report contents ──
    st.markdown("---")
    st.markdown("<p class='section-title'>What's Included in Each Report</p>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        **PDF Report contains:**
        - Cover page (company, period, date)
        - Key financial metrics summary table
        - KPI analysis across 5 categories
        - Composite financial health scores
        - Altman Z-Score detailed breakdown
        - AI-generated narrative (full)
        - Risk analysis summary
        - Disclaimer footer
        """)
    with c2:
        st.markdown("""
        **Excel Report contains:**
        - Summary sheet with key metrics
        - Profitability KPIs sheet
        - Liquidity KPIs sheet
        - Leverage KPIs sheet
        - Efficiency KPIs sheet
        - Cash Flow KPIs sheet
        - Growth KPIs sheet
        """)
    with c3:
        st.markdown("""
        **Best practices:**
        - Run **AI Insights** first for richer narrative
        - Upload 3+ periods for growth metrics
        - Reports auto-include the latest analysis
        - All values are formatted (B/M/K suffix)
        - PDFs are print-ready A4 format
        - Excel files use professional styling
        """)

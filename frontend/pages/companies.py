import streamlit as st
from frontend import api_client as api
from frontend.theme import page_header

SECTORS = [
    "", "Technology", "Healthcare", "Finance", "Consumer Discretionary",
    "Consumer Staples", "Energy", "Industrials", "Materials",
    "Real Estate", "Utilities", "Communication Services",
]

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]


def show():
    page_header("Company Portfolio", "Manage the companies you're tracking", "🏢")

    tab_list, tab_add = st.tabs(["  My Companies  ", "  Add New  "])

    with tab_list:
        _show_company_list()

    with tab_add:
        _show_add_form()


def _show_company_list():
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Company name...", label_visibility="collapsed")
    with col2:
        sector_filter = st.selectbox("Sector", SECTORS, label_visibility="collapsed")
    with col3:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    companies = api.get_companies(search=search or None, sector=sector_filter or None)

    if not companies:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem;background:var(--bg-card);
                    border-radius:var(--radius);border:1px solid var(--border);margin-top:1rem;">
            <div style="font-size:2.5rem;margin-bottom:0.75rem;">🔍</div>
            <p style="color:var(--text-muted);">No companies found. Add your first company!</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"<p class='section-title'>{len(companies)} Companies</p>", unsafe_allow_html=True)

    for co in companies:
        with st.expander(
            f"**{co['name']}** {'— ' + co['ticker'] if co.get('ticker') else ''}  "
            f"{'· ' + co.get('sector','') if co.get('sector') else ''}",
            expanded=False,
        ):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"**Sector:** {co.get('sector') or '—'}")
                st.markdown(f"**Industry:** {co.get('industry') or '—'}")
            with col2:
                st.markdown(f"**Country:** {co.get('country') or '—'}")
                st.markdown(f"**Currency:** {co.get('currency', 'USD')}")
            with col3:
                st.markdown(f"**Statements:** {co.get('statement_count', 0)}")
                if co.get("latest_period"):
                    st.markdown(f"**Latest:** {co['latest_period']}")
            with col4:
                if co.get("website"):
                    st.link_button("🌐 Website", co["website"])

            if co.get("description"):
                st.caption(co["description"])

            edit_col, del_col, _ = st.columns([1, 1, 3])
            with edit_col:
                if st.button("✏️ Edit", key=f"edit_{co['id']}", use_container_width=True):
                    st.session_state[f"editing_{co['id']}"] = True
                    st.rerun()

            with del_col:
                if st.button("🗑️ Delete", key=f"del_{co['id']}", use_container_width=True):
                    st.session_state[f"confirm_del_{co['id']}"] = True

            if st.session_state.get(f"confirm_del_{co['id']}"):
                st.warning(f"Delete **{co['name']}** and all its data? This cannot be undone.")
                yes_col, no_col, _ = st.columns([1, 1, 3])
                with yes_col:
                    if st.button("Yes, delete", key=f"yes_{co['id']}", use_container_width=True):
                        if api.delete_company(co["id"]):
                            st.success(f"Deleted {co['name']}")
                            del st.session_state[f"confirm_del_{co['id']}"]
                            st.rerun()
                with no_col:
                    if st.button("Cancel", key=f"no_{co['id']}", use_container_width=True):
                        del st.session_state[f"confirm_del_{co['id']}"]
                        st.rerun()

            if st.session_state.get(f"editing_{co['id']}"):
                _show_edit_form(co)


def _show_edit_form(co):
    st.markdown("---")
    st.markdown("**Edit Company**")
    with st.form(f"edit_form_{co['id']}"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Company Name", value=co.get("name", ""))
            ticker = st.text_input("Ticker", value=co.get("ticker") or "")
            sector = st.selectbox("Sector", SECTORS,
                                  index=SECTORS.index(co.get("sector") or "") if co.get("sector") in SECTORS else 0)
        with c2:
            industry = st.text_input("Industry", value=co.get("industry") or "")
            country = st.text_input("Country", value=co.get("country") or "")
            currency = st.selectbox("Currency", CURRENCIES,
                                    index=CURRENCIES.index(co.get("currency", "USD")) if co.get("currency") in CURRENCIES else 0)
        website = st.text_input("Website", value=co.get("website") or "")
        description = st.text_area("Description", value=co.get("description") or "", height=60)
        save, cancel = st.columns(2)
        with save:
            submitted = st.form_submit_button("Save Changes", use_container_width=True)
        with cancel:
            if st.form_submit_button("Cancel", use_container_width=True):
                del st.session_state[f"editing_{co['id']}"]
                st.rerun()

    if submitted:
        result = api.update_company(
            co["id"], name=name, ticker=ticker or None, sector=sector or None,
            industry=industry or None, country=country or None, currency=currency,
            website=website or None, description=description or None,
        )
        if result:
            st.success("✅ Company updated")
            del st.session_state[f"editing_{co['id']}"]
            st.rerun()


def _show_add_form():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.form("add_company_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Company Name *", placeholder="Apple Inc.")
            ticker = st.text_input("Ticker Symbol", placeholder="AAPL")
            sector = st.selectbox("Sector", SECTORS)
            industry = st.text_input("Industry", placeholder="Consumer Electronics")
        with col2:
            country = st.text_input("Country", placeholder="United States")
            currency = st.selectbox("Currency", CURRENCIES)
            website = st.text_input("Website", placeholder="https://apple.com")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        description = st.text_area("Description (optional)", height=80,
                                   placeholder="Brief description of the company's business...")
        submitted = st.form_submit_button("➕ Add Company", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Company name is required")
        else:
            result = api.create_company(
                name=name.strip(),
                ticker=ticker.strip() or None,
                sector=sector or None,
                industry=industry.strip() or None,
                country=country.strip() or None,
                currency=currency,
                website=website.strip() or None,
                description=description.strip() or None,
            )
            if result:
                st.success(f"✅ **{name}** added to your portfolio!")
                st.info("👉 Head to **Upload** to add financial statements.")

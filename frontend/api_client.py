"""
Centralised API client — reads BASE_URL from env so Docker works correctly.
"""
import os
import httpx
import streamlit as st
from typing import Any, Dict, Optional

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 120.0


def _headers() -> Dict[str, str]:
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _get(endpoint: str, params: Optional[Dict] = None) -> Any:
    try:
        r = httpx.get(f"{BASE_URL}{endpoint}", params=params, headers=_headers(), timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            st.session_state.pop("access_token", None)
            st.session_state.pop("user", None)
            st.error("Session expired. Please log in again.")
        else:
            st.error(f"Error {e.response.status_code}: {e.response.json().get('detail', e.response.text)}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def _post(endpoint: str, json: Optional[Dict] = None, data: Optional[Dict] = None, files=None) -> Any:
    try:
        r = httpx.post(
            f"{BASE_URL}{endpoint}", json=json, data=data, files=files,
            headers=_headers(), timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            st.session_state.pop("access_token", None)
            st.error("Session expired. Please log in again.")
        else:
            try:
                detail = e.response.json().get("detail", e.response.text)
            except Exception:
                detail = e.response.text
            st.error(f"Error {e.response.status_code}: {detail}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def _patch(endpoint: str, json: Dict) -> Any:
    try:
        r = httpx.patch(f"{BASE_URL}{endpoint}", json=json, headers=_headers(), timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        st.error(f"Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def _delete(endpoint: str) -> Any:
    try:
        r = httpx.delete(f"{BASE_URL}{endpoint}", headers=_headers(), timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def _get_bytes(endpoint: str) -> Optional[bytes]:
    try:
        r = httpx.post(f"{BASE_URL}{endpoint}", headers=_headers(), timeout=TIMEOUT)
        r.raise_for_status()
        return r.content
    except Exception as e:
        st.error(f"Download error: {e}")
        return None


# ── Auth ──────────────────────────────────────────────────────────────────────
def register(email, full_name, password, company_name=None):
    return _post("/auth/register", json={
        "email": email, "full_name": full_name,
        "password": password, "company_name": company_name,
    })


def login(email, password):
    return _post("/auth/login", data={"username": email, "password": password})


def get_me():
    return _get("/auth/me")


def update_profile(full_name=None, company_name=None, bio=None):
    payload = {}
    if full_name is not None:
        payload["full_name"] = full_name
    if company_name is not None:
        payload["company_name"] = company_name
    if bio is not None:
        payload["bio"] = bio
    return _patch("/auth/me", payload)


def change_password(current_password, new_password):
    return _post("/auth/change-password", json={
        "current_password": current_password, "new_password": new_password
    })


# ── Companies ─────────────────────────────────────────────────────────────────
def get_companies(search=None, sector=None):
    params = {}
    if search:
        params["search"] = search
    if sector:
        params["sector"] = sector
    return _get("/companies/", params=params) or []


def create_company(name, ticker=None, sector=None, industry=None, country=None,
                   currency="USD", description=None, website=None):
    return _post("/companies/", json={
        "name": name, "ticker": ticker, "sector": sector,
        "industry": industry, "country": country, "currency": currency,
        "description": description, "website": website,
    })


def update_company(company_id, **kwargs):
    return _patch(f"/companies/{company_id}", kwargs)


def delete_company(company_id):
    return _delete(f"/companies/{company_id}")


def get_statements(company_id):
    return _get(f"/companies/{company_id}/statements") or []


def delete_statement(company_id, stmt_id):
    return _delete(f"/companies/{company_id}/statements/{stmt_id}")


# ── Upload ────────────────────────────────────────────────────────────────────
def upload_statement(file_bytes, filename, company_id, period, period_type, statement_type):
    return _post(
        "/upload/statement",
        data={"company_id": str(company_id), "period": period,
              "period_type": period_type, "statement_type": statement_type},
        files={"file": (filename, file_bytes, "application/octet-stream")},
    )


# ── Analysis ──────────────────────────────────────────────────────────────────
def run_full_analysis(company_id, statement_id=None):
    params = f"?statement_id={statement_id}" if statement_id else ""
    return _post(f"/analysis/{company_id}/full{params}")


def get_kpis(company_id):
    return _get(f"/analysis/{company_id}/kpis")


def get_risk(company_id):
    return _get(f"/analysis/{company_id}/risk")


def get_forecast(company_id, periods=4):
    return _get(f"/analysis/{company_id}/forecast", params={"periods": periods})


def list_reports(company_id):
    return _get(f"/analysis/{company_id}/reports") or []


def export_pdf_bytes(company_id):
    return _get_bytes(f"/analysis/{company_id}/export/pdf")


def export_excel_bytes(company_id):
    return _get_bytes(f"/analysis/{company_id}/export/excel")


# ── Chat ──────────────────────────────────────────────────────────────────────
def send_chat(question, company_id, session_id=None):
    return _post("/chat/", json={"question": question, "company_id": company_id, "session_id": session_id})


def get_chat_history(company_id, session_id=None, limit=50):
    params = {"limit": limit}
    if session_id:
        params["session_id"] = session_id
    return _get(f"/chat/history/{company_id}", params=params) or []


def clear_chat(company_id, session_id=None):
    endpoint = f"/chat/history/{company_id}"
    if session_id:
        endpoint += f"?session_id={session_id}"
    return _delete(endpoint)

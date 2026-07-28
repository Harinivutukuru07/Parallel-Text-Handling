"""Compatibility entrypoint for Streamlit UI."""

with open("Interface.py", encoding="utf-8") as f:
    exec(f.read())

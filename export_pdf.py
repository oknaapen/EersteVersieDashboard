import streamlit as st
import pandas as pd

def maak_pdf():
    # Stijl voor groene knop
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #32CD32;
            color: black;
            font-weight: bold;
            border: none;
            padding: 0.5em 1em;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.button("📄 Genereer PDF"):

        from fpdf import FPDF
        import tempfile
        import os
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        def add_fig_to_pdf(pdf, fig, titel):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                canvas = FigureCanvas(fig)
                canvas.print_png(tmpfile.name)
                tmpfile.close()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, titel, ln=True)
                pdf.image(tmpfile.name, w=180)
                os.unlink(tmpfile.name)

        # Zet dit erbuiten, onder de functie!
        titels = {
            "grafiek_kwadrant1": "Klachten in de tijd",
            "grafiek_kwadrant2": "Verdeling klachten",
            "grafiek_kwadrant3": "Meldingen op de kaart",
            "grafiek_kwadrant4": "Workload per team",
            "grafiek_kwadrant5": "Tevredenheid per team",
            "grafiek_kwadrant6": "Binnen/buiten behandeltermijn"
        }

        for key, titel in titels.items():
            if key in st.session_state and st.session_state[key] is not None:
                add_fig_to_pdf(pdf, st.session_state[key], titel)

        # Downloadknop
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output:
            pdf.output(output.name)
            with open(output.name, "rb") as file:
                st.download_button("📥 Download PDF", file, file_name="dashboard.pdf", mime="application/pdf")

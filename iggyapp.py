import sys
import os
import subprocess
import shutil
import streamlit as st

class rsc:
    @staticmethod
    def get_image(filename):
        return f"./images/{filename}"

def setup_page():
    st.set_page_config(
        page_title="Iggypop",
        page_icon=rsc.get_image("best_icon.png"),
        layout="centered",
        initial_sidebar_state="auto",
    )
    sys.tracebacklimit = 0

    dark_theme_style = """
    <style>
      /* your dark CSS… */
    </style>
    """
    st.markdown(dark_theme_style, unsafe_allow_html=True)
    st.image(rsc.get_image("Iggypopbest2.png"))

    st.sidebar.markdown("### Contact information")
    st.sidebar.markdown(
        """
        <div style="display: flex; gap: 10px; align-items: center;">
            <img src="images/Github-Logo-PNG.png" width="32">
            <img src="images/email.png" width="32">
            <img src="images/paper.png" width="32">
        </div>
        """,
        unsafe_allow_html=True,
    )

def go_to(page_name):
    st.session_state.page = page_name

def run_streamlit():
    setup_page()

    if "page" not in st.session_state:
        st.session_state.page = "main"

    # --- MAIN MENU ---
    if st.session_state.page == "main":
        st.title("Welcome to Iggypop")
        st.write("Choose runtype to continue:")
        c1, c2 = st.columns(2)
        c1.button("CDS", on_click=go_to, args=("cds",))
        c2.button("GB",  on_click=go_to, args=("gb",))

    # --- CDS SUB‐PAGE ---
    elif st.session_state.page == "cds":
        st.title("CDS Runtype")

        # FASTA uploader
        uploaded_fasta = st.file_uploader(
            "Upload your FASTA file", type=["fasta", "fa", "txt"]
        )
        if uploaded_fasta is not None:
            st.write(f"Uploaded file: **{uploaded_fasta.name}**")

        # Mode selector
        st.subheader("Mode")
        mode = st.radio("", ["chisel", "no_mods", "no_hinge"], index=0)

        # Codon optimization
        st.subheader("Codon optimization method")
        codon_method = st.radio(
            "",
            ["use_best_codon", "match_codon_usage", "harmonize_rca", "hybrid", "none"],
            index=4,
        )

        # Species & Original species
        if codon_method != "none":
            st.subheader("Species")
            species = st.text_input(
                "Species",
                value="arabidopsis",
                help="e.g. arabidopsis, escherichia_coli, saccharomyces_cerevisiae",
            )
            if codon_method == "harmonize_rca":
                st.subheader("Original species")
                original_species = st.text_input(
                    "Original species",
                    value="arabidopsis",
                    help="The source organism you’re harmonizing from",
                )

        # Hybrid divergence
        if codon_method == "hybrid":
            st.subheader("Target sequence divergence for hybrid optimization")
            divergence = st.number_input(
                "Percent divergence",
                value=20.0,
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                help="e.g. 20.0 for 20%",
            )

        # Repeats
        st.subheader("Repeats")
        repeats = st.number_input("", min_value=1, value=1, step=1)

        # Oligo length
        st.subheader("Oligo length")
        oligo_length = st.number_input(
            "",
            min_value=1,
            value=250,
            step=1,
            help="Max oligo length in bp",
        )

        # External overhangs
        st.subheader("External overhangs")
        ext_overhang_5 = st.text_input(
            "External overhang 5′", value="AATG", help="Overhang on the 5′ end"
        )
        ext_overhang_3 = st.text_input(
            "External overhang 3′", value="GCTT", help="Overhang on the 3′ end"
        )

        # Base ends
        st.subheader("Base 5′ end")
        base5 = st.text_input("Base 5′ end", value="AATGCGGTCTCTA")
        st.subheader("Base 3′ end")
        base3 = st.text_input("Base 3′ end", value="GCTTAGAGACCGCTT")

        # Two-step assemblies
        st.subheader("Two-step assemblies")
        two_step = st.radio("", ["On", "Off"], index=1)

        # PCR CUT sites
        st.subheader("PCR 5′ CUT")
        pcr5_cut = st.text_input("PCR 5′ CUT", value="CGTCTCA")
        st.subheader("PCR 3′ CUT")
        pcr3_cut = st.text_input("PCR 3′ CUT", value="AGAGACG")

        # Primer index
        st.subheader("Primer index")
        primer_index = st.number_input(
            "This is the row of indexsets file to start from",
            min_value=1,
            value=1,
            step=1,
        )

        # Number of tries
        st.subheader("Number of tries")
        num_tries = st.number_input("", min_value=1, value=50, step=1)

        # Radius
        st.subheader("Radius")
        radius = st.number_input("", min_value=1, value=8, step=1)

        # Maximum fragments per PCR
        st.subheader("Maximum fragments per PCR")
        max_fragments = st.number_input("", min_value=1, value=18, step=1)

        # Example & Back buttons
        if st.button("Example"):
            st.write("You clicked the CDS Example button!")
        st.button("Back", on_click=go_to, args=("main",))

        # ——— New “Pop!” button ———
        if st.button("Pop!"):
            if uploaded_fasta is None:
                st.error("Please upload a FASTA file first.")
            else:
                # 1) save the uploaded file
                upload_dir = "./uploads"
                os.makedirs(upload_dir, exist_ok=True)
                input_path = os.path.join(upload_dir, uploaded_fasta.name)
                with open(input_path, "wb") as f:
                    f.write(uploaded_fasta.getbuffer())

                # 2) determine the output stem
                stem = os.path.splitext(uploaded_fasta.name)[0]

                # 3) assemble the iggypop command
                cmd = ["./iggypop.py", "cds", "--i", input_path, "--o", stem]
                cmd += ["--mode", mode]
                cmd += ["--codon_opt", codon_method]
                if codon_method != "none":
                    cmd += ["--species", species]
                    if codon_method == "harmonize_rca":
                        cmd += ["--original_species", original_species]
                if codon_method == "hybrid":
                    cmd += ["--pct", str(divergence)]
                cmd += ["--repeats", str(repeats)]
                if two_step == "On":
                    cmd += ["--two_step", "on"]
                cmd += ["--oligo_length", str(oligo_length)]
                cmd += ["--ext_overhangs", ext_overhang_5, ext_overhang_3]
                cmd += ["--base_5p_end", base5]
                cmd += ["--base_3p_end", base3]
                cmd += ["--pcr_5p_cut", pcr5_cut]
                cmd += ["--pcr_3p_cut", pcr3_cut]
                cmd += ["--primer_index", str(primer_index)]
                cmd += ["--n_tries", str(num_tries)]
                cmd += ["--radius", str(radius)]
                cmd += ["--max_fragments", str(max_fragments)]

                # 4) run it
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    # ZIP up the out/stem folder
                    out_dir = os.path.join("out", stem)
                    zip_path = shutil.make_archive(out_dir, 'zip', out_dir)

                    # store for the results page
                    st.session_state.result_zip = zip_path
                    st.session_state.last_stem = stem
                    st.session_state.page = "results"
                    st.rerun()
                else:
                    st.error(f"❌ iggypop failed (exit {result.returncode}):\n```\n{result.stderr}\n```")

    # --- RESULTS PAGE ---
    elif st.session_state.page == "results":
        st.title("Run Complete!")
        stem = st.session_state.last_stem
        zip_path = st.session_state.result_zip

        st.write(f"Your results for **{stem}** are ready. Download them as a ZIP:")
        with open(zip_path, "rb") as fp:
            st.download_button(
                label="📦 Download Results",
                data=fp,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
            )

        st.button("← Back to CDS", on_click=go_to, args=("cds",))

    # --- GB SUB‐PAGE ---
    elif st.session_state.page == "gb":
        st.title("GB Page")
        if st.button("Example"):
            st.write("You clicked the GB Example button!")
        st.button("Back", on_click=go_to, args=("main",))

if __name__ == "__main__":
    run_streamlit()

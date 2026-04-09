import streamlit as st
import pandas as pd

def main():
    st.title("Log File Processor")

    # Input fields for description and short description
    description = st.text_input("Description")
    short_description = st.text_input("Short Description")

    uploaded_file = st.file_uploader("Upload a log file (txt, log, json, csv)", type=["txt", "log", "json", "csv"])

    analyze = st.button("Analyze")

    if analyze and uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 100:
            st.error("File size exceeds 100 MB limit. Please upload a smaller file.")
            return
        try:
            file_name = uploaded_file.name
            content = uploaded_file.read()
            try:
                log_data = content.decode("utf-8")
            except Exception:
                log_data = str(content)
            st.text_area("Log File Content", log_data, height=300)

            st.markdown("---")
            st.subheader("Output of the Analysis")
            if file_name.endswith('.json'):
                import json
                try:
                    json_data = json.loads(log_data)
                    st.json(json_data)
                except Exception as e:
                    st.warning(f"Could not parse JSON: {e}")
            elif file_name.endswith('.csv'):
                import io
                try:
                    df = pd.read_csv(io.StringIO(log_data))
                    st.dataframe(df)
                except Exception as e:
                    st.warning(f"Could not parse CSV: {e}")
            else:
                lines = log_data.splitlines()
                st.write(f"Number of lines in the log file: {len(lines)}")
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
    elif analyze and uploaded_file is None:
        st.warning("Please upload a log file to analyze.")
if __name__ == "__main__":
    main()

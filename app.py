import streamlit as st
import requests

st.set_page_config(page_title="WordPress CPT Viewer", layout="wide")

# App Title
st.title("📝 WordPress Custom Post Type (CPT) Viewer")

# Description
st.markdown("""
This application allows you to **fetch and display all Custom Post Types (CPTs)** from a given WordPress REST API endpoint.
Simply enter the API URL below and click the **"Fetch CPTs"** button.
""")

# Input URL
default_url = "https://entremotivator.com/wp-json/wp/v2/types"
url = st.text_input("Enter WordPress API URL:", default_url)

# Fetch CPTs Button
if st.button("🔍 Fetch CPTs"):
    with st.spinner("Fetching Custom Post Types..."):
        try:
            # Make API Request
            response = requests.get(url)
            
            # Check if API request is successful
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    st.success(f"✅ Successfully retrieved {len(data)} CPT(s)!")
                    
                    # Display CPTs in a structured format
                    for cpt_key, cpt_data in data.items():
                        with st.expander(f"📌 **{cpt_key.upper()}**"):
                            st.write(f"**🔹 Name:** {cpt_data.get('name', 'N/A')}")
                            st.write(f"**🔹 Description:** {cpt_data.get('description', 'N/A')}")
                            st.write(f"**🔹 REST Namespace:** {cpt_data.get('rest_namespace', 'N/A')}")
                            st.write(f"**🔹 Link to API Endpoint:** [View JSON]({cpt_data.get('_links', {}).get('collection', [{'href': ''}])[0]['href']})")

                            # CPT Labels
                            labels = cpt_data.get("labels", {})
                            if labels:
                                st.subheader("📝 Labels")
                                for label_key, label_value in labels.items():
                                    st.write(f"**{label_key.replace('_', ' ').capitalize()}**: {label_value}")

                            # CPT Capabilities
                            capabilities = cpt_data.get("capabilities", {})
                            if capabilities:
                                st.subheader("🔐 Capabilities")
                                for cap_key, cap_value in capabilities.items():
                                    st.write(f"**{cap_key.replace('_', ' ').capitalize()}**: {cap_value}")

                            st.write("---")
                else:
                    st.warning("⚠️ No Custom Post Types found at this endpoint.")

            else:
                st.error(f"❌ Failed to fetch data. Status Code: {response.status_code}")

        except requests.exceptions.MissingSchema:
            st.error("🚨 Invalid URL! Please enter a valid WordPress API URL.")

        except requests.exceptions.RequestException as e:
            st.error(f"🚨 Error fetching CPTs: {e}")

import streamlit as st
import requests
import json
from urllib.parse import urlparse
import time

# Set page configuration
st.set_page_config(page_title="WordPress CPT Dynamic API Generator", layout="wide")

# App Title and Description
st.title("📌 WordPress Custom Post Types API Generator")
st.markdown("""
This tool dynamically fetches **Custom Post Types (CPTs)** from a WordPress REST API and generates comprehensive API request templates including:
- **Basic Configuration (Authentication & Endpoints)**
- **GET Request Template with Filters**
- **POST Request Template**
- **PUT Request Template (with Dynamic ID)**
- **JavaScript Code for Handling Paginated Responses**
- **JavaScript Field Transformation Function**
- **Agent Code (n8n Format) for automated API interactions**

---

### 🚀 **How to Use:**
1. **Enter the API URL** (Defaults to *EntreMotivator*).
2. **Click "Fetch CPTs and Generate Code"**.
3. **Expand each CPT section to view the generated code snippets.**
""")

# Input for the WordPress API URL (for CPTs)
default_url = "https://entremotivator.com/wp-json/wp/v2/types"
api_url = st.text_input("🔗 Enter the WordPress API URL for CPTs:", default_url)

# Validate URL format
if not api_url.startswith("http"):
    st.error("❌ Invalid URL. Please enter a valid WordPress REST API URL.")
    st.stop()

# Cache the fetched data to avoid redundant API calls
@st.cache_data(ttl=300)
def fetch_cpts(url):
    """Fetch CPTs from the given WordPress REST API URL with retries and extended timeout."""
    retries = 3
    timeout = 100  # Extended timeout of 100 seconds
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"⚠️ HTTP {response.status_code} - {response.reason}")
                return None
        except requests.exceptions.Timeout:
            st.warning(f"⏳ Timeout (Attempt {attempt + 1}/{retries}) - Retrying...")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection Error! Please check your internet connection.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Network Error: {e}")
            return None
        time.sleep(2)
    st.error("🚨 All attempts failed. Unable to fetch CPTs.")
    return None

# On button click, fetch data and generate code snippets
if st.button("🚀 Fetch CPTs and Generate Code"):
    with st.spinner("🔄 Fetching Custom Post Types..."):
        data = fetch_cpts(api_url)

        if data:
            st.success(f"✅ Successfully fetched {len(data)} CPT(s)!")
            
            # Extract base URL from the provided API URL
            parsed_url = urlparse(api_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            st.markdown("## 📜 Generated Dynamic Code Snippets")
            
            # Iterate over each CPT to generate dynamic code sections
            for cpt_slug, details in data.items():
                with st.expander(f"🔹 CPT: {cpt_slug} - {details.get('name', 'N/A')}"):
                    
                    # Define the endpoint URL for this CPT
                    endpoint = f"{base_url}/wp-json/wp/v2/{cpt_slug}"
                    
                    # 1. Basic Configuration (Authentication & Endpoint)
                    basic_config = {
                        "authentication": "basicAuth",
                        "url": endpoint,
                        "headers": {"Content-Type": "application/json"}
                    }
                    st.markdown("### 🔹 Basic Configuration:")
                    st.code(json.dumps(basic_config, indent=2), language="json")
                    
                    # 2. GET Request Template with Query Parameters
                    get_request = {
                        "method": "GET",
                        "qs": {
                            "per_page": 100,
                            "orderby": "date",
                            "order": "desc"
                        }
                    }
                    st.markdown("### 🔍 GET Request Template:")
                    st.code(json.dumps(get_request, indent=2), language="json")
                    
                    # 3. POST Request Template
                    post_request = {
                        "method": "POST",
                        "body": {
                            "title": "{{ $json.title }}",
                            "content": "{{ $json.content }}",
                            "status": "draft",
                            "meta": {"custom_field": "{{ $json.customValue }}"}
                        }
                    }
                    st.markdown("### 📝 POST Request Template:")
                    st.code(json.dumps(post_request, indent=2), language="json")
                    
                    # 4. PUT Request Template (Dynamic ID insertion)
                    put_request = {
                        "method": "PUT",
                        "url": f"{endpoint}/{{{{ $json.id }}}}"
                    }
                    st.markdown("### 🔄 PUT Request Template:")
                    st.code(json.dumps(put_request, indent=2), language="json")
                    
                    # 5. JavaScript Code for Handling Paginated Responses
                    paginated_code = f"""
// JavaScript: Handle paginated responses
const allResults = [];
let page = 1;

do {{
  const response = await $httpRequest({{
    method: 'GET',
    url: `{endpoint}?page=${{page}}`,
    returnFullResponse: true
  }});
  allResults.push(...response.body);
  page++;
}} while(response.headers['x-wp-totalpages'] >= page);

return allResults.map(item => ({{ json: item }}));
"""
                    st.markdown("### 📄 JavaScript: Paginated Responses:")
                    st.code(paginated_code, language="javascript")
                    
                    # 6. JavaScript Function for Field Transformation
                    transformation_code = """
// JavaScript: Field transformation function
return items.map(item => ({
  json: {
    processed_data: {
      ...item.json,
      combined_field: `${item.json.meta.field1} - ${item.json.meta.field2}`
    }
  }
}));
"""
                    st.markdown("### 🔧 JavaScript: Field Transformation:")
                    st.code(transformation_code, language="javascript")
                    
                    # 7. Agent Code (n8n Format) for Automated API Interaction
                    agent_code = {
                        "nodes": [
                            {
                                "parameters": {
                                    "url": endpoint,
                                    "authentication": "predefinedCredentialType",
                                    "nodeCredentialType": "wordpressApi",
                                    "options": {}
                                },
                                "type": "n8n-nodes-base.httpRequest",
                                "typeVersion": 4.2,
                                "position": [140, -20],
                                "id": "983e0dae-6715-4a9b-ab07-1c938e277eba",
                                "name": "HTTP Request",
                                "credentials": {
                                    "wordpressApi": {
                                        "id": "MMY1sVzZsnr23t81",
                                        "name": "Wordpress account"
                                    }
                                }
                            }
                        ],
                        "connections": {},
                        "pinData": {}
                    }
                    st.markdown("### 🤖 Agent Code (n8n Format):")
                    st.code(json.dumps(agent_code, indent=2), language="json")
                    
                    st.markdown("---")
        else:
            st.warning("⚠️ No Custom Post Types found at the provided endpoint.")


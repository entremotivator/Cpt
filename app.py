import streamlit as st
import requests
import json
from urllib.parse import urlparse
import time

# Set page configuration
st.set_page_config(page_title="WordPress CPT Dynamic API Generator", layout="wide")

# App Title and Description
st.title("📌 WordPress Custom Post Types Dynamic API Generator")
st.markdown("""
This tool fetches **Custom Post Types (CPTs)** from a WordPress REST API and generates dynamic API request templates.  
For each CPT, you'll receive:
- ✅ **Basic Configuration (Authentication & Endpoints)**
- 📝 **POST Request Template**
- 🔄 **PUT Request Template (with Dynamic ID)**
- 🔍 **GET Request Template with Filters**
- 📄 **JavaScript Code for Paginated Responses**
- 🔧 **JavaScript Field Transformation Function**

---

### 🚀 **How to Use:**
1. **Enter the API URL** (Defaults to *EntreMotivator*)
2. **Click "Fetch CPTs and Generate Code"**
3. **Copy the generated API snippets and use them!**
""")

# Input for the WordPress API URL (for CPTs)
default_url = "https://entremotivator.com/wp-json/wp/v2/types"
api_url = st.text_input("🔗 Enter the WordPress API URL for CPTs:", default_url)

# Validate URL format
if not api_url.startswith("http"):
    st.error("❌ Invalid URL. Please enter a valid WordPress REST API URL.")
    st.stop()

# Caching API responses to prevent redundant calls
@st.cache_data(ttl=300)  # Cache results for 5 minutes
def fetch_cpts(url):
    """Fetch CPTs from the given WordPress REST API URL with retries."""
    retries = 3
    timeout = 100
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"⚠️ Error: HTTP {response.status_code} - {response.reason}")
                return None
        except requests.exceptions.Timeout:
            st.warning(f"⏳ Timeout Error (Attempt {attempt + 1}/{retries}) - Retrying...")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection Error! Please check your internet connection.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Network Error: {e}")
            return None
        time.sleep(2)  # Wait before retrying
    st.error("🚨 All attempts failed. Unable to fetch CPTs.")
    return None

# On button click, fetch data and generate code snippets
if st.button("🚀 Fetch CPTs and Generate Code"):
    with st.spinner("🔄 Fetching Custom Post Types... Please wait!"):
        data = fetch_cpts(api_url)

        if data:
            st.success(f"✅ Successfully fetched {len(data)} CPT(s)!")
            
            # Extract base URL from the provided API URL
            parsed_url = urlparse(api_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            st.markdown("## 📜 Generated Dynamic Code Snippets")
            
            # Iterate over each CPT and generate dynamic code
            for cpt_slug, details in data.items():
                with st.expander(f"🔹 **CPT: {cpt_slug}** - {details.get('name', 'N/A')}"):
                    
                    # 1. Basic Configuration
                    basic_config = {
                        "authentication": "basicAuth",
                        "url": f"{base_url}/wp-json/wp/v2/{cpt_slug}",
                        "headers": {"Content-Type": "application/json"}
                    }
                    st.markdown("### 🔹 Basic Configuration:")
                    st.code(json.dumps(basic_config, indent=2), language="json")

                    # 2. POST Request
                    post_config = {
                        "method": "POST",
                        "body": {
                            "title": "{{ $json.title }}",
                            "content": "{{ $json.content }}",
                            "status": "draft",
                            "meta": {"custom_field": "{{ $json.customValue }}"}
                        }
                    }
                    st.markdown("### 📝 POST Request Configuration:")
                    st.code(json.dumps(post_config, indent=2), language="json")

                    # 3. PUT Request (Dynamic ID)
                    put_config = {
                        "method": "PUT",
                        "url": f"{base_url}/wp-json/wp/v2/{cpt_slug}/{{{{ $json.id }}}}"
                    }
                    st.markdown("### 🔄 PUT Request Configuration:")
                    st.code(json.dumps(put_config, indent=2), language="json")

                    # 4. GET Request with Query Parameters
                    get_config = {
                        "method": "GET",
                        "qs": {
                            "per_page": 100,
                            "orderby": "date",
                            "order": "desc"
                        }
                    }
                    st.markdown("### 🔍 GET Request with Query Parameters:")
                    st.code(json.dumps(get_config, indent=2), language="json")

                    # 5. JavaScript Code for Handling Paginated Responses
                    paginated_code = f"""
// JavaScript: Handling paginated responses
const allResults = [];
let page = 1;

do {{
  const response = await $httpRequest({{
    method: 'GET',
    url: `{base_url}/wp-json/wp/v2/{cpt_slug}?page=${{page}}`,
    returnFullResponse: true
  }});

  allResults.push(...response.body);
  page++;
}} while(response.headers['x-wp-totalpages'] >= page);

return allResults.map(item => ({{ json: item }}));
"""
                    st.markdown("### 📄 JavaScript Code for Paginated Responses:")
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
                    st.markdown("### 🔧 JavaScript Function for Field Transformation:")
                    st.code(transformation_code, language="javascript")

                    st.markdown("---")  # Divider

        else:
            st.warning("⚠️ No Custom Post Types found at the provided endpoint.")

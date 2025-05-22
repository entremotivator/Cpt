import streamlit as st
import requests
import json
from urllib.parse import urlparse
import time

# Page Configuration
st.set_page_config(page_title="Advanced WordPress CPT API & n8n Agent Generator", layout="wide")

# App Title and Description
st.title("📌 Advanced WordPress CPT API & n8n Agent Generator")
st.markdown("""
This tool fetches **Custom Post Types (CPTs)** from a WordPress REST API and generates:
- ✅ Auth & endpoint config
- 🔍 GET/POST/PUT/DELETE request templates
- 🧠 JavaScript for pagination, field extraction, transformations
- 🤖 n8n workflow starter snippets

---

### 🚀 How to Use:
1. Enter the WordPress API URL (defaults to *EntreMotivator*)
2. Click **Fetch CPTs and Generate Code**
3. Expand each CPT to explore full code templates
""")

# Default API endpoint
default_url = "https://entremotivator.com/wp-json/wp/v2/types"
api_url = st.text_input("🔗 Enter the WordPress API URL for CPTs:", default_url)

# Validate URL input
if not api_url.startswith("http"):
    st.error("❌ Invalid URL. Please enter a valid WordPress REST API URL.")
    st.stop()

# Cached CPT fetcher
@st.cache_data(ttl=300)
def fetch_cpts(url):
    retries = 3
    timeout = 100
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

# Trigger fetching and generation
if st.button("🚀 Fetch CPTs and Generate Code"):
    with st.spinner("🔄 Fetching Custom Post Types..."):
        data = fetch_cpts(api_url)

    if data:
        if not isinstance(data, dict):
            st.error("❌ Unexpected API response format. Expected a dictionary of CPTs.")
            st.json(data)
            st.stop()

        st.success(f"✅ Successfully fetched {len(data)} CPT(s)!")
        parsed_url = urlparse(api_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        st.markdown("## 📜 Generated Dynamic Code Snippets")

        for cpt_slug, details in data.items():
            # Fallback if details is not a dictionary
            name = details.get('name', 'N/A') if isinstance(details, dict) else 'N/A'
            endpoint = f"{base_url}/wp-json/wp/v2/{cpt_slug}"

            with st.expander(f"🔹 CPT: {cpt_slug} - {name}"):
                # 1. Basic Configuration
                basic_config = {
                    "authentication": "basicAuth",
                    "url": endpoint,
                    "headers": {"Content-Type": "application/json"}
                }
                st.markdown("### 🔹 Basic Configuration:")
                st.code(json.dumps(basic_config, indent=2), language="json")

                # 2. GET Request Template
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
                        "excerpt": "{{ $json.excerpt }}",
                        "status": "{{ $json.status | default('draft') }}",
                        "slug": "{{ $json.slug }}",
                        "author": "{{ $json.author }}",
                        "featured_media": "{{ $json.featured_media }}",
                        "categories": "{{ $json.categories }}",
                        "tags": "{{ $json.tags }}",
                        "date": "{{ $json.date }}",
                        "date_gmt": "{{ $json.date_gmt }}",
                        "modified": "{{ $json.modified }}",
                        "modified_gmt": "{{ $json.modified_gmt }}",
                        "meta": {
                            "custom_field1": "{{ $json.custom_field1 }}",
                            "custom_field2": "{{ $json.custom_field2 }}",
                            "additional_field": "{{ $json.additional_field }}"
                        }
                    }
                }
                st.markdown("### 📝 POST Request Template (Create New CPT):")
                st.code(json.dumps(post_request, indent=2), language="json")

                # 4. PUT Request Template
                put_request = {
                    "method": "PUT",
                    "url": f"{endpoint}/{{{{ $json.id }}}}",
                    "body": post_request["body"]
                }
                st.markdown("### 🔄 PUT Request Template (Update CPT):")
                st.code(json.dumps(put_request, indent=2), language="json")

                # 5. DELETE Request Template
                delete_request = {
                    "method": "DELETE",
                    "url": f"{endpoint}/{{{{ $json.id }}}}",
                    "qs": {
                        "force": True
                    }
                }
                st.markdown("### 🗑️ DELETE Request Template:")
                st.code(json.dumps(delete_request, indent=2), language="json")

                # 6. JavaScript: Pagination Handler
                js_pagination = f"""
// JavaScript: Handle paginated results for '{cpt_slug}'
const allResults = [];
let page = 1;
let totalPages = 1;

do {{
  const response = await $httpRequest({{
    method: 'GET',
    url: '{endpoint}',
    qs: {{
      per_page: 100,
      page: page
    }}
  }});
  
  allResults.push(...response.body);
  totalPages = parseInt(response.headers['x-wp-totalpages'] || 1);
  page++;
}} while (page <= totalPages);

return allResults;
"""
                st.markdown("### 🔁 JavaScript for Paginated Fetch:")
                st.code(js_pagination, language="javascript")

                # 7. JavaScript: Extract Custom Fields
                js_custom_fields = """
// Extract all meta/custom fields from a CPT item
function extractCustomFields(item) {
  const meta = item.meta || {};
  const fields = {};
  for (const key in meta) {
    fields[key] = meta[key];
  }
  return fields;
}
"""
                st.markdown("### 🧬 JavaScript to Extract Custom Fields:")
                st.code(js_custom_fields, language="javascript")


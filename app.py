import streamlit as st
import requests
import json
from urllib.parse import urlparse
import time

st.set_page_config(page_title="Advanced WordPress CPT API & n8n Agent Generator", layout="wide")

st.title("📌 Advanced WordPress CPT API & n8n Agent Generator")
st.markdown("""
This interactive tool dynamically fetches **Custom Post Types (CPTs)** from a WordPress REST API and generates comprehensive API request templates.

---

### 🚀 **How to Use:**
1. **Enter the WordPress API URL** (Defaults to *EntreMotivator*).
2. **Click "Fetch CPTs and Generate Code"**.
3. **Expand each CPT section to view the generated code snippets and agent workflows.**
""")

default_url = "https://entremotivator.com/wp-json/wp/v2/types"
api_url = st.text_input("🔗 Enter the WordPress API URL for CPTs:", default_url)

if not api_url.startswith("http"):
    st.error("❌ Invalid URL. Please enter a valid WordPress REST API URL.")
    st.stop()

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

def is_valid_cpt(details):
    # Valid CPTs have a 'rest_base' and a 'name'
    return isinstance(details, dict) and 'rest_base' in details and 'name' in details

if st.button("🚀 Fetch CPTs and Generate Code"):
    with st.spinner("🔄 Fetching Custom Post Types..."):
        data = fetch_cpts(api_url)

        if not isinstance(data, dict):
            st.error("❌ The API did not return the expected data structure. Please check the API endpoint.")
            st.write("Raw API response:", data)
        else:
            # Filter only valid CPTs
            cpt_items = [(slug, details) for slug, details in data.items() if is_valid_cpt(details)]
            if not cpt_items:
                st.warning("⚠️ No valid Custom Post Types found in the API response.")
                st.write("Raw API response:", data)
            else:
                st.success(f"✅ Found {len(cpt_items)} CPT(s): " + ", ".join([slug for slug, _ in cpt_items]))
                parsed_url = urlparse(api_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                st.markdown("## 📜 Generated Dynamic Code Snippets")

                for cpt_slug, details in cpt_items:
                    with st.expander(f"🔹 CPT: {cpt_slug} - {details.get('name', 'N/A')}"):
                        endpoint = f"{base_url}/wp-json/wp/v2/{cpt_slug}"

                        basic_config = {
                            "authentication": "basicAuth",
                            "url": endpoint,
                            "headers": {"Content-Type": "application/json"}
                        }
                        st.markdown("### 🔹 Basic Configuration:")
                        st.code(json.dumps(basic_config, indent=2), language="json")

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
                        st.markdown("### 📝 POST Request Template (Create New CPT with All Fields):")
                        st.code(json.dumps(post_request, indent=2), language="json")

                        put_request = {
                            "method": "PUT",
                            "url": f"{endpoint}/{{{{ $json.id }}}}",
                            "body": post_request["body"]
                        }
                        st.markdown("### 🔄 PUT Request Template (Update Existing CPT Entry):")
                        st.code(json.dumps(put_request, indent=2), language="json")

                        delete_request = {
                            "method": "DELETE",
                            "url": f"{endpoint}/{{{{ $json.id }}}}",
                            "qs": {
                                "force": True
                            }
                        }
                        st.markdown("### 🗑️ DELETE Request Template:")
                        st.code(json.dumps(delete_request, indent=2), language="json")

                        paginated_code = f"""
// JavaScript: Handle paginated responses for CPT '{cpt_slug}'
const allResults = [];
let page = 1;
let totalPages = 1;
do {{
  const response = await $httpRequest({{
    method: 'GET',
    url: '{endpoint}?page=' + page + '&per_page=100',
    returnFullResponse: true
  }});
  totalPages = parseInt(response.headers['x-wp-totalpages'] || '1', 10);
  allResults.push(...response.body);
  page++;
}} while(page <= totalPages);
return allResults.map(item => ({{ json: item }}));
"""
                        st.markdown("### 📄 JavaScript: Paginated Responses:")
                        st.code(paginated_code, language="javascript")

                        transformation_code = """
// JavaScript: Transform fields and combine meta values for enhanced processing
return items.map(item => ({
  json: {
    ...item.json,
    combined_field: `${item.json.meta.custom_field1} - ${item.json.meta.custom_field2}`
  }
}));
"""
                        st.markdown("### 🔧 JavaScript: Field Transformation:")
                        st.code(transformation_code, language="javascript")

                        custom_fields_code = """
// JavaScript: Extract and list all custom fields (meta data) for each CPT entry
return items.map(item => {
  const meta = item.json.meta || {};
  const customFields = Object.keys(meta).reduce((acc, key) => {
    acc[key] = meta[key];
    return acc;
  }, {});
  return { json: { ...item.json, customFields } };
});
"""
                        st.markdown("### 🔍 JavaScript: Extract All Custom Fields:")
                        st.code(custom_fields_code, language="javascript")

                        agent_code = {
                            "nodes": [
                                {
                                    "parameters": {
                                        "url": endpoint,
                                        "method": "GET",
                                        "queryParameters": [
                                            {"name": "per_page", "value": "100"},
                                            {"name": "page", "value": "1"}
                                        ]
                                    },
                                    "name": "Fetch CPT Data",
                                    "type": "n8n-nodes-base.httpRequest",
                                    "typeVersion": 2,
                                    "position": [250, 200]
                                },
                                {
                                    "parameters": {
                                        "functionCode": (
                                            "// Function to handle pagination and collate all pages\\n"
                                            "const allData = [];\\n"
                                            "let currentPage = 1;\\n"
                                            "let totalPages = parseInt($node['Fetch CPT Data'].json['x-wp-totalpages'] || '1', 10);\\n\\n"
                                            "while (currentPage <= totalPages) {\\n"
                                            "  // In a real scenario, you would fetch each page here\\n"
                                            "  allData.push(...$node['Fetch CPT Data'].json);\\n"
                                            "  currentPage++;\\n"
                                            "}\\n\\n"
                                            "return allData.map(data => ({ json: data }));"
                                        )
                                    },
                                    "name": "Handle Pagination",
                                    "type": "n8n-nodes-base.function",
                                    "typeVersion": 1,
                                    "position": [500, 200]
                                },
                                {
                                    "parameters": {
                                        "url": f"{endpoint}/{{{{ $json.id }}}}",
                                        "method": "PUT",
                                        "body": post_request["body"]
                                    },
                                    "name": "Update CPT Entry",
                                    "type": "n8n-nodes-base.httpRequest",
                                    "typeVersion": 2,
                                    "position": [750, 200]
                                },
                                {
                                    "parameters": {
                                        "url": f"{endpoint}/{{{{ $json.id }}}}",
                                        "method": "DELETE",
                                        "queryParameters": [
                                            {"name": "force", "value": "true"}
                                        ]
                                    },
                                    "name": "Delete CPT Entry",
                                    "type": "n8n-nodes-base.httpRequest",
                                    "typeVersion": 2,
                                    "position": [750, 400]
                                }
                            ],
                            "connections": {}
                        }
                        st.markdown("### 🤖 n8n Agent Workflow:")
                        st.code(json.dumps(agent_code, indent=2), language="json")

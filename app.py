import streamlit as st
import requests
import json
from urllib.parse import urlparse
import time

# Set advanced page configuration
st.set_page_config(page_title="Advanced WordPress CPT API & n8n Agent Generator", layout="wide")

# App Title and Description
st.title("📌 Advanced WordPress CPT API & n8n Agent Generator")
st.markdown("""
This interactive tool dynamically fetches **Custom Post Types (CPTs)** from a WordPress REST API and generates comprehensive API request templates including:
- **Basic Configuration (Authentication & Endpoints)**
- **GET Request Template with Query Parameters**
- **POST Request Template for creating new CPT entries (with all available fields)**
- **PUT Request Template (with Dynamic ID) for updating entries**
- **DELETE Request Template for removing entries**
- **JavaScript Code for Handling Paginated Responses**
- **JavaScript Field Transformation Function**
- **JavaScript Code to Extract and List All Custom Fields (Meta)**
- **Advanced Agent Workflow (n8n Format) for automated API interactions**  

The POST and PUT request templates below include placeholders for every commonly used field. Additionally, the JavaScript snippet demonstrates how to extract all custom (meta) fields from each CPT entry, ensuring you can dynamically pull and work with all custom data available.

---

### 🚀 **How to Use:**
1. **Enter the WordPress API URL** (Defaults to *EntreMotivator*).
2. **Click "Fetch CPTs and Generate Code"**.
3. **Expand each CPT section to view the generated code snippets and agent workflows.**
""")

# Input for the WordPress API URL (for CPTs)
default_url = "https://entremotivator.com/wp-json/wp/v2/types"
api_url = st.text_input("🔗 Enter the WordPress API URL for CPTs:", default_url)

# Validate URL format
if not api_url.startswith("http"):
    st.error("❌ Invalid URL. Please enter a valid WordPress REST API URL.")
    st.stop()

# Function to fetch CPTs with caching and retry logic
@st.cache_data(ttl=300)
def fetch_cpts(url):
    """
    Fetch CPTs from the given WordPress REST API URL using retries and an extended timeout.
    """
    retries = 3
    timeout = 100  # Extended timeout in seconds
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
            
            # Extract the base URL from the provided API URL
            parsed_url = urlparse(api_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            st.markdown("## 📜 Generated Dynamic Code Snippets")
            
            # Loop through each CPT to create dynamic code sections
            for cpt_slug, details in data.items():
                with st.expander(f"🔹 CPT: {cpt_slug} - {details.get('name', 'N/A')}"):
                    
                    # Define the endpoint URL for the current CPT
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
                    
                    # 3. Extended POST Request Template for Creating a New CPT Entry with All Fields
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
                    
                    # 4. PUT Request Template (Dynamic ID) for Updating a CPT Entry
                    put_request = {
                        "method": "PUT",
                        "url": f"{endpoint}/{{{{ $json.id }}}}",
                        "body": {
                            "title": "{{ $json.title }}",
                            "content": "{{ $json.content }}",
                            "excerpt": "{{ $json.excerpt }}",
                            "status": "{{ $json.status }}",
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
                    st.markdown("### 🔄 PUT Request Template (Update Existing CPT Entry):")
                    st.code(json.dumps(put_request, indent=2), language="json")
                    
                    # 5. DELETE Request Template for Removing a CPT Entry
                    delete_request = {
                        "method": "DELETE",
                        "url": f"{endpoint}/{{{{ $json.id }}}}",
                        "qs": {
                            "force": True
                        }
                    }
                    st.markdown("### 🗑️ DELETE Request Template:")
                    st.code(json.dumps(delete_request, indent=2), language="json")
                    
                    # 6. JavaScript Code for Handling Paginated Responses
                    paginated_code = f"""
// JavaScript: Handle paginated responses for CPT '{cpt_slug}'
const allResults = [];
let page = 1;
let totalPages = 1;

do {{
  const response = await $httpRequest({{
    method: 'GET',
    url: `{endpoint}?page=${{page}}&per_page=100`,
    returnFullResponse: true
  }});
  
  // Determine total number of pages from response headers
  totalPages = parseInt(response.headers['x-wp-totalpages'] || '1', 10);
  allResults.push(...response.body);
  page++;
}} while(page <= totalPages);

return allResults.map(item => ({{ json: item }}));
"""
                    st.markdown("### 📄 JavaScript: Paginated Responses:")
                    st.code(paginated_code, language="javascript")
                    
                    # 7. JavaScript Function for Field Transformation
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
                    
                    # 8. JavaScript Code to Extract and List All Custom Fields
                    custom_fields_code = """
// JavaScript: Extract and list all custom fields (meta data) for each CPT entry
return items.map(item => {
  const meta = item.json.meta || {};
  // Build a simple object containing all custom field key-value pairs
  const customFields = Object.keys(meta).reduce((acc, key) => {
    acc[key] = meta[key];
    return acc;
  }, {});
  return { json: { ...item.json, customFields } };
});
"""
                    st.markdown("### 🔍 JavaScript: Extract All Custom Fields:")
                    st.code(custom_fields_code, language="javascript")
                    
                    # 9. Advanced Agent Workflow (n8n Format) for Automated API Interaction
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
                                    "body": {
                                        "title": "{{ $json.title }}",
                                        "content": "{{ $json.content }}",
                                        "excerpt": "{{ $json.excerpt }}",
                                        "status": "{{ $json.status }}",
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
                        "connections": {
                            "Fetch CPT Data": {
                                "main": [
                                    [
                                        {"node": "Handle Pagination", "type": "main", "index": 0}
                                    ]
                                ]
                            },
                            "Handle Pagination": {
                                "main": [
                                    [
                                        {"node": "Update CPT Entry", "type": "main", "index": 0},
                                        {"node": "Delete CPT Entry", "type": "main", "index": 0}
                                    ]
                                ]
                            }
                        }
                    }
                    st.markdown("### 🤖 Advanced Agent Workflow (n8n Format):")
                    st.code(json.dumps(agent_code, indent=2), language="json")
                    
                    st.markdown("---")
        else:
            st.warning("⚠️ No Custom Post Types found at the provided endpoint.")

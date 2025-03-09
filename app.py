import streamlit as st
import requests
from urllib.parse import urlparse

# Set page configuration
st.set_page_config(page_title="WordPress CPT Dynamic Links Generator", layout="wide")

# App Title and Description
st.title("WordPress Custom Post Types Dynamic Links Generator")
st.markdown("""
This application fetches **Custom Post Types (CPTs)** from a WordPress REST API endpoint and generates dynamic code snippets for interacting with each CPT.  
For every post type, you’ll get:
- A **basic configuration** snippet (with authentication and the GET endpoint)
- A **POST request** configuration
- A **PUT request** configuration (with dynamic ID insertion)
- A **GET request** snippet with query parameters
- A **JavaScript code node** for handling paginated responses
- A **JavaScript function node** for field transformation

Simply enter the API URL below (defaults to *EntreMotivator*) and click the **"Fetch CPTs and Generate Code"** button.
""")

# Input for the WordPress API URL (for CPTs)
default_url = "https://entremotivator.com/wp-json/wp/v2/types"
api_url = st.text_input("Enter the WordPress API URL for CPTs:", default_url)

# On button click, fetch data and generate code snippets
if st.button("Fetch CPTs and Generate Code"):
    with st.spinner("Fetching Custom Post Types..."):
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    st.success(f"Fetched {len(data)} CPT(s) successfully!")
                    
                    # Extract base URL from the provided API URL
                    parsed_url = urlparse(api_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    
                    st.markdown("### Generated Dynamic Code Snippets for Each CPT")
                    
                    # Iterate over each CPT to generate its dynamic code blocks
                    for cpt_slug, details in data.items():
                        st.markdown(f"## CPT: **{cpt_slug}** - {details.get('name', 'N/A')}")
                        
                        # 1. Basic Configuration with Authentication and GET endpoint
                        basic_config = f'''{{
  "authentication": "basicAuth",
  "url": "{base_url}/wp-json/wp/v2/{cpt_slug}",
  "headers": {{
    "Content-Type": "application/json"
  }}
}}'''
                        st.markdown("**Basic Configuration:**")
                        st.code(basic_config, language="json")
                        
                        # 2. POST Request Configuration
                        post_config = '''{
  "method": "POST",
  "body": {
    "title": "{{ $json.title }}",
    "content": "{{ $json.content }}",
    "status": "draft",
    "meta": {
      "custom_field": "{{ $json.customValue }}"
    }
  }
}'''
                        st.markdown("**POST Request Configuration:**")
                        st.code(post_config, language="json")
                        
                        # 3. PUT Request Configuration (using dynamic id)
                        put_config = f'''{{
  "method": "PUT",
  "url": "{base_url}/wp-json/wp/v2/{cpt_slug}/{{{{ $json.id }}}}"
}}'''
                        st.markdown("**PUT Request Configuration:**")
                        st.code(put_config, language="json")
                        
                        # 4. GET Request with Query Parameters
                        get_config = '''{
  "method": "GET",
  "qs": {
    "per_page": 100,
    "orderby": "date",
    "order": "desc"
  }
}'''
                        st.markdown("**GET Request with Query Parameters:**")
                        st.code(get_config, language="json")
                        
                        # 5. Code Node for Handling Paginated Responses (JavaScript)
                        paginated_code = f'''// Code node to handle paginated responses
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

return allResults.map(item => ({{ json: item }}));'''
                        st.markdown("**Code Node for Handling Paginated Responses:**")
                        st.code(paginated_code, language="javascript")
                        
                        # 6. Function Node for Field Transformation (JavaScript)
                        transformation_code = '''// Function node for field transformation
return items.map(item => ({
  json: {
    processed_data: {
      ...item.json,
      combined_field: `${item.json.meta.field1} - ${item.json.meta.field2}`
    }
  }
}));'''
                        st.markdown("**Function Node for Field Transformation:**")
                        st.code(transformation_code, language="javascript")
                        
                        st.markdown("---")
                else:
                    st.warning("No Custom Post Types found at the provided endpoint.")
            else:
                st.error(f"Error fetching data: HTTP {response.status_code}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

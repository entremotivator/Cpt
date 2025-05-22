import streamlit as st
import requests
import json
from urllib.parse import urlparse, urljoin
import time
from datetime import datetime, timezone
import base64
import hashlib
import re
from typing import Dict, List, Optional, Any

# Set advanced page configuration
st.set_page_config(
    page_title="Advanced WordPress CPT API & n8n Agent Generator", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://developer.wordpress.org/rest-api/',
        'Report a bug': None,
        'About': "Advanced WordPress CPT API Generator with n8n Integration"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .code-section {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .success-banner {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-banner {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App Title and Description
st.markdown("""
<div class="main-header">
    <h1>🚀 Advanced WordPress CPT API & n8n Agent Generator</h1>
    <p>Comprehensive tool for WordPress REST API integration with automated workflow generation</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Authentication Settings
    st.subheader("🔐 Authentication")
    auth_type = st.selectbox(
        "Authentication Type:",
        ["None", "Basic Auth", "Application Password", "JWT Token", "OAuth 2.0"]
    )
    
    if auth_type == "Basic Auth":
        username = st.text_input("Username:", placeholder="your-username")
        password = st.text_input("Password:", type="password", placeholder="your-password")
    elif auth_type == "Application Password":
        app_username = st.text_input("Application Username:", placeholder="your-username")
        app_password = st.text_input("Application Password:", type="password", placeholder="xxxx xxxx xxxx xxxx")
    elif auth_type == "JWT Token":
        jwt_token = st.text_input("JWT Token:", type="password", placeholder="your-jwt-token")
    elif auth_type == "OAuth 2.0":
        client_id = st.text_input("Client ID:", placeholder="your-client-id")
        client_secret = st.text_input("Client Secret:", type="password", placeholder="your-client-secret")
    
    # Advanced Options
    st.subheader("🔧 Advanced Options")
    timeout_duration = st.slider("Request Timeout (seconds):", 10, 300, 100)
    max_retries = st.slider("Max Retries:", 1, 10, 3)
    items_per_page = st.slider("Items per Page:", 10, 100, 50)
    
    # Custom Headers
    st.subheader("📋 Custom Headers")
    custom_headers_text = st.text_area(
        "Custom Headers (JSON format):",
        placeholder='{"X-Custom-Header": "value", "User-Agent": "My-App/1.0"}',
        height=100
    )
    
    # Export Options
    st.subheader("📤 Export Options")
    export_format = st.selectbox(
        "Export Format:",
        ["JSON", "YAML", "Postman Collection", "Insomnia Collection"]
    )
    
    include_examples = st.checkbox("Include Example Data", value=True)
    include_documentation = st.checkbox("Include Documentation", value=True)

# Main Content
st.markdown("""
## 📖 Features Overview

<div class="feature-box">
<strong>🎯 Dynamic CPT Discovery:</strong> Automatically detects and analyzes all Custom Post Types from your WordPress site
</div>

<div class="feature-box">
<strong>🔧 Complete CRUD Operations:</strong> Generates templates for Create, Read, Update, and Delete operations with full field mapping
</div>

<div class="feature-box">
<strong>🤖 n8n Workflow Generation:</strong> Creates ready-to-use n8n workflows for automated API interactions
</div>

<div class="feature-box">
<strong>📊 Advanced Data Processing:</strong> Includes pagination handling, field transformation, and custom meta extraction
</div>

<div class="feature-box">
<strong>🔐 Multiple Authentication Methods:</strong> Supports various WordPress authentication mechanisms
</div>

<div class="feature-box">
<strong>📱 Export & Integration:</strong> Multiple export formats for easy integration with different tools
</div>

---

### 🚀 **How to Use:**
1. **Configure Authentication** in the sidebar (if required)
2. **Enter your WordPress API URL** below
3. **Adjust advanced settings** as needed
4. **Click "Generate Complete API Documentation"**
5. **Explore generated code snippets and workflows**
6. **Export in your preferred format**
""", unsafe_allow_html=True)

# Input for the WordPress API URL
st.subheader("🌐 WordPress Site Configuration")

col1, col2 = st.columns([3, 1])
with col1:
    default_url = "https://entremotivator.com/wp-json/wp/v2/types"
    api_url = st.text_input(
        "🔗 WordPress API URL for CPTs:",
        value=default_url,
        help="Enter the full URL to your WordPress REST API types endpoint"
    )

with col2:
    auto_detect = st.checkbox("Auto-detect", help="Automatically detect API endpoint from domain")

# URL validation and processing
if auto_detect and api_url:
    parsed_url = urlparse(api_url)
    if parsed_url.netloc:
        auto_url = f"{parsed_url.scheme}://{parsed_url.netloc}/wp-json/wp/v2/types"
        if auto_url != api_url:
            st.info(f"🔄 Auto-detected URL: {auto_url}")
            api_url = auto_url

# Validate URL format
if api_url and not api_url.startswith("http"):
    st.error("❌ Invalid URL. Please enter a valid WordPress REST API URL.")
    st.stop()

# Enhanced CPT fetching function with authentication and advanced error handling
@st.cache_data(ttl=300, show_spinner=False)
def fetch_cpts_advanced(url: str, auth_config: Dict[str, Any], headers: Dict[str, str], timeout: int, retries: int) -> Optional[Dict]:
    """
    Enhanced CPT fetching with comprehensive authentication and error handling
    """
    session = requests.Session()
    
    # Set up authentication
    if auth_config.get('type') == 'Basic Auth':
        session.auth = (auth_config.get('username', ''), auth_config.get('password', ''))
    elif auth_config.get('type') == 'Application Password':
        credentials = f"{auth_config.get('username', '')}:{auth_config.get('password', '')}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers['Authorization'] = f'Basic {encoded_credentials}'
    elif auth_config.get('type') == 'JWT Token':
        headers['Authorization'] = f'Bearer {auth_config.get("token", "")}'
    
    # Set custom headers
    session.headers.update(headers)
    
    for attempt in range(retries):
        try:
            with st.spinner(f"🔄 Fetching CPTs (Attempt {attempt + 1}/{retries})..."):
                response = session.get(url, timeout=timeout)
                
                if response.status_code == 200:
                    return {
                        'data': response.json(),
                        'headers': dict(response.headers),
                        'status_code': response.status_code,
                        'url': response.url
                    }
                elif response.status_code == 401:
                    st.error("🔐 Authentication failed. Please check your credentials.")
                    return None
                elif response.status_code == 403:
                    st.error("🚫 Access forbidden. You may not have permission to access this endpoint.")
                    return None
                elif response.status_code == 404:
                    st.error("🔍 Endpoint not found. Please verify the URL is correct.")
                    return None
                else:
                    st.warning(f"⚠️ HTTP {response.status_code} - {response.reason}")
                    
        except requests.exceptions.Timeout:
            st.warning(f"⏳ Request timeout (Attempt {attempt + 1}/{retries})")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error. Please check your internet connection and URL.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Request error: {str(e)}")
            
        if attempt < retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    st.error("🚨 All attempts failed. Unable to fetch CPTs.")
    return None

# Function to analyze CPT structure
def analyze_cpt_structure(cpt_data: Dict) -> Dict[str, Any]:
    """
    Analyze CPT structure to extract detailed information
    """
    analysis = {
        'total_cpts': len(cpt_data),
        'public_cpts': [],
        'private_cpts': [],
        'hierarchical_cpts': [],
        'supports': {},
        'taxonomies': {},
        'capabilities': {}
    }
    
    for slug, details in cpt_data.items():
        if details.get('public', False):
            analysis['public_cpts'].append(slug)
        else:
            analysis['private_cpts'].append(slug)
            
        if details.get('hierarchical', False):
            analysis['hierarchical_cpts'].append(slug)
            
        analysis['supports'][slug] = details.get('supports', [])
        analysis['taxonomies'][slug] = details.get('taxonomies', [])
        analysis['capabilities'][slug] = details.get('cap', {})
    
    return analysis

# Function to generate comprehensive field mapping
def generate_field_mapping(cpt_slug: str, supports: List[str]) -> Dict[str, Any]:
    """
    Generate comprehensive field mapping based on CPT supports
    """
    base_fields = {
        'id': {'type': 'integer', 'readonly': True, 'description': 'Unique identifier for the post'},
        'date': {'type': 'string', 'format': 'date-time', 'description': 'The date the post was published'},
        'date_gmt': {'type': 'string', 'format': 'date-time', 'description': 'The date the post was published, as GMT'},
        'guid': {'type': 'object', 'readonly': True, 'description': 'The globally unique identifier for the post'},
        'modified': {'type': 'string', 'format': 'date-time', 'readonly': True, 'description': 'The date the post was last modified'},
        'modified_gmt': {'type': 'string', 'format': 'date-time', 'readonly': True, 'description': 'The date the post was last modified, as GMT'},
        'password': {'type': 'string', 'description': 'A password to protect access to the content and excerpt'},
        'slug': {'type': 'string', 'description': 'An alphanumeric identifier for the post unique to its type'},
        'status': {'type': 'string', 'enum': ['publish', 'future', 'draft', 'pending', 'private'], 'description': 'A named status for the post'},
        'type': {'type': 'string', 'readonly': True, 'description': 'Type of post'},
        'link': {'type': 'string', 'format': 'uri', 'readonly': True, 'description': 'URL to the post'},
        'meta': {'type': 'object', 'description': 'Meta fields'}
    }
    
    # Add conditional fields based on supports
    if 'title' in supports:
        base_fields['title'] = {'type': 'object', 'description': 'The title for the post'}
    
    if 'editor' in supports:
        base_fields['content'] = {'type': 'object', 'description': 'The content for the post'}
    
    if 'excerpt' in supports:
        base_fields['excerpt'] = {'type': 'object', 'description': 'The excerpt for the post'}
    
    if 'author' in supports:
        base_fields['author'] = {'type': 'integer', 'description': 'The ID for the author of the post'}
    
    if 'thumbnail' in supports:
        base_fields['featured_media'] = {'type': 'integer', 'description': 'The ID of the featured media for the post'}
    
    if 'comments' in supports:
        base_fields['comment_status'] = {'type': 'string', 'enum': ['open', 'closed'], 'description': 'Whether or not comments are open on the post'}
        base_fields['ping_status'] = {'type': 'string', 'enum': ['open', 'closed'], 'description': 'Whether or not the post can be pinged'}
    
    if 'page-attributes' in supports:
        base_fields['menu_order'] = {'type': 'integer', 'description': 'The order of the post in relation to other posts'}
        base_fields['parent'] = {'type': 'integer', 'description': 'The ID for the parent of the post'}
    
    return base_fields

# Function to generate advanced JavaScript utilities
def generate_javascript_utilities(cpt_slug: str, endpoint: str) -> Dict[str, str]:
    """
    Generate comprehensive JavaScript utility functions
    """
    utilities = {}
    
    # Pagination handler
    utilities['pagination'] = f'''
// Advanced Pagination Handler for {cpt_slug}
class WordPressPagination {{
    constructor(endpoint, options = {{}}) {{
        this.endpoint = endpoint;
        this.options = {{
            perPage: 100,
            timeout: 30000,
            retryAttempts: 3,
            ...options
        }};
    }}
    
    async fetchAllPages() {{
        const allResults = [];
        let page = 1;
        let totalPages = 1;
        
        do {{
            try {{
                const response = await this.fetchPage(page);
                totalPages = parseInt(response.headers['x-wp-totalpages'] || '1', 10);
                allResults.push(...response.data);
                page++;
            }} catch (error) {{
                console.error(`Error fetching page ${{page}}:`, error);
                break;
            }}
        }} while (page <= totalPages);
        
        return allResults;
    }}
    
    async fetchPage(page) {{
        const url = `${{this.endpoint}}?page=${{page}}&per_page=${{this.options.perPage}}`;
        
        for (let attempt = 1; attempt <= this.options.retryAttempts; attempt++) {{
            try {{
                const response = await fetch(url, {{
                    timeout: this.options.timeout
                }});
                
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const data = await response.json();
                return {{
                    data,
                    headers: Object.fromEntries(response.headers.entries())
                }};
            }} catch (error) {{
                if (attempt === this.options.retryAttempts) {{
                    throw error;
                }}
                await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
            }}
        }}
    }}
}}

// Usage
const paginator = new WordPressPagination('{endpoint}');
const allData = await paginator.fetchAllPages();
'''
    
    # Data transformer
    utilities['transformer'] = f'''
// Advanced Data Transformer for {cpt_slug}
class DataTransformer {{
    static extractCustomFields(item) {{
        const meta = item.meta || {{}};
        const customFields = {{}};
        
        // Extract all meta fields
        for (const [key, value] of Object.entries(meta)) {{
            if (!key.startsWith('_') && value !== '') {{
                customFields[key] = value;
            }}
        }}
        
        return customFields;
    }}
    
    static normalizeContent(item) {{
        return {{
            ...item,
            title: item.title?.rendered || item.title || '',
            content: item.content?.rendered || item.content || '',
            excerpt: item.excerpt?.rendered || item.excerpt || '',
            customFields: this.extractCustomFields(item),
            permalink: item.link || '',
            publishDate: new Date(item.date),
            modifiedDate: new Date(item.modified)
        }};
    }}
    
    static transformForExport(items) {{
        return items.map(item => {{
            const normalized = this.normalizeContent(item);
            return {{
                id: normalized.id,
                title: normalized.title,
                content: normalized.content,
                excerpt: normalized.excerpt,
                status: normalized.status,
                author: normalized.author,
                publishDate: normalized.publishDate.toISOString(),
                customFields: normalized.customFields
            }};
        }});
    }}
}}

// Usage
const transformedData = items.map(item => DataTransformer.normalizeContent(item));
'''
    
    # Batch operations
    utilities['batch_operations'] = f'''
// Batch Operations Handler for {cpt_slug}
class BatchOperations {{
    constructor(endpoint, authHeaders = {{}}) {{
        this.endpoint = endpoint;
        this.authHeaders = authHeaders;
        this.batchSize = 10;
    }}
    
    async batchCreate(items) {{
        const results = [];
        const batches = this.chunkArray(items, this.batchSize);
        
        for (const batch of batches) {{
            const batchPromises = batch.map(item => this.createSingle(item));
            const batchResults = await Promise.allSettled(batchPromises);
            results.push(...batchResults);
        }}
        
        return results;
    }}
    
    async batchUpdate(items) {{
        const results = [];
        const batches = this.chunkArray(items, this.batchSize);
        
        for (const batch of batches) {{
            const batchPromises = batch.map(item => this.updateSingle(item));
            const batchResults = await Promise.allSettled(batchPromises);
            results.push(...batchResults);
        }}
        
        return results;
    }}
    
    async createSingle(item) {{
        const response = await fetch(this.endpoint, {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                ...this.authHeaders
            }},
            body: JSON.stringify(item)
        }});
        
        return response.json();
    }}
    
    async updateSingle(item) {{
        const response = await fetch(`${{this.endpoint}}/${{item.id}}`, {{
            method: 'PUT',
            headers: {{
                'Content-Type': 'application/json',
                ...this.authHeaders
            }},
            body: JSON.stringify(item)
        }});
        
        return response.json();
    }}
    
    chunkArray(array, chunkSize) {{
        const chunks = [];
        for (let i = 0; i < array.length; i += chunkSize) {{
            chunks.push(array.slice(i, i + chunkSize));
        }}
        return chunks;
    }}
}}
'''
    
    return utilities

# Function to generate n8n workflow templates
def generate_n8n_workflows(cpt_slug: str, endpoint: str, field_mapping: Dict) -> Dict[str, Any]:
    """
    Generate comprehensive n8n workflow templates
    """
    workflows = {}
    
    # Complete CRUD workflow
    workflows['complete_crud'] = {
        "name": f"WordPress {cpt_slug.upper()} - Complete CRUD Operations",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "GET",
                    "url": endpoint,
                    "options": {
                        "queryParameters": {
                            "per_page": "100",
                            "orderby": "date",
                            "order": "desc",
                            "status": "publish"
                        }
                    }
                },
                "name": f"Fetch All {cpt_slug.title()}",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [250, 200],
                "id": "fetch_all"
            },
            {
                "parameters": {
                    "functionCode": f'''
// Process and validate fetched {cpt_slug} data
const items = $input.all();
const processedItems = [];

for (const item of items) {{
    const processedItem = {{
        id: item.json.id,
        title: item.json.title?.rendered || item.json.title || 'Untitled',
        content: item.json.content?.rendered || item.json.content || '',
        excerpt: item.json.excerpt?.rendered || item.json.excerpt || '',
        status: item.json.status || 'draft',
        date: item.json.date,
        modified: item.json.modified,
        author: item.json.author,
        link: item.json.link,
        customFields: item.json.meta || {{}},
        // Add validation flags
        isValid: !!(item.json.title && item.json.content),
        needsUpdate: false
    }};
    
    processedItems.push({{ json: processedItem }});
}}

return processedItems;
'''
                },
                "name": "Process Data",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [450, 200],
                "id": "process_data"
            },
            {
                "parameters": {
                    "conditions": {
                        "string": [
                            {
                                "value1": "={{$json.isValid}}",
                                "operation": "equal",
                                "value2": "true"
                            }
                        ]
                    }
                },
                "name": "Filter Valid Items",
                "type": "n8n-nodes-base.filter",
                "typeVersion": 1,
                "position": [650, 200],
                "id": "filter_valid"
            },
            {
                "parameters": {
                    "httpMethod": "POST",
                    "url": endpoint,
                    "body": {
                        "title": "={{$json.title}}",
                        "content": "={{$json.content}}",
                        "excerpt": "={{$json.excerpt}}",
                        "status": "={{$json.status || 'draft'}}",
                        "author": "={{$json.author}}",
                        "meta": "={{$json.customFields}}"
                    }
                },
                "name": f"Create New {cpt_slug.title()}",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [450, 400],
                "id": "create_new"
            },
            {
                "parameters": {
                    "httpMethod": "PUT",
                    "url": f"{endpoint}/{{{{$json.id}}}}",
                    "body": {
                        "title": "={{$json.title}}",
                        "content": "={{$json.content}}",
                        "excerpt": "={{$json.excerpt}}",
                        "status": "={{$json.status}}",
                        "author": "={{$json.author}}",
                        "meta": "={{$json.customFields}}"
                    }
                },
                "name": f"Update {cpt_slug.title()}",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [850, 200],
                "id": "update_item"
            },
            {
                "parameters": {
                    "httpMethod": "DELETE",
                    "url": f"{endpoint}/{{{{$json.id}}}}",
                    "options": {
                        "queryParameters": {
                            "force": "true"
                        }
                    }
                },
                "name": f"Delete {cpt_slug.title()}",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [850, 400],
                "id": "delete_item"
            }
        ],
        "connections": {
            "Fetch All": {
                "main": [
                    [{"node": "Process Data", "type": "main", "index": 0}]
                ]
            },
            "Process Data": {
                "main": [
                    [{"node": "Filter Valid Items", "type": "main", "index": 0}]
                ]
            },
            "Filter Valid Items": {
                "main": [
                    [
                        {"node": f"Update {cpt_slug.title()}", "type": "main", "index": 0},
                        {"node": f"Delete {cpt_slug.title()}", "type": "main", "index": 0}
                    ]
                ]
            }
        }
    }
    
    # Sync workflow
    workflows['sync_workflow'] = {
        "name": f"WordPress {cpt_slug.upper()} - Data Sync",
        "nodes": [
            {
                "parameters": {
                    "rule": {
                        "interval": [{"field": "cronExpression", "value": "0 */6 * * *"}]
                    }
                },
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1,
                "position": [100, 200],
                "id": "schedule_trigger"
            },
            {
                "parameters": {
                    "httpMethod": "GET",
                    "url": endpoint,
                    "options": {
                        "queryParameters": {
                            "modified_after": "={{DateTime.now().minus({hours: 6}).toISO()}}"
                        }
                    }
                },
                "name": "Fetch Recent Changes",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [300, 200],
                "id": "fetch_recent"
            }
        ],
        "connections": {
            "Schedule Trigger": {
                "main": [
                    [{"node": "Fetch Recent Changes", "type": "main", "index": 0}]
                ]
            }
        }
    }
    
    return workflows

# Function to generate export data
def generate_export_data(cpt_data: Dict, analysis: Dict, format_type: str) -> str:
    """
    Generate export data in various formats
    """
    if format_type == "Postman Collection":
        collection = {
            "info": {
                "name": "WordPress CPT API Collection",
                "description": "Generated WordPress Custom Post Types API collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        for cpt_slug, details in cpt_data.items():
            cpt_folder = {
                "name": f"{cpt_slug.title()} Operations",
                "item": [
                    {
                        "name": f"Get All {cpt_slug}",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": f"{{{{base_url}}}}/wp-json/wp/v2/{cpt_slug}?per_page=100",
                                "host": ["{{base_url}}"],
                                "path": ["wp-json", "wp", "v2", cpt_slug],
                                "query": [{"key": "per_page", "value": "100"}]
                            }
                        }
                    }
                ]
            }
            collection["item"].append(cpt_folder)
        
        return json.dumps(collection, indent=2)
    
    elif format_type == "YAML":
        import yaml
        export_data = {
            "wordpress_cpt_api": {
                "analysis": analysis,
                "cpts": cpt_data
            }
        }
        return yaml.dump(export_data, default_flow_style=False)
    
    else:  # JSON
        return json.dumps({
            "analysis": analysis,
            "cpts": cpt_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }, indent=2)

# Main execution
if st.button("🚀 Generate Complete API Documentation", type="primary"):
    if not api_url:
        st.error("Please enter a WordPress API URL.")
        st.stop()
    
    # Prepare authentication configuration
    auth_config = {'type': auth_type}
    if auth_type == "Basic Auth":
        auth_config.update({'username': username, 'password': password})
    elif auth_type == "Application Password":
        auth_config.update({'username': app_username, 'password': app_password})
    elif auth_type == "JWT Token":
        auth_config.update({'token': jwt_token})
    
    # Prepare custom headers
    headers = {'Content-Type': 'application/json', 'User-Agent': 'WordPress-CPT-Generator/1.0'}
    if custom_headers_text:
        try:
            custom_headers = json.loads(custom_headers_text)
            headers.update(custom_headers)
        except json.JSONDecodeError:
            st.warning("⚠️ Invalid JSON in custom headers. Using default headers.")
    
    # Fetch CPT data
    result = fetch_cpts_advanced(api_url, auth_config, headers, timeout_duration, max_retries)
    
    if not result:
        st.stop()
    
    cpt_data = result['data']
    response_headers = result['headers']
    
    if not cpt_data:
        st.warning("⚠️ No Custom Post Types found at the provided endpoint.")
        st.stop()
    
    # Display success message
    st.markdown(f"""
    <div class="success-banner">
        <strong>✅ Successfully fetched {len(cpt_data)} Custom Post Type(s)!</strong><br>
        <small>Response time: {response_headers.get('X-Response-Time', 'N/A')} | Server: {response_headers.get('Server', 'N/A')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Analyze CPT structure
    analysis = analyze_cpt_structure(cpt_data)
    
    # Extract base URL
    parsed_url = urlparse(api_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Display analysis overview
    st.subheader("📊 CPT Analysis Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total CPTs", analysis['total_cpts'])
    with col2:
        st.metric("Public CPTs", len(analysis['public_cpts']))
    with col3:
        st.metric("Private CPTs", len(analysis['private_cpts']))
    with col4:
        st.metric("Hierarchical CPTs", len(analysis['hierarchical_cpts']))
    
    # Detailed analysis
    with st.expander("🔍 Detailed Analysis"):
        st.write("**Public CPTs:**", ', '.join(analysis['public_cpts']) if analysis['public_cpts'] else 'None')
        st.write("**Private CPTs:**", ', '.join(analysis['private_cpts']) if analysis['private_cpts'] else 'None')
        st.write("**Hierarchical CPTs:**", ', '.join(analysis['hierarchical_cpts']) if analysis['hierarchical_cpts'] else 'None')
        
        # Show support features
        for cpt_slug, supports in analysis['supports'].items():
            if supports:
                st.write(f"**{cpt_slug} supports:**", ', '.join(supports))
    
    # Generate comprehensive documentation
    st.markdown("## 📚 Complete API Documentation")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔧 CRUD Operations", 
        "🤖 n8n Workflows", 
        "💻 JavaScript Utilities", 
        "📖 Documentation", 
        "📤 Export"
    ])
    
    with tab1:
        st.markdown("### 🔧 Complete CRUD Operations")
        
        for cpt_slug, details in cpt_data.items():
            with st.expander(f"🔹 {cpt_slug.upper()} - {details.get('name', 'N/A')}"):
                endpoint = f"{base_url}/wp-json/wp/v2/{cpt_slug}"
                supports = details.get('supports', [])
                field_mapping = generate_field_mapping(cpt_slug, supports)
                
                # CPT Information
                st.markdown("#### ℹ️ CPT Information")
                info_data = {
                    "Name": details.get('name', 'N/A'),
                    "Description": details.get('description', 'N/A'),
                    "Public": details.get('public', False),
                    "Hierarchical": details.get('hierarchical', False),
                    "REST Base": details.get('rest_base', cpt_slug),
                    "Supports": ', '.join(supports) if supports else 'None'
                }
                
                for key, value in info_data.items():
                    st.write(f"**{key}:** {value}")
                
                st.markdown("---")
                
                # Authentication Configuration
                st.markdown("#### 🔐 Authentication Configuration")
                auth_config_template = {
                    "authentication": {
                        "type": auth_type.lower().replace(' ', '_'),
                        "url": endpoint,
                        "headers": {
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        }
                    }
                }
                
                if auth_type == "Basic Auth":
                    auth_config_template["authentication"]["credentials"] = {
                        "username": "{{username}}",
                        "password": "{{password}}"
                    }
                elif auth_type == "Application Password":
                    auth_config_template["authentication"]["headers"]["Authorization"] = "Basic {{base64(username:app_password)}}"
                elif auth_type == "JWT Token":
                    auth_config_template["authentication"]["headers"]["Authorization"] = "Bearer {{jwt_token}}"
                
                st.code(json.dumps(auth_config_template, indent=2), language="json")
                
                # Field Schema
                st.markdown("#### 📋 Field Schema")
                st.code(json.dumps(field_mapping, indent=2), language="json")
                
                # GET Operations
                st.markdown("#### 🔍 GET Operations")
                
                # Basic GET
                get_basic = {
                    "method": "GET",
                    "url": endpoint,
                    "queryParameters": {
                        "per_page": items_per_page,
                        "page": 1,
                        "orderby": "date",
                        "order": "desc",
                        "status": "publish"
                    }
                }
                st.markdown("**Basic GET Request:**")
                st.code(json.dumps(get_basic, indent=2), language="json")
                
                # Advanced GET with filters
                get_advanced = {
                    "method": "GET",
                    "url": endpoint,
                    "queryParameters": {
                        "per_page": items_per_page,
                        "page": "{{page_number}}",
                        "search": "{{search_term}}",
                        "author": "{{author_id}}",
                        "before": "{{date_before}}",
                        "after": "{{date_after}}",
                        "exclude": "{{exclude_ids}}",
                        "include": "{{include_ids}}",
                        "offset": "{{offset}}",
                        "orderby": "{{order_field}}",
                        "order": "{{order_direction}}",
                        "slug": "{{post_slug}}",
                        "status": "{{post_status}}",
                        "categories": "{{category_ids}}",
                        "tags": "{{tag_ids}}",
                        "categories_exclude": "{{exclude_category_ids}}",
                        "tags_exclude": "{{exclude_tag_ids}}"
                    }
                }
                st.markdown("**Advanced GET with Filters:**")
                st.code(json.dumps(get_advanced, indent=2), language="json")
                
                # GET by ID
                get_by_id = {
                    "method": "GET",
                    "url": f"{endpoint}/{{{{post_id}}}}",
                    "queryParameters": {
                        "context": "edit",
                        "password": "{{post_password}}"
                    }
                }
                st.markdown("**GET by ID:**")
                st.code(json.dumps(get_by_id, indent=2), language="json")
                
                # POST Operations
                st.markdown("#### ➕ POST Operations (Create)")
                
                post_body = {}
                for field, config in field_mapping.items():
                    if not config.get('readonly', False):
                        if field == 'meta':
                            post_body[field] = {
                                "custom_field_1": "{{custom_value_1}}",
                                "custom_field_2": "{{custom_value_2}}",
                                "acf_field": "{{acf_value}}",
                                "_custom_meta": "{{meta_value}}"
                            }
                        elif field in ['title', 'content', 'excerpt']:
                            post_body[field] = {"raw": f"{{{{{field}}}}}"}
                        else:
                            post_body[field] = f"{{{{{field}}}}}"
                
                post_request = {
                    "method": "POST",
                    "url": endpoint,
                    "body": post_body,
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
                st.code(json.dumps(post_request, indent=2), language="json")
                
                # PUT Operations
                st.markdown("#### 🔄 PUT Operations (Update)")
                
                put_request = {
                    "method": "PUT",
                    "url": f"{endpoint}/{{{{post_id}}}}",
                    "body": post_body,
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
                st.code(json.dumps(put_request, indent=2), language="json")
                
                # PATCH Operations
                st.markdown("#### 🔧 PATCH Operations (Partial Update)")
                
                patch_request = {
                    "method": "PATCH",
                    "url": f"{endpoint}/{{{{post_id}}}}",
                    "body": {
                        "status": "{{new_status}}",
                        "meta": {
                            "updated_field": "{{new_value}}"
                        }
                    },
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
                st.code(json.dumps(patch_request, indent=2), language="json")
                
                # DELETE Operations
                st.markdown("#### 🗑️ DELETE Operations")
                
                # Soft delete (trash)
                delete_soft = {
                    "method": "DELETE",
                    "url": f"{endpoint}/{{{{post_id}}}}",
                    "queryParameters": {
                        "force": False
                    }
                }
                st.markdown("**Soft Delete (Move to Trash):**")
                st.code(json.dumps(delete_soft, indent=2), language="json")
                
                # Hard delete (permanent)
                delete_hard = {
                    "method": "DELETE",
                    "url": f"{endpoint}/{{{{post_id}}}}",
                    "queryParameters": {
                        "force": True
                    }
                }
                st.markdown("**Hard Delete (Permanent):**")
                st.code(json.dumps(delete_hard, indent=2), language="json")
                
                # Bulk Operations
                st.markdown("#### 📦 Bulk Operations")
                
                bulk_create = {
                    "method": "POST",
                    "url": f"{base_url}/wp-json/wp/v2/batch",
                    "body": {
                        "requests": [
                            {
                                "method": "POST",
                                "path": f"/wp/v2/{cpt_slug}",
                                "body": post_body
                            }
                        ]
                    }
                }
                st.markdown("**Bulk Create:**")
                st.code(json.dumps(bulk_create, indent=2), language="json")
                
                st.markdown("---")
    
    with tab2:
        st.markdown("### 🤖 n8n Workflow Templates")
        
        for cpt_slug, details in cpt_data.items():
            with st.expander(f"🔹 {cpt_slug.upper()} Workflows"):
                endpoint = f"{base_url}/wp-json/wp/v2/{cpt_slug}"
                supports = details.get('supports', [])
                field_mapping = generate_field_mapping(cpt_slug, supports)
                workflows = generate_n8n_workflows(cpt_slug, endpoint, field_mapping)
                
                for workflow_name, workflow_data in workflows.items():
                    st.markdown(f"#### {workflow_name.replace('_', ' ').title()}")
                    st.code(json.dumps(workflow_data, indent=2), language="json")
                    st.markdown("---")
    
    with tab3:
        st.markdown("### 💻 JavaScript Utilities")
        
        for cpt_slug, details in cpt_data.items():
            with st.expander(f"🔹 {cpt_slug.upper()} JavaScript Utilities"):
                endpoint = f"{base_url}/wp-json/wp/v2/{cpt_slug}"
                utilities = generate_javascript_utilities(cpt_slug, endpoint)
                
                for utility_name, utility_code in utilities.items():
                    st.markdown(f"#### {utility_name.replace('_', ' ').title()}")
                    st.code(utility_code, language="javascript")
                    st.markdown("---")
    
    with tab4:
        st.markdown("### 📖 API Documentation")
        
        # Generate comprehensive documentation
        doc_content = f"""
# WordPress Custom Post Types API Documentation

## Overview
This documentation covers all Custom Post Types available in your WordPress installation.

**Base URL:** `{base_url}`
**API Version:** WordPress REST API v2
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Authentication
{auth_type} authentication is configured for this API.

## Available Custom Post Types

"""
        
        for cpt_slug, details in cpt_data.items():
            supports = details.get('supports', [])
            field_mapping = generate_field_mapping(cpt_slug, supports)
            
            doc_content += f"""
### {cpt_slug.upper()}

**Name:** {details.get('name', 'N/A')}
**Description:** {details.get('description', 'No description available')}
**Endpoint:** `/wp-json/wp/v2/{cpt_slug}`
**Public:** {'Yes' if details.get('public', False) else 'No'}
**Hierarchical:** {'Yes' if details.get('hierarchical', False) else 'No'}

#### Supported Features
{', '.join(supports) if supports else 'None'}

#### Available Fields
"""
            
            for field, config in field_mapping.items():
                readonly_text = " (Read-only)" if config.get('readonly', False) else ""
                doc_content += f"- **{field}** ({config['type']}){readonly_text}: {config.get('description', 'No description')}\n"
            
            doc_content += f"""
#### Example Requests

**GET All {cpt_slug}:**
```
GET {base_url}/wp-json/wp/v2/{cpt_slug}?per_page=10&status=publish
```

**GET Single {cpt_slug}:**
```
GET {base_url}/wp-json/wp/v2/{cpt_slug}/123
```

**CREATE New {cpt_slug}:**
```
POST {base_url}/wp-json/wp/v2/{cpt_slug}
Content-Type: application/json

{json.dumps({"title": {"raw": "Example Title"}, "content": {"raw": "Example content"}, "status": "draft"}, indent=2)}
```

**UPDATE {cpt_slug}:**
```
PUT {base_url}/wp-json/wp/v2/{cpt_slug}/123
Content-Type: application/json

{json.dumps({"title": {"raw": "Updated Title"}, "status": "publish"}, indent=2)}
```

**DELETE {cpt_slug}:**
```
DELETE {base_url}/wp-json/wp/v2/{cpt_slug}/123?force=true
```

---
"""
        
        st.markdown(doc_content)
        
        # Download documentation
        st.download_button(
            label="📥 Download Documentation",
            data=doc_content,
            file_name=f"wordpress_cpt_api_documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    with tab5:
        st.markdown("### 📤 Export Options")
        
        # Generate export data
        export_data = generate_export_data(cpt_data, analysis, export_format)
        
        st.markdown(f"**Export Format:** {export_format}")
        st.code(export_data[:2000] + "..." if len(export_data) > 2000 else export_data, language="json" if export_format in ["JSON", "Postman Collection"] else "yaml")
        
        # Download button
        file_extension = {
            "JSON": "json",
            "YAML": "yaml",
            "Postman Collection": "postman_collection.json",
            "Insomnia Collection": "insomnia_collection.json"
        }
        
        st.download_button(
            label=f"📥 Download {export_format}",
            data=export_data,
            file_name=f"wordpress_cpt_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension[export_format]}",
            mime="application/json" if "json" in file_extension[export_format] else "text/yaml"
        )
        
        # Additional export options
        st.markdown("#### 🔧 Additional Export Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Copy to Clipboard"):
                st.code("navigator.clipboard.writeText(`" + export_data.replace('`', '\\`') + "`)")
                st.success("✅ Code to copy data has been generated above!")
        
        with col2:
            if st.button("📧 Generate Email Template"):
                email_template = f"""
Subject: WordPress CPT API Documentation - {len(cpt_data)} Custom Post Types

Hi there,

I've generated comprehensive API documentation for the WordPress Custom Post Types. Here are the details:

- Total CPTs: {len(cpt_data)}
- Public CPTs: {len(analysis['public_cpts'])}
- Private CPTs: {len(analysis['private_cpts'])}
- Base URL: {base_url}

The documentation includes:
✅ Complete CRUD operations for all CPTs
✅ n8n workflow templates
✅ JavaScript utilities for data processing
✅ Authentication configurations
✅ Field mappings and validation

Please find the complete documentation attached.

Best regards,
WordPress CPT API Generator
"""
                st.text_area("Email Template:", email_template, height=300)
    
    # Performance metrics
    st.markdown("## 📊 Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("API Response Time", response_headers.get('X-Response-Time', 'N/A'))
    with col2:
        st.metric("Total Fields Generated", sum(len(generate_field_mapping(slug, details.get('supports', []))) for slug, details in cpt_data.items()))
    with col3:
        st.metric("Code Templates Created", len(cpt_data) * 8)  # 8 templates per CPT
    
    # Quick actions
    st.markdown("## ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    with col2:
        if st.button("📊 Generate Report"):
            report_data = {
                "summary": analysis,
                "cpts": list(cpt_data.keys()),
                "generated_at": datetime.now().isoformat(),
                "total_templates": len(cpt_data) * 8
            }
            st.json(report_data)
    
    with col3:
        if st.button("🔗 Test Endpoints"):
            st.info("🔗 Endpoint testing feature coming soon!")
    
    with col4:
        if st.button("💾 Save Configuration"):
            config_data = {
                "api_url": api_url,
                "auth_type": auth_type,
                "timeout": timeout_duration,
                "items_per_page": items_per_page
            }
            st.download_button(
                "Download Config",
                data=json.dumps(config_data, indent=2),
                file_name="wp_cpt_config.json",
                mime="application/json"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <h4>🚀 WordPress CPT API & n8n Agent Generator</h4>
    <p>Built with ❤️ using Streamlit | Support: <a href="https://developer.wordpress.org/rest-api/" target="_blank">WordPress REST API Docs</a></p>
    <small>Generate comprehensive API documentation and workflows for WordPress Custom Post Types</small>
</div>
""", unsafe_allow_html=True)

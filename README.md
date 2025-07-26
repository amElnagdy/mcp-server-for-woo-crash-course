# MCP for WooCommerce

A Python-based server application for integrating MCP with WooCommerce.

## Getting Started

Follow these steps to set up the project after cloning the repository:

### Prerequisites

- Python 3.12 or later
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/amElnagdy/mcp-server-for-woo-crash-course.git
   cd mcp-for-woocommerce
   ```

2. **Set up a virtual environment**

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   uv pip install -e .
   ```

4. **Configure WooCommerce API credentials**

   Edit the `config.json` file and add your WooCommerce store details:
   ```json
   {
     "store_url": "https://your-woocommerce-store.com",
     "consumer_key": "your_consumer_key",
     "consumer_secret": "your_consumer_secret",
     "api_version": "wc/v3"
   }
   ```

5. **Run the application**

   ```bash
   uv run src/server.py
   ```

## Project Structure

- `src/server.py`: Main server implementation and entry point for the application
- `src/woo_client.py`: WooCommerce API client
- `config.json`: Configuration for WooCommerce connection

## Getting WooCommerce API Credentials

To generate your WooCommerce API credentials:

1. Log in to your WordPress admin panel
2. Navigate to WooCommerce → Settings → Advanced → REST API
3. Click "Add key"
4. Add a description, select a user, and set permissions to "Read/Write"
5. Click "Generate API key"
6. Copy the Consumer Key and Consumer Secret to your `config.json` file
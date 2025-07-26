from typing import Optional, Dict, Any, List

from woo_client import WooClient
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP Server for WooCommerce")

_woo_client: Optional[WooClient] = None


def get_woo_client():
    global _woo_client
    if _woo_client is None:
        _woo_client = WooClient()
    return _woo_client


# ------ TOOLS ------ #
@mcp.tool()
def get_products(status: Optional[str] = None, category: Optional[int] = None, per_page: int = 10) -> str:
    try:
        client = get_woo_client()
        params = {'per_page': min(per_page, 100)}

        if status:
            params['status'] = status
        if category:
            params['category'] = category

        products = client.get_products(**params)

        if not products:
            return "No products matched the query."

        result = f"found {len(products)} products:\n\n"

        for product in products:
            result += f"ID: {product['id']}\n"
            result += f"Name: {product['name']}\n"
            result += f"Status: {product['status']}\n"
            result += f"Price: {product['price']}\n"
            result += f"Stock Status: {product['stock_status']}\n"

            missing_content = []
            if not product.get('description').strip():
                missing_content.append("description")
            if not product.get('short_description').strip():
                missing_content.append("short description")

            if missing_content:
                result += f"Missing content: {', '.join(missing_content)}\n"

            result += "\n"

        return result
    except Exception as e:
        return f"Error fetching products: {e}"


@mcp.tool()
def get_product_by_id(product_id: int) -> str:
    try:
        client = get_woo_client()
        product = client.get_product_by_id(product_id)
        # Format detailed product information
        result = f"Product Details (ID: {product['id']})\n"
        result += f"{'=' * 40}\n\n"
        result += f"Name: {product['name']}\n"
        result += f"Status: {product['status']}\n"
        result += f"Type: {product['type']}\n"
        result += f"Price: {product['price']}\n"
        result += f"Regular Price: {product['regular_price']}\n"
        result += f"Sale Price: {product['sale_price']}\n"
        result += f"Stock Status: {product['stock_status']}\n"
        result += f"Stock Quantity: {product.get('stock_quantity', 'N/A')}\n\n"

        result += f"Description:\n{product.get('description', 'No description')}\n\n"
        result += f"Short Description:\n{product.get('short_description', 'No short description')}\n\n"

        # SEO Meta information
        meta_data = product.get('meta_data', [])
        seo_title = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_title'), None)
        seo_desc = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_metadesc'), None)

        result += f"SEO Title: {seo_title or 'Not set'}\n"
        result += f"SEO Description: {seo_desc or 'Not set'}\n\n"

        # Categories
        if product.get('categories'):
            result += "Categories:\n"
            for cat in product['categories']:
                result += f"  - {cat['name']} (ID: {cat['id']})\n"

        return result

    except Exception as e:
        return f"Error fetching product: {str(e)}"


@mcp.tool()
def update_product(
        product_id: int,
        description: Optional[str] = None,
        short_description: Optional[str] = None,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None
) -> str:
    try:
        client = get_woo_client()
        update_data = {}

        if description:
            update_data['description'] = description

        if short_description:
            update_data['short_description'] = short_description

        meta_data = []
        if meta_title:
            meta_data.append({
                'key': '_yoast_wpseo_title',
                'value': meta_title
            })

        if meta_description:
            meta_data.append({
                'key': '_yoast_wpseo_metadesc',
                'value': meta_description
            })

        if meta_data:
            update_data['meta_data'] = meta_data

        if not update_data:
            return "Error: No update data provided"

        # Perform update
        updated_product = client.update_product(product_id, update_data)

        result = f"Successfully updated product ID {product_id}:\n\n"

        if description:
            result += f"✅ Description updated\n"
        if short_description:
            result += f"✅ Short description updated\n"
        if meta_title:
            result += f"✅ SEO title updated\n"
        if meta_description:
            result += f"✅ SEO description updated\n"

        result += f"\nProduct: {updated_product['name']}"

        return result
    except Exception as e:
        return f"Error updating product: {str(e)}"

@mcp.tool()
def analyze_products(per_page: int = 50) -> str:
    try:
        client = get_woo_client()
        params = {'per_page': min(per_page, 100)}

        products = client.get_products(**params)

        if not products:
            return "No products found to analyze."

        missing_description = []
        missing_short_description = []
        missing_seo = []

        for product in products:
            product_info = {
                'id': product['id'],
                'name': product['name'],
                'status': product['status']
            }

            # Check descriptions
            if not product.get('description', '').strip():
                missing_description.append(product_info)

            if not product.get('short_description', '').strip():
                missing_short_description.append(product_info)

            # Check SEO meta
            meta_data = product.get('meta_data', [])
            seo_title = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_title'), None)
            seo_desc = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_metadesc'), None)

            if not seo_title or not seo_desc:
                missing_seo.append(product_info)

        result = "Products Analysis:\n\n"
        result += f"{'='*30}\n\n"
        result += f"Analyzed {len(products)} products\n\n"
        result += f"📝 Missing Descriptions: {len(missing_description)}\n"

        if missing_description:
            for product in missing_description[:10]:
                result += f"  - ID {product['id']}: {product['name']}\n"
            if len(missing_description) > 10:
                result += f"  ... and {len(missing_description) - 10} more\n"

        result += f"\n📄 Missing Short Descriptions: {len(missing_short_description)}\n"

        if missing_short_description:
            for product in missing_short_description[:10]:
                result += f"  - ID {product['id']}: {product['name']}\n"
            if len(missing_short_description) > 10:
                result += f"  ... and {len(missing_short_description) - 10} more\n"

        result += f"\n🔍 Missing SEO Data: {len(missing_seo)}\n"
        if missing_seo:
            for product in missing_seo[:10]:
                result += f"  - ID {product['id']}: {product['name']}\n"
            if len(missing_seo) > 10:
                result += f"  ... and {len(missing_seo) - 10} more\n"

        return result

    except Exception as e:
        return f"Error analyzing products: {str(e)}"


@mcp.tool()
def bulk_update_products(updates: List[Dict[str, Any]]) -> str:
    """
    Update multiple products at once.

    Args:
        updates: List of product updates, each containing product_id and update fields
    """
    try:
        client = get_woo_client()
        results = []
        errors = []

        for update in updates:
            try:
                if 'product_id' not in update:
                    errors.append("Missing product_id in update")
                    continue

                product_id = int(update['product_id'])
                update_data = {}

                # Extract update fields
                for field in ['description', 'short_description']:
                    if field in update:
                        update_data[field] = update[field]

                # Handle SEO meta
                meta_data = []
                if 'meta_title' in update:
                    meta_data.append({
                        'key': '_yoast_wpseo_title',
                        'value': update['meta_title']
                    })

                if 'meta_description' in update:
                    meta_data.append({
                        'key': '_yoast_wpseo_metadesc',
                        'value': update['meta_description']
                    })

                if meta_data:
                    update_data['meta_data'] = meta_data

                if update_data:
                    updated_product = client.update_product(product_id, update_data)
                    results.append(f"✅ Updated product ID {product_id}: {updated_product['name']}")
                else:
                    errors.append(f"No update data for product ID {product_id}")

            except Exception as e:
                errors.append(f"Failed to update product ID {update.get('product_id', 'unknown')}: {str(e)}")

        # Generate summary
        result = f"Bulk Update Results\n"
        result += f"{'=' * 25}\n\n"
        result += f"Successfully updated: {len(results)}\n"
        result += f"Errors: {len(errors)}\n\n"

        if results:
            result += "Successful Updates:\n"
            for success in results:
                result += f"{success}\n"
            result += "\n"

        if errors:
            result += "Errors:\n"
            for error in errors:
                result += f"❌ {error}\n"

        return result

    except Exception as e:
        return f"Error in bulk update: {str(e)}"


@mcp.tool()
def audit_product_images(product_id: int) -> str:
    """
    Audit product images for SEO issues and accessibility.

    Args:
        product_id: The product ID to audit images for
    """
    try:
        client = get_woo_client()
        product = client.get_product_by_id(product_id)

        if not product:
            return f"❌ Product {product_id} not found"

        product_name = product.get('name', 'Unknown Product')
        images = product.get('images', [])

        # Initialize audit results
        issues = []
        suggestions = []
        good_practices = []

        # Check if product has images
        if not images:
            issues.append("❌ No product images found")
            suggestions.append(f"Add at least 1-3 high-quality images for '{product_name}'")
            return f"\n🖼️ Image SEO Audit for: {product_name}\n" + "=" * 50 + f"\n\n❌ Critical Issue: No images found!\n\nSuggestions:\n• {suggestions[0]}\n• Images improve conversion rates by 30-40%\n• Add main product image, detail shots, and lifestyle images"

        # Audit each image
        for i, image in enumerate(images):
            image_num = i + 1
            alt_text = image.get('alt', '').strip()
            image_name = image.get('name', '').strip()

            # Check alt text
            if not alt_text:
                issues.append(f"❌ Image {image_num} missing alt text")
                suggestions.append(f"Add alt text: '{product_name} - product view {image_num}'")
            elif len(alt_text) < 10:
                issues.append(f"⚠️ Image {image_num} alt text too short: '{alt_text}'")
                suggestions.append(f"Expand alt text to be more descriptive (10+ characters)")
            elif alt_text.lower() == product_name.lower():
                issues.append(f"⚠️ Image {image_num} alt text is just product name")
                suggestions.append(f"Make alt text more descriptive: '{product_name} - [describe what's shown]'")
            else:
                good_practices.append(f"✅ Image {image_num} has good alt text")

            # Check image name/title
            if not image_name or image_name.lower() in ['image', 'img', 'photo', 'picture']:
                issues.append(f"⚠️ Image {image_num} has generic or missing name")
                suggestions.append(f"Use descriptive filename: '{product_name.lower().replace(' ', '-')}-{image_num}'")

        # Generate summary
        total_images = len(images)
        total_issues = len(issues)

        # Build report
        report = f"\n🖼️ Image SEO Audit for: {product_name}\n"
        report += "=" * 50 + "\n\n"
        report += f"📊 Summary:\n"
        report += f"  • Total Images: {total_images}\n"
        report += f"  • Issues Found: {total_issues}\n"
        report += f"  • Good Practices: {len(good_practices)}\n\n"

        if issues:
            report += "❌ Issues Found:\n"
            for issue in issues:
                report += f"  • {issue}\n"
            report += "\n"

        if suggestions:
            report += "💡 Suggestions:\n"
            for suggestion in suggestions:
                report += f"  • {suggestion}\n"
            report += "\n"

        if good_practices:
            report += "✅ Good Practices:\n"
            for practice in good_practices:
                report += f"  • {practice}\n"
            report += "\n"

        # SEO tips
        report += "🎯 SEO Best Practices:\n"
        report += "  • Alt text should describe what's in the image\n"
        report += "  • Include product name + descriptive details\n"
        report += "  • Keep alt text under 125 characters\n"
        report += "  • Use keywords naturally, don't stuff\n"
        report += "  • Consider image file size for page speed\n"

        return report

    except Exception as e:
        return f"Error auditing product images: {str(e)}"


# ------ RESOURCES ------ #
@mcp.resource("woo://store/stats")
def store_stats() -> str:
    try:
        client = get_woo_client()

        products = client.get_products(per_page=100)
        categories = client.get_categories(per_page=100)

        total_products = len(products)
        missing_description = 0
        missing_short_description = 0
        missing_seo = 0
        published_products = 0
        draft_products = 0

        for product in products:
            # Count by status
            if product['status'] == 'publish':
                published_products += 1
            elif product['status'] == 'draft':
                draft_products += 1

            # Check for missing content
            if not product.get('description', '').strip():
                missing_description += 1

            if not product.get('short_description', '').strip():
                missing_short_description += 1

            # Check SEO meta
            meta_data = product.get('meta_data', [])
            seo_title = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_title'), None)
            seo_desc = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_metadesc'), None)

            if not seo_title or not seo_desc:
                missing_seo += 1

        total_needing_optimization = len(set([
            i for i, product in enumerate(products)
            if (not product.get('description', '').strip() or
                not product.get('short_description', '').strip() or
                not any(item['key'] == '_yoast_wpseo_title' and item.get('value')
                        for item in product.get('meta_data', [])) or
                not any(item['key'] == '_yoast_wpseo_metadesc' and item.get('value')
                        for item in product.get('meta_data', [])))
        ]))

        content = f"""WooCommerce Store Statistics
        ===============================

        📊 Product Overview:
          Total Products: {total_products}
          Published: {published_products}
          Drafts: {draft_products}

        🔧 Optimization Opportunities:
          Products Needing Work: {total_needing_optimization}
          Missing Descriptions: {missing_description}
          Missing Short Descriptions: {missing_short_description}
          Missing SEO Data: {missing_seo}

        📁 Categories:
          Total Categories: {len(categories)}

        🎯 Priority Actions:
        """

        if total_needing_optimization > 0:
            content += f"  • {total_needing_optimization} products need content optimization\n"

        if missing_seo > 0:
            content += f"  • {missing_seo} products missing SEO metadata\n"

        if missing_description > 0:
            content += f"  • {missing_description} products need descriptions\n"

        if total_needing_optimization == 0:
            content += "  • All products are well-optimized! 🎉\n"

        optimization_percentage = (
                    (total_products - total_needing_optimization) / total_products * 100) if total_products > 0 else 100
        content += f"\n📈 Store Optimization Score: {optimization_percentage:.1f}%"

        return content

    except Exception as e:
        return f"Error fetching store statistics: {str(e)}"

# ------ PROMPTS ------ #
@mcp.prompt()
def analyze_store(include_products: bool = True, max_products: int = 50) -> str:
    try:
        prompt = "You are a WooCommerce store optimization consultant specialized in SEO and product optimization. "

        client = get_woo_client()
        max_products = min(max_products, 100)
        products = client.get_products(per_page=max_products)
        categories = client.get_categories(per_page=100)

        analysis = {
            'total_products': len(products),
            'published': sum(1 for p in products if p['status'] == 'publish'),
            'drafts': sum(1 for p in products if p['status'] == 'draft'),
            'missing_description': [],
            'missing_short_description': [],
            'missing_seo': [],
            'low_quality_content': [],
            'categories_analysis': {}
        }

        for product in products:
            product_info = {
                'id': product['id'],
                'name': product['name'],
                'status': product['status'],
                'price': product.get('price', '0')
            }

            # Check descriptions
            description = product.get('description', '').strip()
            short_description = product.get('short_description', '').strip()

            if not description:
                analysis['missing_description'].append(product_info)
            elif len(description) < 100:
                analysis['low_quality_content'].append({**product_info, 'issue': 'Short description (<100 chars)'})

            if not short_description:
                analysis['missing_short_description'].append(product_info)

            # Check SEO
            meta_data = product.get('meta_data', [])
            seo_title = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_title'), None)
            seo_desc = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_metadesc'), None)

            if not seo_title or not seo_desc:
                analysis['missing_seo'].append(product_info)

        # Analyze categories
        for category in categories:
            analysis['categories_analysis'][category['name']] = {
                'id': category['id'],
                'product_count': category['count'],
                'has_description': bool(category.get('description', '').strip())
            }


        prompt += f"""
STORE OVERVIEW:
- Total Products Analyzed: {analysis['total_products']}
- Published Products: {analysis['published']}
- Draft Products: {analysis['drafts']}
- Total Categories: {len(categories)}

CONTENT ISSUES FOUND:
- Products Missing Descriptions: {len(analysis['missing_description'])}
- Products Missing Short Descriptions: {len(analysis['missing_short_description'])}
- Products Missing SEO Data: {len(analysis['missing_seo'])}
- Products with Low-Quality Content: {len(analysis['low_quality_content'])}

"""

        if include_products and analysis['missing_description']:
            prompt += f"\nPRODUCTS MISSING DESCRIPTIONS ({len(analysis['missing_description'])}):\n"
            for product in analysis['missing_description'][:10]:
                prompt += f"- ID {product['id']}: {product['name']} (${product['price']})\n"
            if len(analysis['missing_description']) > 10:
                prompt += f"... and {len(analysis['missing_description']) - 10} more\n"

        if include_products and analysis['missing_seo']:
            prompt += f"\nPRODUCTS MISSING SEO DATA ({len(analysis['missing_seo'])}):\n"
            for product in analysis['missing_seo'][:10]:
                prompt += f"- ID {product['id']}: {product['name']} (${product['price']})\n"
            if len(analysis['missing_seo']) > 10:
                prompt += f"... and {len(analysis['missing_seo']) - 10} more\n"

            prompt += f"""
CATEGORY ANALYSIS:
"""
        for cat_name, cat_data in list(analysis['categories_analysis'].items())[:10]:
            prompt += f"- {cat_name}: {cat_data['product_count']} products, {'✓' if cat_data['has_description'] else '✗'} description\n"

        prompt += """

Please provide:

1. PRIORITY ASSESSMENT (High/Medium/Low for each issue)
2. ACTIONABLE RECOMMENDATIONS with specific steps
3. CONTENT STRATEGY suggestions for improving product descriptions
4. SEO OPTIMIZATION roadmap
5. ESTIMATED TIMELINE for implementing improvements
6. POTENTIAL IMPACT on store performance

Focus on:
- Quick wins that can be implemented immediately
- Long-term strategies for content improvement
- SEO best practices for e-commerce
- User experience improvements
- Conversion optimization opportunities

Provide specific, actionable advice that a store owner can implement right away.
"""

        return prompt

    except Exception as e:
        return f"Error generating store analysis prompt: {str(e)}"


@mcp.prompt()
def bulk_generate_seo(category_id: Optional[int] = None, limit: int = 20) -> str:
    try:
        client = get_woo_client()

        # Get parameters
        params = {'per_page': min(limit, 50)}

        if category_id:
            params['category'] = str(category_id)

        # Fetch products
        products = client.get_products(**params)

        # Filter products missing SEO data
        products_needing_seo = []

        for product in products:
            meta_data = product.get('meta_data', [])
            seo_title = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_title'), None)
            seo_desc = next((item['value'] for item in meta_data if item['key'] == '_yoast_wpseo_metadesc'), None)

            if not seo_title or not seo_desc:
                products_needing_seo.append({
                    'id': product['id'],
                    'name': product['name'],
                    'description': product.get('description', ''),
                    'short_description': product.get('short_description', ''),
                    'price': product.get('price', ''),
                    'categories': [cat['name'] for cat in product.get('categories', [])],
                    'missing_seo_title': not seo_title,
                    'missing_seo_desc': not seo_desc
                })

        if not products_needing_seo:
            return "Great news! All products in the specified range already have SEO metadata configured."

        prompt_text = f"""You are an SEO expert helping to optimize WooCommerce products. Please generate SEO metadata for the following {len(products_needing_seo)} products that are missing SEO data.

For each product, provide:
1. SEO Title (max 60 characters) - should be compelling and include key product terms
2. Meta Description (max 160 characters) - should be engaging and encourage clicks
3. Use natural language keywords

Products needing SEO optimization:

"""

        for i, product in enumerate(products_needing_seo, 1):
            prompt_text += f"""
Product {i}:
- ID: {product['id']}
- Name: {product['name']}
- Price: ${product['price']}
- Categories: {', '.join(product['categories']) if product['categories'] else 'Uncategorized'}
- Description: {product['description'][:200]}{'...' if len(product['description']) > 200 else ''}
- Missing: {'SEO Title' if product['missing_seo_title'] else ''}{', ' if product['missing_seo_title'] and product['missing_seo_desc'] else ''}{'Meta Description' if product['missing_seo_desc'] else ''}

"""

        prompt_text += """
Please provide the SEO metadata in this format for each product:

Product ID [ID]:
SEO Title: [Your optimized title here]
Meta Description: [Your optimized description here]

Focus on:
- Including relevant keywords naturally
- Making titles and descriptions compelling for users
- Staying within character limits
- Highlighting unique selling points
- Using action-oriented language where appropriate
"""

        return prompt_text

    except Exception as e:
        return f"Error generating SEO prompt: {str(e)}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()

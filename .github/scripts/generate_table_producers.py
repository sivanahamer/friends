#!/usr/bin/env python3
"""Generate attestation sources table from README.md frontmatter."""

import re
from pathlib import Path
from typing import Dict, List, Any
import yaml

SOURCES_DIR = Path("list_producers")
README_PATH = Path("README.md")

# Define the order of types in the table
TYPE_ORDER = {
    'Repository': 0,
    'Images': 1,
    'Package Registry': 2,
    'Package Registries': 2,
    'Database': 3,
    'Databases': 3,
    'Aggregator': 4,
    'Aggregators': 4,
}

def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}

def get_directory_name(path: Path) -> str:
    """Convert directory path to human-readable name."""
    name = path.name
    # Convert kebab-case and snake_case to Title Case
    return ' '.join(word.capitalize() for word in re.split(r'[-_]', name))

def collect_sources() -> List[Dict[str, Any]]:
    """Collect all attestation sources from subdirectories."""
    sources = []

    # Get all first-level subdirectories
    for item in sorted(SOURCES_DIR.iterdir()):
        if item.is_dir() and item.name not in {'imgs', 'test-csv-files', '__pycache__'}:
            readme = item / "README.md"
            
            if readme.exists():
                with open(readme, 'r') as f:
                    content = f.read()
                
                frontmatter = parse_frontmatter(content)
                
                # Skip if no frontmatter
                if not frontmatter:
                    continue
                
                sources.append({
                    'name': get_directory_name(item),
                    'type': frontmatter.get('type', 'Unknown'),
                    'besides': frontmatter.get('besides', 'Unknown'),
                    'format': frontmatter.get('format', []),
                    'visibility': frontmatter.get('visibility', []),
                    'path': item
                })
    
    return sorted(sources, key=lambda x: (TYPE_ORDER.get(x['type'], 999), x['name']))

def format_format(formats: List[str] | str) -> str:
    """Format the format field for the table."""
    if isinstance(formats, str):
        formats = [formats]
    
    if not formats:
        return "Unknown"
    
    formatted = []
    for fmt in formats:
        fmt_lower = fmt.lower()
        
        # Handle simple cases first
        if fmt_lower == 'dsse':
            formatted.append('[dsse](https://github.com/secure-systems-lab/dsse)')
        elif fmt_lower == 'intoto':
            formatted.append('[intoto](https://github.com/sigstore/rekor/blob/main/pkg/types/intoto/README.mdn)')
        elif fmt_lower == 'hashrekord':
            formatted.append('[HashRekord](https://github.com/sigstore/rekor/blob/main/pkg/types/hashedrekord/v0.0.1/hashedrekord_v0_0_1_schema.json)')
        elif fmt_lower == 'sigstore bundle' or fmt_lower == 'sigstore bundles':
            formatted.append('[Sigstore Bundle](https://docs.sigstore.dev/about/bundle/)')
        elif fmt_lower == 'cosign bundle':
            formatted.append('[Cosign Bundle](https://github.com/sigstore/cosign/blob/main/specs/BUNDLE_SPEC.md)')
        elif fmt_lower == 'attestation bundle':
            formatted.append('[Attestation Bundle](https://github.com/in-toto/attestation/blob/main/spec/v1/bundle.md)')
        elif fmt_lower == 'attestation blob':
            formatted.append('[Attestation Blob](https://github.com/moby/buildkit/blob/master/docs/attestations/attestation-storage.md#attestation-blob)')
        # Handle complex formats with parentheses like "Any (Suggested Attestation Bundle)"
        elif 'attestation bundle' in fmt_lower:
            result = fmt.replace('Attestation Bundle', '[Attestation Bundle](https://github.com/in-toto/attestation/blob/main/spec/v1/bundle.md)')
            result = result.replace('attestation bundle', '[Attestation Bundle](https://github.com/in-toto/attestation/blob/main/spec/v1/bundle.md)')
            formatted.append(result)
        elif 'sigstore bundle' in fmt_lower:
            result = fmt.replace('Sigstore Bundle', '[Sigstore Bundle](https://docs.sigstore.dev/about/bundle/)')
            result = result.replace('sigstore bundle', '[Sigstore Bundle](https://docs.sigstore.dev/about/bundle/)')
            formatted.append(result)
        elif 'cosign bundle' in fmt_lower:
            result = fmt.replace('Cosign Bundle', '[Cosign Bundle](https://github.com/sigstore/cosign/blob/main/specs/BUNDLE_SPEC.md)')
            result = result.replace('cosign bundle', '[Cosign Bundle](https://github.com/sigstore/cosign/blob/main/specs/BUNDLE_SPEC.md)')
            formatted.append(result)
        else:
            formatted.append(fmt)
    
    return ', '.join(formatted)

def format_visibility(visibility: List[str] | str) -> str:
    """Format the visibility field for the table."""
    if isinstance(visibility, str):
        visibility = [visibility]
    
    if not visibility:
        return "Unknown"
    
    return ', '.join(str(v).strip() for v in visibility)

def generate_table(sources: List[Dict[str, Any]]) -> str:
    """Generate markdown table from sources."""
    if not sources:
        return "No sources found.\n"
    
    # Build table
    lines = [
        "| Location | Alongside artifact? | Storage Format | Visibility |",
        "|----------|---------------------|--------|-----------|"
    ]
    
    for source in sources:
        location = f"{source['type']}-{source['name']}"
        besides = str(source['besides']).capitalize()
        format_str = format_format(source['format'])
        visibility = format_visibility(source['visibility'])
        
        lines.append(f"| {location} | {besides} | {format_str} | {visibility} |")
    
    return '\n'.join(lines) + "\n"

def update_readme(table: str):
    """Update the main README with the generated table."""
    with open(README_PATH, 'r') as f:
        content = f.read()
    
    # Find and replace the table
    # Look for the Summary section with ### (three hashes)
    marker = "### Summary\n"
    if marker in content:
        parts = content.split(marker)
        # Keep everything up to Summary, add Summary back, add new table
        new_content = parts[0] + marker + "\n\n" + table
        
        # Append any trailing content after the table section
        if len(parts) > 1:
            remaining = parts[1]
            # Find where the table ends and other content begins
            # Skip leading whitespace and table lines
            lines = remaining.split('\n')
            table_end = 0
            for i, line in enumerate(lines):
                # Stop when we hit a non-empty, non-table line
                if line.strip() and not line.strip().startswith('|'):
                    table_end = i
                    break
            
            # Append non-table content if any
            if table_end < len(lines):
                trailing = '\n'.join(lines[table_end:])
                if trailing.strip():
                    new_content += '\n' + trailing
    else:
        # Pattern didn't match
        new_content = content
    
    with open(README_PATH, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Updated {README_PATH}")

if __name__ == "__main__":
    print("Collecting attestation sources...")
    sources = collect_sources()
    print(f"Found {len(sources)} sources")
    
    print("Generating table...")
    table = generate_table(sources)
    
    print("Updating README...")
    update_readme(table)
    
    print("✓ Done!")

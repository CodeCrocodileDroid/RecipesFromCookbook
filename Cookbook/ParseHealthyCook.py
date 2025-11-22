import PyPDF2
import re
import json


def extract_recipes_by_page(pdf_path):
    """Extract recipes where each recipe is on a single page with specific structure."""
    recipes = []

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            # Check if this page has the recipe structure
            if not (re.search(r'INGREDIENTS:', text) and
                    re.search(r'INSTRUCTIONS:', text) and
                    re.search(r'NUTRIENT ANALYSIS', text)):
                print(f"Skipping page {page_num + 1} - doesn't match recipe structure")
                continue

            recipe = parse_recipe_page(text)
            if recipe:
                recipe['source_page'] = page_num + 1
                recipes.append(recipe)

    return recipes


def parse_recipe_page(text):
    """Parse a single recipe page with known structure."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None

    recipe = {
        'title': '',
        'servings': '',
        'ingredients': [],
        'instructions': [],
        'nutrient_analysis': ''
    }

    # Title is first line
    recipe['title'] = lines[0]

    # Find section indices
    sections = {
        'servings': None,
        'ingredients': None,
        'instructions': None,
        'nutrient': None
    }

    for i, line in enumerate(lines):
        if line.startswith('Serves:') and not sections['servings']:
            sections['servings'] = i
        elif 'INGREDIENTS:' in line and not sections['ingredients']:
            sections['ingredients'] = i
        elif 'INSTRUCTIONS:' in line and not sections['instructions']:
            sections['instructions'] = i
        elif 'NUTRIENT ANALYSIS' in line and not sections['nutrient']:
            sections['nutrient'] = i

    # Extract servings if exists
    if sections['servings']:
        recipe['servings'] = lines[sections['servings']].replace('Serves:', '').strip()

    # Extract ingredients
    if sections['ingredients'] and sections['instructions']:
        start = sections['ingredients'] + 1
        end = sections['instructions']
        recipe['ingredients'] = [line for line in lines[start:end] if line and not line.isspace()]

    # Extract instructions
    if sections['instructions'] and sections['nutrient']:
        start = sections['instructions'] + 1
        end = sections['nutrient']
        recipe['instructions'] = [line for line in lines[start:end] if line and not line.isspace()]

    # Extract nutrient analysis
    if sections['nutrient']:
        start = sections['nutrient']
        recipe['nutrient_analysis'] = '\n'.join([line for line in lines[start:] if line and not line.isspace()])

    return recipe


def save_recipes_to_json(recipes, output_file):
    """Save extracted recipes to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)


def main():
    pdf_path = 'cookbook.pdf'  # Replace with your PDF path
    output_file = 'extracted_recipes.json'

    print(f"Extracting recipes from {pdf_path}...")
    recipes = extract_recipes_by_page(pdf_path)

    print(f"Saving {len(recipes)} recipes to {output_file}...")
    save_recipes_to_json(recipes, output_file)

    print("Done!")
    if recipes:
        print("\nSample extracted recipe:")
        print(json.dumps(recipes[0], indent=2))


if __name__ == "__main__":
    main()
import PyPDF2
import re
from collections import defaultdict
import json


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


def parse_recipes(text):
    """Parse recipes from extracted text."""
    # This will vary greatly depending on your cookbook's structure
    recipes = []

    # Common patterns (you'll need to adjust these based on your PDF's structure)
    recipe_title_pattern = re.compile(r'^([A-Z][A-Za-z\s]+)\n', re.MULTILINE)
    ingredient_section_pattern = re.compile(r'Ingredients?:\s*\n(.+?)\n\n', re.DOTALL)
    instruction_section_pattern = re.compile(r'Instructions?|Method:\s*\n(.+?)(?=\n\n[A-Z]|\Z)', re.DOTALL)

    # Split text into potential recipe sections
    # This is a simple approach - you may need something more sophisticated
    sections = re.split(r'\n\s*\n', text)

    current_recipe = None

    for section in sections:
        # Check for recipe title
        title_match = recipe_title_pattern.match(section)
        if title_match:
            if current_recipe:
                recipes.append(current_recipe)
            current_recipe = {
                'title': title_match.group(1).strip(),
                'ingredients': [],
                'instructions': []
            }
            continue

        # Check for ingredients section
        if current_recipe and not current_recipe['ingredients']:
            ingredient_matches = re.findall(r'•\s*(.+?)\n|\d+\.\s*(.+?)\n|-\s*(.+?)\n', section)
            if ingredient_matches:
                for match in ingredient_matches:
                    # Get the first non-empty match group
                    ingredient = next(item for item in match if item)
                    current_recipe['ingredients'].append(ingredient.strip())
                continue

        # Check for instructions section
        if current_recipe and not current_recipe['instructions']:
            instruction_matches = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n\Z)', section)
            if instruction_matches:
                current_recipe['instructions'] = instruction_matches
                continue

    if current_recipe:
        recipes.append(current_recipe)

    return recipes


def save_recipes_to_json(recipes, output_file):
    """Save extracted recipes to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)


def main():
    pdf_path = 'Experiment1/cookbook.pdf'  # Replace with your PDF path
    output_file = 'Experiment1/extracted_recipes.json'

    print(f"Extracting text from {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)

    print("Parsing recipes...")
    recipes = parse_recipes(text)

    print(f"Saving recipes to {output_file}...")
    save_recipes_to_json(recipes, output_file)

    print(f"Successfully extracted {len(recipes)} recipes!")


if __name__ == "__main__":
    main()
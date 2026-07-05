import re

with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change flex-column back to flex-row
content = content.replace('d-flex flex-column align-items-center justify-content-end text-center', 'd-flex flex-row align-items-center justify-content-center pb-3 text-center')

# Remove <br> in titles (by replacing specific text)
titles_map = {
    'RESIDENTIAL<br>INTERIORS': 'RESIDENTIAL INTERIORS',
    'COMMERCIAL<br>SPACES': 'COMMERCIAL SPACES',
    'LIVING<br>ROOMS': 'LIVING ROOMS',
    'KITCHENS<br>&nbsp;': 'KITCHENS',
    'BEDROOMS<br>&nbsp;': 'BEDROOMS',
    'CUSTOM<br>FURNITURE': 'CUSTOM FURNITURE',
    'BEFORE & AFTER<br>TRANSFORMATIONS': 'BEFORE & AFTER TRANSFORMATIONS',
    'CAFE<br>INTERIORS': 'CAFE INTERIORS',
    'HOTEL<br>INTERIORS': 'HOTEL INTERIORS',
    'RESTAURANT<br>INTERIORS': 'RESTAURANT INTERIORS',
    'OFFICE<br>INTERIORS': 'OFFICE INTERIORS',
    'RETAIL<br>INTERIORS': 'RETAIL INTERIORS',
    'BAR & LOUNGE<br>INTERIORS': 'BAR & LOUNGE INTERIORS',
    'OUTDOOR &<br>TERRACE SPACES': 'OUTDOOR & TERRACE SPACES'
}
for old, new in titles_map.items():
    content = content.replace(f'<h6 class="category-card-title mb-0">{old}</h6>', f'<h6 class="category-card-title mb-0">{new}</h6>')

# Fix icon margin CSS (change margin-bottom: 8px to margin-right: 10px)
content = content.replace('margin-bottom: 8px;', 'margin-right: 10px; margin-bottom: 0;')

# Slightly adjust font size if needed (keep 13px but it was 13px already)

with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)

import re

with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change row to row-cols-5
content = content.replace('<div class="row g-3">', '<div class="row g-3 row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-5">')
# Remove individual col classes
content = re.sub(r'<div class="col-lg-2 col-md-4 col-sm-6">', '<div class="col">', content)

# Revert flex-row back to flex-column
content = content.replace('d-flex flex-row align-items-center justify-content-center pb-3 text-center', 'd-flex flex-column align-items-center justify-content-end text-center')

# Put line breaks back in titles (by replacing specific text)
titles_map = {
    'RESIDENTIAL INTERIORS': 'RESIDENTIAL<br>INTERIORS',
    'COMMERCIAL SPACES': 'COMMERCIAL<br>SPACES',
    'LIVING ROOMS': 'LIVING<br>ROOMS',
    'KITCHENS': 'KITCHENS<br>&nbsp;',
    'BEDROOMS': 'BEDROOMS<br>&nbsp;',
    'CUSTOM FURNITURE': 'CUSTOM<br>FURNITURE',
    'BEFORE & AFTER TRANSFORMATIONS': 'BEFORE & AFTER<br>TRANSFORMATIONS',
    'CAFE INTERIORS': 'CAFE<br>INTERIORS',
    'HOTEL INTERIORS': 'HOTEL<br>INTERIORS',
    'RESTAURANT INTERIORS': 'RESTAURANT<br>INTERIORS',
    'OFFICE INTERIORS': 'OFFICE<br>INTERIORS',
    'RETAIL INTERIORS': 'RETAIL<br>INTERIORS',
    'BAR & LOUNGE INTERIORS': 'BAR & LOUNGE<br>INTERIORS',
    'OUTDOOR & TERRACE SPACES': 'OUTDOOR &<br>TERRACE SPACES'
}
for old, new in titles_map.items():
    content = content.replace(f'<h6 class="category-card-title mb-0">{old}</h6>', f'<h6 class="category-card-title mb-0">{new}</h6>')

# Fix icon margin CSS
content = content.replace('margin-right: 10px; margin-bottom: 0;', 'margin-bottom: 8px;')

# Change font size back to 13px (from 15px/14px) and keep serif
content = content.replace('font-size: 15px;', 'font-size: 13px;')
content = content.replace('font-size: 14px;', 'font-size: 13px;')

with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)

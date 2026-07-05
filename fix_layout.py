with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change flex-row to flex-column
content = content.replace('d-flex flex-row align-items-end justify-content-center pb-3 text-center', 'd-flex flex-column align-items-center justify-content-center pb-3 text-center')
content = content.replace('d-flex flex-row align-items-end justify-content-center pb-4 text-center', 'd-flex flex-column align-items-center justify-content-center pb-3 text-center')

# Fix icon margin to be at the bottom instead of the right
content = content.replace('margin-right: 10px; margin-bottom: 0;', 'margin-bottom: 5px;')

# Put <br> back in the titles so they look like the reference image
titles_map = {
    'RESIDENTIAL INTERIORS': 'RESIDENTIAL<br>INTERIORS',
    'COMMERCIAL SPACES': 'COMMERCIAL<br>SPACES',
    'LIVING ROOMS': 'LIVING<br>ROOMS',
    'KITCHENS': 'KITCHENS',
    'BEDROOMS': 'BEDROOMS',
    'CUSTOM FURNITURE': 'CUSTOM<br>FURNITURE',
    'CAFE INTERIORS': 'CAFE<br>INTERIORS',
    'HOTEL INTERIORS': 'HOTEL<br>INTERIORS',
    'RESTAURANT INTERIORS': 'RESTAURANT<br>INTERIORS',
    'OFFICE INTERIORS': 'OFFICE<br>INTERIORS',
    'RETAIL INTERIORS': 'RETAIL<br>INTERIORS',
    'BAR & LOUNGE INTERIORS': 'BAR & LOUNGE<br>INTERIORS',
    'OUTDOOR & TERRACE SPACES': 'OUTDOOR &<br>TERRACE SPACES'
}
for old, new in titles_map.items():
    content = content.replace(f'<h6 class="category-card-title mb-0">{old}</h6>', f'<h6 class="category-card-title mb-0 text-center">{new}</h6>')

# Ensure BEFORE & AFTER is also centered
content = content.replace('<h6 class="category-card-title mb-0 text-start">BEFORE & AFTER<br>TRANSFORMATIONS</h6>', '<h6 class="category-card-title mb-0 text-center">BEFORE & AFTER<br>TRANSFORMATIONS</h6>')
content = content.replace('<h6 class="category-card-title mb-0 text-start">BAR & LOUNGE<br>INTERIORS</h6>', '<h6 class="category-card-title mb-0 text-center">BAR & LOUNGE<br>INTERIORS</h6>')
content = content.replace('<h6 class="category-card-title mb-0 text-start">OUTDOOR &<br>TERRACE SPACES</h6>', '<h6 class="category-card-title mb-0 text-center">OUTDOOR &<br>TERRACE SPACES</h6>')

with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)

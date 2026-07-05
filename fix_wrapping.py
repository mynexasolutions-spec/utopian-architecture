with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the text for card 7 to break the line and add text-start
content = content.replace('<h6 class="category-card-title mb-0">BEFORE & AFTER TRANSFORMATIONS</h6>', '<h6 class="category-card-title mb-0 text-start">BEFORE & AFTER<br>TRANSFORMATIONS</h6>')

# Do the same for other long titles if they are causing issues, though user only mentioned Before & After
content = content.replace('<h6 class="category-card-title mb-0">BAR & LOUNGE INTERIORS</h6>', '<h6 class="category-card-title mb-0 text-start">BAR & LOUNGE<br>INTERIORS</h6>')
content = content.replace('<h6 class="category-card-title mb-0">OUTDOOR & TERRACE SPACES</h6>', '<h6 class="category-card-title mb-0 text-start">OUTDOOR &<br>TERRACE SPACES</h6>')

with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)

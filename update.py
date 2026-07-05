import re

with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change container
content = content.replace('<div class="container">\n        <div class="text-center mb-5">', '<div class="container-fluid px-2 px-lg-4">\n        <div class="text-center mb-5">')

# Change col-lg-3 to col-lg-2
content = content.replace('col-lg-3 col-md-4 col-sm-6', 'col-lg-2 col-md-4 col-sm-6')

# Change flex-column to flex-row and fix alignments
content = content.replace('d-flex flex-column align-items-center justify-content-end text-center', 'd-flex flex-row align-items-center justify-content-center pb-3 text-center')

# Remove <br> in titles and change icons
content = re.sub(r'<i class=\"fa fa-[a-zA-Z0-9\-]+ category-card-icon\"></i>', '<i class=\"fa fa-image category-card-icon\"></i>', content)
content = content.replace('<br>', ' ')
content = content.replace('<br>&nbsp;', '')
content = content.replace('&nbsp;', '')

# Update CSS for icon margin instead of margin-bottom
content = content.replace('margin-bottom: 8px;', 'margin-right: 10px; margin-bottom: 0;')

# Change font for title
content = content.replace('font-size: 13px;', 'font-family: \'Playfair Display\', serif;\n        font-size: 15px;')

with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)

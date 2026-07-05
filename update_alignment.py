with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix alignment so items stay at the bottom of the overlay
content = content.replace('d-flex flex-row align-items-center justify-content-center pb-3 text-center', 'd-flex flex-row align-items-end justify-content-center pb-3 text-center')

with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)

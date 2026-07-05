with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace CSS for overlay
old_css = '''      .explore-card-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(30, 24, 18, 0.95);
        padding: 15px 10px;
      }'''
new_css = '''      .explore-card-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(30, 24, 18, 0.95);
        padding: 20px 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
      }'''
content = content.replace(old_css, new_css)

# Remove icon margin-right since we use gap now
old_icon_css = '''      .category-card-icon {
        color: #cca471;
        font-size: 24px;
        margin-right: 10px; margin-bottom: 0;
      }'''
new_icon_css = '''      .category-card-icon {
        color: #cca471;
        font-size: 24px;
        margin: 0;
      }'''
content = content.replace(old_icon_css, new_icon_css)

# Clean up HTML classes since we moved flex to CSS
content = content.replace('explore-card-overlay d-flex flex-row align-items-end justify-content-center pb-3 text-center', 'explore-card-overlay')

with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)

import re

with open('templates/pages/portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_tag = '<div class="row g-3 row-cols-2 row-cols-sm-2 row-cols-md-3 row-cols-lg-5">'
start_idx = content.find(start_tag)
if start_idx != -1:
    new_loop = '''
          {% for cat in portfolio_categories %}
          <div class="col">
            <a href="{{ url_for('portfolio', category=cat.slug) }}" class="text-decoration-none">
              <div class="explore-card position-relative overflow-hidden">
                 <img src="{{ cat.image_url if 'cloudinary' in cat.image_url else url_for('static', filename=cat.image_url) }}" alt="{{ cat.name }}" class="w-100 h-100 object-fit-cover">
                 <div class="explore-card-overlay">
                    <i class="fa {{ cat.icon_class }} category-card-icon"></i>
                    <h6 class="category-card-title mb-0 text-start">{{ cat.name|safe }}</h6>
                 </div>
              </div>
            </a>
          </div>
          {% else %}
          <div class="col-12 text-center py-5">
             <h5 class="text-muted">No categories found.</h5>
          </div>
          {% endfor %}
'''
    pattern = re.compile(r'<!-- Card 1 -->.*<!-- Card 14 -->.*?</div>\s*</a>\s*</div>', re.DOTALL)
    new_content = pattern.sub(new_loop, content)
    
    with open('templates/pages/portfolio.html', 'w', encoding='utf-8') as out:
        out.write(new_content)
        print('Updated portfolio.html with Jinja loop!')
else:
    print('Start tag not found!')

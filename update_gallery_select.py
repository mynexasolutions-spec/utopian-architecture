with open('templates/admin/gallery.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find the select block
select_pattern = re.compile(r'<select name="category" class="form-select" required id="categorySelect">.*?</select>', re.DOTALL)
match = select_pattern.search(content)

if match:
    old_select = match.group(0)
    new_select = '''<select name="category" class="form-select" required id="categorySelect">
                            <option value="">-- Select Category --</option>
                            {% for cat in portfolio_categories %}
                            <option value="{{ cat.slug }}">{{ cat.name }}</option>
                            {% endfor %}
                            <option value="other">Other (Specify Below)</option>
                        </select>'''
    content = content.replace(old_select, new_select)
    with open('templates/admin/gallery.html', 'w', encoding='utf-8') as f:
        f.write(content)
        print("Updated gallery.html with dynamic categories.")

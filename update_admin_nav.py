with open('templates/admin/layout.html', 'r', encoding='utf-8') as f:
    content = f.read()

nav_item = '''
            <li class="nav-item">
                <a class="nav-link" href="{{ url_for('admin_gallery') }}">
                    <i class="fas fa-fw fa-images"></i>
                    <span>Gallery</span>
                </a>
            </li>
'''
new_nav_item = '''
            <li class="nav-item">
                <a class="nav-link" href="{{ url_for('admin_gallery') }}">
                    <i class="fas fa-fw fa-images"></i>
                    <span>Gallery Images</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="{{ url_for('admin_portfolio_categories') }}">
                    <i class="fas fa-fw fa-th-large"></i>
                    <span>Portfolio Categories</span>
                </a>
            </li>
'''
content = content.replace(nav_item, new_nav_item)

with open('templates/admin/layout.html', 'w', encoding='utf-8') as f:
    f.write(content)

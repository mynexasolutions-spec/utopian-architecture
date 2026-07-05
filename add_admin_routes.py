from flask import request, redirect, url_for, flash, render_template, abort, session
from functools import wraps
from app import app, db, PortfolioCategory
from helpers import upload_image_to_cloudinary, delete_image_from_cloudinary

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Add these lines to app.py (just generating the block to append)
routes = '''
# ---------------------------------------------------------
# Admin Portfolio Categories Routes
# ---------------------------------------------------------

@app.route('/admin/portfolio-categories')
@login_required
def admin_portfolio_categories():
    categories = PortfolioCategory.query.order_by(PortfolioCategory.position).all()
    return render_template('admin/portfolio_categories.html', categories=categories)

@app.route('/admin/portfolio-categories/add', methods=['POST'])
@login_required
def add_portfolio_category():
    name = request.form.get('name')
    slug = request.form.get('slug')
    icon_class = request.form.get('icon_class', 'fa-image')
    position = request.form.get('position', 0, type=int)
    
    file = request.files.get('image')
    image_url = None
    if file and file.filename != '':
        image_url = upload_image_to_cloudinary(file, folder="portfolio_categories")
        
    if not image_url:
        flash('Background image is required.', 'danger')
        return redirect(url_for('admin_portfolio_categories'))

    cat = PortfolioCategory(
        name=name,
        slug=slug,
        icon_class=icon_class,
        image_url=image_url,
        position=position
    )
    db.session.add(cat)
    db.session.commit()
    flash('Portfolio category added successfully!', 'success')
    return redirect(url_for('admin_portfolio_categories'))

@app.route('/admin/portfolio-categories/edit/<int:id>', methods=['POST'])
@login_required
def edit_portfolio_category(id):
    cat = PortfolioCategory.query.get_or_404(id)
    cat.name = request.form.get('name')
    cat.slug = request.form.get('slug')
    cat.icon_class = request.form.get('icon_class', 'fa-image')
    cat.position = request.form.get('position', 0, type=int)
    
    file = request.files.get('image')
    if file and file.filename != '':
        new_image_url = upload_image_to_cloudinary(file, folder="portfolio_categories")
        if new_image_url:
            if cat.image_url:
                delete_image_from_cloudinary(cat.image_url)
            cat.image_url = new_image_url

    db.session.commit()
    flash('Portfolio category updated successfully!', 'success')
    return redirect(url_for('admin_portfolio_categories'))

@app.route('/admin/portfolio-categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_portfolio_category(id):
    cat = PortfolioCategory.query.get_or_404(id)
    if cat.image_url:
        delete_image_from_cloudinary(cat.image_url)
    db.session.delete(cat)
    db.session.commit()
    flash('Portfolio category deleted successfully!', 'success')
    return redirect(url_for('admin_portfolio_categories'))
'''

with open('app.py', 'a', encoding='utf-8') as f:
    f.write(routes)

from app import app, db, PortfolioCategory

with app.app_context():
    # Create the new table
    db.create_all()

    # Seed the initial data
    initial_categories = [
        {'name': 'RESIDENTIAL INTERIORS', 'slug': 'residential', 'icon_class': 'img/gallery_icons/1.png', 'image_url': 'img/gallery/living_room/lr1.webp', 'position': 1},
        {'name': 'COMMERCIAL SPACES', 'slug': 'commercial', 'icon_class': 'img/gallery_icons/2.png', 'image_url': 'img/gallery/office/office1.webp', 'position': 2},
        {'name': 'LIVING ROOMS', 'slug': 'living-room', 'icon_class': 'img/gallery_icons/3.png', 'image_url': 'img/gallery/living_room/lr1.webp', 'position': 3},
        {'name': 'KITCHENS', 'slug': 'kitchen', 'icon_class': 'img/gallery_icons/4.png', 'image_url': 'img/gallery/kitchen/kit1.webp', 'position': 4},
        {'name': 'BEDROOMS', 'slug': 'bedroom', 'icon_class': 'img/gallery_icons/5.png', 'image_url': 'img/gallery/bedroom/bed1.webp', 'position': 5},
        {'name': 'CUSTOM FURNITURE', 'slug': 'sofaset', 'icon_class': 'img/gallery_icons/6.png', 'image_url': 'img/gallery/sofaset/sofa-set.webp', 'position': 6},
        {'name': 'BEFORE & AFTER TRANSFORMATIONS', 'slug': 'other', 'icon_class': 'img/gallery_icons/7.png', 'image_url': 'img/gallery/other/entertainmentcenter.webp', 'position': 7},
        {'name': 'CAFE INTERIORS', 'slug': 'cafe', 'icon_class': 'img/gallery_icons/8.png', 'image_url': 'img/gallery/office/office1.webp', 'position': 8},
        {'name': 'HOTEL INTERIORS', 'slug': 'hotel', 'icon_class': 'img/gallery_icons/9.png', 'image_url': 'img/gallery/bedroom/bed1.webp', 'position': 9},
        {'name': 'RESTAURANT INTERIORS', 'slug': 'restaurant', 'icon_class': 'img/gallery_icons/10.png', 'image_url': 'img/gallery/kitchen/kit1.webp', 'position': 10},
        {'name': 'OFFICE INTERIORS', 'slug': 'office', 'icon_class': 'img/gallery_icons/11.png', 'image_url': 'img/gallery/office/office1.webp', 'position': 11},
        {'name': 'RETAIL INTERIORS', 'slug': 'retail', 'icon_class': 'img/gallery_icons/12.png', 'image_url': 'img/gallery/other/entertainmentcenter.webp', 'position': 12},
        {'name': 'BAR & LOUNGE INTERIORS', 'slug': 'bar', 'icon_class': 'img/gallery_icons/13.png', 'image_url': 'img/gallery/kitchen/kit1.webp', 'position': 13},
        {'name': 'OUTDOOR & TERRACE SPACES', 'slug': 'outdoor', 'icon_class': 'img/gallery_icons/14.png', 'image_url': 'img/gallery/other/entertainmentcenter.webp', 'position': 14}
    ]

    for data in initial_categories:
        exists = PortfolioCategory.query.filter_by(slug=data['slug']).first()
        if not exists:
            cat = PortfolioCategory(
                name=data['name'],
                slug=data['slug'],
                icon_class=data['icon_class'],
                image_url=data['image_url'],
                position=data['position']
            )
            db.session.add(cat)
    
    db.session.commit()
    print("Database seeded with portfolio categories!")

from mcli import create_view, delete_view, validate_views, click_group

click_group.add(create_view)
click_group.add(delete_view)
click_group.add(validate_views)
click_group()

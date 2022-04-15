from mcli import create_view, delete_view, validate_views, click_group

click_group.add_command(create_view)
click_group.add_command(delete_view)
click_group.add_command(validate_views)
click_group()

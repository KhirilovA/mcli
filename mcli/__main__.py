from mcli import (create_view,
                  delete_view,
                  validate_views,
                  click_group,
                  create_model,
                  create_templates_views,
                  create_templates_model)

click_group.add_command(create_view)
click_group.add_command(delete_view)
click_group.add_command(validate_views)
click_group.add_command(create_model)
click_group.add_command(create_templates_views)
click_group.add_command(create_templates_model)
click_group()

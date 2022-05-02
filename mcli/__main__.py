from mcli import (
                  click_group,
                  create_views,
                  create_mvc
                  )

click_group.add_command(create_views)
click_group.add_command(create_mvc)
click_group()

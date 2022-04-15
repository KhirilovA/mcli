from pyfiglet import Figlet
import fire
from mcli import create_view


f = Figlet(font='slant')
print(f.renderText('MCLI!'))
fire.Fire(create_view)

import os
from configparser import ConfigParser
from common.load_balancer import alb as alb
from common.load_balancer import nlb as nlb
#import alb as alb
#import nlb as nlb

class LBSelection:
  def createResources(self, ns):

    config = ConfigParser()

    # Get default LB settings
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'default.ini')
    config.read(filename)
    #print({section: dict(config[section]) for section in config.sections()})

    # Get tier specific settings
    config.read(f'{ns}.ini')
    #print({section: dict(config[section]) for section in config.sections()})
    
    if config['main']['lb_type'] == 'application':
      alb.ALBResources.createResources(self, ns, config)
    elif config['main']['lb_type'] == 'network':
      nlb.NLBResources.createResources(self, ns, config)
__version__ = '1.0.4.post1'

from siloprompts.manager import PromptManager
from siloprompts.web import create_app

__all__ = ['PromptManager', 'create_app', '__version__']

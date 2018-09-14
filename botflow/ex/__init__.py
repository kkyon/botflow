from .http import HttpLoader
from .aiofile import AioFile

Fetch=HttpLoader
__all__=["AioFile","HttpLoader","Fetch"]
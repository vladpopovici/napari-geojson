try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.1"


from ._reader import napari_get_reader


__all__ = ['napari_get_reader']

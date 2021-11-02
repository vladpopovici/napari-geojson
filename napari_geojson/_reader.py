"""
NAPARI_GEOJSON
"""
from napari_plugin_engine import napari_hook_implementation

import numpy as np
import shapely
import shapely.geometry as shg
import geojson
from pathlib import Path

@napari_hook_implementation
def napari_get_reader(path):
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, str) and Path(path).suffix.lower() == '.geojson':
        return geojson_reader
    return None


def geojson_reader(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    layers = []

    defaults = dict(shape_edge_width=100, shape_edge_color='red', shape_face_color='blue', opacity=0.25,
                    blending='opaque')

    for pth in paths:
        # for each GeoJSON file create a new layer (Shape)
        layer_data = []
        layer_shape_type = []
        layer_shape_edge_width = []
        layer_shape_edge_color = []
        layer_shape_face_color = []
        with open(pth, 'r') as fp:
            geo = geojson.load(fp)
            if geo["type"].lower() != "featurecollection":
                raise RuntimeError("Need a FeatureCollection as annotation! Got: " + geo["type"])
            for obj in geo['features']:
                shape = shg.shape(obj['geometry'])
                if not shape.is_valid:
                    # TODO: maybe raise an exception?
                    continue
                if shape.geom_type.lower() == 'point':
                    pass
                elif shape.geom_type.lower() == 'linestring':
                    pass
                elif shape.geom_type.lower() == 'polygon':
                    layer_shape_type.append('polygon')
                else:
                    continue

                # TODO: replace with values read from 'properties' of each shape
                layer_shape_edge_width.append(defaults['shape_edge_width'])
                layer_shape_edge_color.append(defaults['shape_edge_color'])
                layer_shape_face_color.append(defaults['shape_face_color'])

                layer_data.append(geom2xy(shape))

        layers.append(
            (layer_data,
             {
                 'shape_type': layer_shape_type,
                 'edge_width': layer_shape_edge_width,
                 'edge_color': layer_shape_edge_color,
                 'face_color': layer_shape_face_color,
                 'opacity': defaults['opacity'],
                 'blending': defaults['blending']
             },
             'shapes')
        )
    return layers
##


def geom2xy(geom: shapely.geometry, as_type=None) -> np.array:
    """Return the coordinates of a 2D geometrical object as a numpy array (N x 2).

    :param geom: shapely.geometry
        a 2D geometrical object

    :return:
        numpy.array
    """
    xy = list(zip(*geom.exterior.coords.xy))
    if as_type is None:
        z = np.array(xy)
    else:
        z = np.array(xy, dtype=as_type)

    return z
##
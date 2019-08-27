import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import geojson
from shapely.geometry import shape, GeometryCollection, Point, Polygon, mapping
import shapely.ops
import pyproj
import rasterio
from rasterio.mask import mask

'''
A number of helper functions to construct a time-series from geotiffs sampled
along specified distances (i.e., 100m, 500m, 1000m)
'''


def geojson_to_numpy(path):
    '''
    Convert geoJson to numpy array.

    Arguments:
        path (str)      to geoJson file

    Returns:
        array           numpy array of coordinates
    '''
    with open(path) as f:
        gj = geojson.load(f)["features"][0]['geometry']['coordinates']
    numpy_array = np.array(gj)
    return(numpy_array)



def convert_crs(coordinates, src_crs, dst_crs):
    '''
    Converts array of coordinates between src_crs and dst_crs.

    Arguments:
        coordinates (array): array of coordinates to reproject
        src_crs, dst_crs (str): crs EPSG code

    Returns:
        array: reprojected coordinates
    '''
    orig_crs = pyproj.Proj('+init='+src_crs)
    dest_crs = pyproj.Proj('+init='+dst_crs)
    reproj = np.zeros((len(coordinates),2))
    for i in range(0, len(coordinates)):
        reproj[i] = pyproj.transform(orig_crs, dest_crs, coordinates[i,0], coordinates[i,1])
    return(reproj)


def find_intersect(line1, line2):
    '''
    Find coordinate of intersection between centerline and terminus

    Arguments:
        line1, line2 (array): numpy array of coordinates

    Returns:
        array: array with coordinate of line intersection
    '''
    intsec = LineString(line1).intersection(LineString(line2))
    isec = np.array(intsec)
    return(isec)


#p = find_intersect(cl_utm, tmns_utm)


def get_points_on_line(line2cut, cutwith, dist):
    '''
    Splits line2cut with cutwith line and returns array of coordinates of points
    at distances listed in dist.
    NOTE: Distances calculated in direction in which line was originally traced.

    Arguments:
        line2cut (array): coordinates of line to be cut
        cutwith (array): coordinates of line used to cut
        dist (list): list of distances

    Returns:
        GeometryCollection: of new cut line
        array: coordinates of selected points (x, y)
    '''
    ln1 = LineString(line2cut)
    ln2 = LineString(cutwith)
    cutln = shapely.ops.split(ln1, ln2)
    dist_pts = np.zeros((len(dist),2))
    for i in range(0, len(dist)):
        pt = cutln[1].interpolate(dist[i])
        dist_pts[i] = np.array((np.array(pt)[0], np.array(pt)[1]))
    return(cutln, dist_pts)


#dist = ([100, 500, 1000])
#cutline, dists_from_terminus = get_points_on_line(cl_utm, tmns_utm, dist)
#print(dists_from_terminus)


def median_of_square(fp, point, pt_crs, l_side):
    '''
    Returns median value of a geotiff within a l-sided square around point P.

    Arguments:
        fp (str): filepath to GeoTiff
        point (array): x,y coordinates in pt_crs of point P.
        pt_crs (str): EPSG-code of point coordinate reference system
        l_side (int): side length (in pixels) of square arount point to derive mean value from.

    Returns:
        ndarray: (row, column) image index of points
        float: median value of all points within defined square
    '''
    #import tiff and get row, col index of wanted point
    with rasterio.open(path + "GeoTiff-BigTiff_20190108T154850_20190120_Orb_Stack_vel.tif") as src:
        # Use pyproj to convert point coordinates
        img_crs = pyproj.Proj(src.crs) # Pass CRS of image from rasterio
        pt_crs = pyproj.Proj(init=pt_crs)
        img_x, img_y = pyproj.transform(pt_crs, img_crs, point[0], point[1])
        row, col = src.index(img_x, img_y)
        values = src.read(1)
        median_value = np.median(values[row-(np.int(np.floor(l_side/2))) : row + (np.int(np.floor(l_side/2))),
                            col - (np.int(np.floor(l_side/2))) : col + (np.int(np.floor(l_side/2)))])
        return(row, col, median_value)

#fp = path + "GeoTiff-BigTiff_20190108T154850_20190120_Orb_Stack_vel.tif"
#point = dists_from_terminus[0]
#row, col, median_value = median_of_square(fp, point, 'epsg:32607', 15)


def median_of_circle(fp, point, pt_crs, r_circ, line = None):
    '''
    Returns median value of a geotiff within a circle with radius r_circ around
    point P. If line is given, circle will be intersected with line and merged
    if line cuts circle, and the median taken from the merged polygon.

    Arguments:
        fp (str): filepath to GeoTiff
        point (array): x,y coordinates in pt_crs of point P.
        pt_crs (str): EPSG-code of point coordinate reference system
        l_side (int): radius in meters around point to derive median value from.

    Optional argument:
        line (array): ndarray with coordinates of a polyline.

    Returns:
        float: median value of all points within defined circle
        array: coordinates of polygon around point.
    '''
    # define window in meters regardless of coordinate system of raster
    circ_poly = Point(point).buffer(r_circ)
    if line is not None:
        print('Line overlaps circle:')
    # see if circle overlaps with terminus.
        check = circ_poly.intersects(LineString(line))
        print(check)
        if check == True:
            # split circle with terminus if it overlaps
            cut_circ = shapely.ops.split(circ_poly, LineString(line))
            #print(cut_circ[0].length)
            #print(cut_circ[1].length)
            if cut_circ[0].length > cut_circ[1].length:
                circ_poly = cut_circ[0]
            else:
                circ_poly = cut_circ[1]
    #reproject circle to crs of image
    circ_poly_coords = np.array(circ_poly.exterior.coords)
    circ_reproj = np.zeros((len(circ_poly_coords),2))
    with rasterio.open(fp) as src:
        img_crs = pyproj.Proj(src.crs) # Pass CRS of image from rasterio
        pt_crs = pyproj.Proj(init=pt_crs)
        for i in range(0, len(circ_reproj)):
            circ_reproj[i]= pyproj.transform(pt_crs, img_crs, circ_poly_coords[i,0], circ_poly_coords[i,1])
        circ_reproj_poly = Polygon(circ_reproj)
        circ = [mapping(circ_reproj_poly)]
        out_image, out_transform = mask(src, circ, crop=True)
        out_meta = src.meta.copy()
        median_value = np.median(out_image)
    return(median_value, circ_poly_coords)


#median_value, poly = median_of_circle(fp, point, 'epsg:32607', 100, tmns_utm)


'''
#could return out_meta, out_image, and out_transform from median_of_circle
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
with rasterio.open(path + "Testmasked.tif", "w", **out_meta) as dest:
    dest.write(out_image)
'''

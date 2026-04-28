# import required libraries
import geopandas as gpd
import pandas as pd
import numpy as np
import os, glob, math, json
from matplotlib import pyplot as plt
from copy import deepcopy
from shapely.geometry import box
from rtree import index
from shapely.validation import make_valid

# define a function to merge touching polygons in adjacent tiles 
def merge_adjacent_tiles(gdf, folder, OVERLAP_THRESHOLD, verbose=True):
    main_gdf = deepcopy(gdf.explode(index_parts=False).reset_index())

    main_gdf['id'] = main_gdf.index
    main_gdf['merge_id'] = -1
    main_gdf['dissolve_id'] = -1

    # remove the precision of the coordinates because some of them cause trouble after 7-8 decimal places
    main_gdf['geometry'] = main_gdf['geometry'].apply(lambda geom: geom.__class__(
        [(
            math.floor(coord[0]),
            math.floor(coord[1])
        ) for coord in list(geom.exterior.coords)]
    )).buffer(0)

    dissolve_n = 0

    for segment in main_gdf.name.unique():
            #print(segment)

            # the row and column index to find neighbours
            if 'Enhanced' in folder:
                row, col = segment.split('_')[3:5]
            else:
                row, col = segment.split('_')[2:4]

            row = int(row)
            col = int(col)

            # get the neighbours of the layer (doing row and column in two lines because we don't want diagonal neighbours)
            neighbours = [segment.replace(f'_{row}_{col}_', f'_{y}_{x}_') for y in [row] for x in [col-1, col+1]]
            neighbours = neighbours + [segment.replace(f'_{row}_{col}_', f'_{y}_{x}_') for y in [row-1, row+1] for x in [col]]

            # double check that the generated neighbours actually exist (helps for test layers at the edge)
            # this is basically an intersection of two lists
            neighbours = list(set(neighbours) & set(main_gdf.name.unique()))

            # get the test gdf
            test_gdf = main_gdf.loc[main_gdf.name == segment]

            # get the neighbour gdfs
            neighbour_gdf = main_gdf.loc[main_gdf.name.isin(neighbours)]

            # for every polygon in test gdf check if it touches poly in another gdf but intersection area is none
            for test_idx, test_row in test_gdf.iterrows():
                for neighbour_idx, neighbour_row in neighbour_gdf.iterrows():
                    if test_row.geometry.touches(neighbour_row.geometry) and \
                        gpd.overlay(test_gdf.loc[test_gdf.id == test_row.id], 
                                    neighbour_gdf.loc[neighbour_gdf.id == neighbour_row.id], 
                                    how='intersection', keep_geom_type=False).shape[0] > 0:

                            """
                            # option 1: using centroids, get the driection to check which side it touches
                            test_centroid = test_gdf.loc[test_gdf.id == test_row.id].geometry.centroid.values[0]
                            neighbour_centroid = neighbour_gdf.loc[neighbour_gdf.id == neighbour_row.id].geometry.centroid.values[0]

                            destination_x, origin_x, destination_y, origin_y = neighbour_centroid.x, test_centroid.x, neighbour_centroid.y, test_centroid.y
                            direction = direction_lookup(destination_x, origin_x, destination_y, origin_y)
                            """

                            # option 2: to get the direction, one can also use file names :)
                            if 'Enhanced' in folder:
                                test_x, test_y = int(test_row['name'].split('_')[3]), int(test_row['name'].split('_')[4])
                                neighbour_x, neighbour_y = int(neighbour_row['name'].split('_')[3]), int(neighbour_row['name'].split('_')[3])
                            else:
                                test_x, test_y = int(test_row['name'].split('_')[2]), int(test_row['name'].split('_')[3])
                                neighbour_x, neighbour_y = int(neighbour_row['name'].split('_')[2]), int(neighbour_row['name'].split('_')[3])

                            if test_x == neighbour_x:
                                if test_y > neighbour_y:
                                    direction = 'N'
                                else:
                                    direction = 'S'
                            else:
                                if test_x > neighbour_x:
                                    direction = 'W'
                                else:
                                    direction = 'E'

                            def check_coordinate_list_depth(in_list, n=0):
                                n += 1
                                if type(in_list[0]) == type(list()):
                                    n = check_coordinate_list_depth(in_list[0], n=n)
                                return n

                            if direction in ['N', 'S', 'E', 'W']:
                                # get the bounds of test and neighbour polygon
                                test_json = json.loads(test_gdf.loc[test_gdf.id == test_row.id].to_json())

                                # somehow multipolygons are not exploded, in such cases the list depth is 4 instead of 3
                                if check_coordinate_list_depth(test_json['features'][0]['geometry']['coordinates']) < 4:
                                    try:
                                        test_coordinates = np.concatenate(test_json['features'][0]['geometry']['coordinates'])
                                    except:
                                        test_coordinates = np.concatenate(test_json['features'][0]['geometry']['coordinates'], axis=1).reshape(-1, 2)
                                else:
                                    try:
                                        test_coordinates = np.concatenate([b for a in test_json['features'][0]['geometry']['coordinates'] for b in a])
                                    except:
                                        test_coordinates = np.concatenate([b for a in test_json['features'][0]['geometry']['coordinates'] for b in a], axis=1).reshape(-1, 2)
                                [test_xmin, test_ymin], [test_xmax, test_ymax] = test_coordinates.min(axis=0), test_coordinates.max(axis=0)

                                neighbour_json = json.loads(neighbour_gdf.loc[neighbour_gdf.id == neighbour_row.id].to_json())

                                # somehow multipolygons are not exploded, in such cases the list depth is 4 instead of 3
                                if check_coordinate_list_depth(neighbour_json['features'][0]['geometry']['coordinates']) < 4:
                                    try:
                                        neighbour_coordinates = np.concatenate(neighbour_json['features'][0]['geometry']['coordinates'])
                                    except:
                                        neighbour_coordinates = np.concatenate(neighbour_json['features'][0]['geometry']['coordinates'], axis=1).reshape(-1, 2)
                                else:
                                    try:
                                        neighbour_coordinates = np.concatenate([b for a in neighbour_json['features'][0]['geometry']['coordinates'] for b in a])
                                    except:
                                        neighbour_coordinates = np.concatenate([b for a in neighbour_json['features'][0]['geometry']['coordinates'] for b in a], axis=1).reshape(-1, 2)

                                [neighbour_xmin, neighbour_ymin], [neighbour_xmax, neighbour_ymax] = neighbour_coordinates.min(axis=0), neighbour_coordinates.max(axis=0)


                                def get_overlap(test_coords, neighbour_coords, direction):
                                    test_lon, test_lat = test_coords[:, 0], test_coords[:, 1]
                                    neighbour_lon, neighbour_lat = neighbour_coords[:, 0], neighbour_coords[:, 1]

                                    if direction == 'E':
                                        # get ymin and ymax of test poly using max longitude index of test
                                        test_edge_coords = test_coords[np.where(test_lon == test_lon.max()), :]
                                        test_ymin, test_ymax = test_edge_coords[0][:, 1].min(), test_edge_coords[0][:, 1].max()

                                        # get ymin and ymax of neighbour poly using min latitude index of neighbour
                                        neighbour_edge_coords = neighbour_coords[np.where(neighbour_lon == neighbour_lon.min()), :]
                                        neighbour_ymin, neighbour_ymax = neighbour_edge_coords[0][:, 1].min(), neighbour_edge_coords[0][:, 1].max()

                                    elif direction == 'W':
                                        # get xmin and xmax of test poly using min latitude index of test
                                        test_edge_coords = test_coords[np.where(test_lat == test_lat.min()), :]
                                        test_ymin, test_ymax = test_edge_coords[0][:, 1].min(), test_edge_coords[0][:, 1].max()

                                        # get xmin and xmax of neighbour poly using max latitude index of neighbour
                                        neighbour_edge_coords = neighbour_coords[np.where(neighbour_lat == neighbour_lat.max()), :]
                                        neighbour_ymin, neighbour_ymax = neighbour_edge_coords[0][:, 1].min(), neighbour_edge_coords[0][:, 1].max()

                                    elif direction == 'N':
                                        # get xmin and xmax of test poly using max latitude index of test
                                        test_edge_coords = test_coords[np.where(test_lat == test_lat.max()), :]
                                        test_xmin, test_xmax = test_edge_coords[0][:, 0].min(), test_edge_coords[0][:, 0].max()

                                        # get xmin and xmax of neighbour poly using min latitude index of neighbour
                                        neighbour_edge_coords = neighbour_coords[np.where(neighbour_lat == neighbour_lat.min()), :]
                                        neighbour_xmin, neighbour_xmax = neighbour_edge_coords[0][:, 0].min(), neighbour_edge_coords[0][:, 0].max()

                                    elif direction == 'S':
                                        # get xmin and xmax of test poly using min latitude index of test
                                        test_edge_coords = test_coords[np.where(test_lat == test_lat.min()), :]
                                        test_xmin, test_xmax = test_edge_coords[0][:, 0].min(), test_edge_coords[0][:, 0].max()

                                        # get xmin and xmax of neighbour poly using max latitude index of neighbour
                                        neighbour_edge_coords = neighbour_coords[np.where(neighbour_lat == neighbour_lat.max()), :]
                                        neighbour_xmin, neighbour_xmax = neighbour_edge_coords[0][:, 0].min(), neighbour_edge_coords[0][:, 0].max()

                                    # calculate the overlap
                                    test_overlap_percent, neighbour_overlap_percent = 0, 0
                                    if direction in ['N', 'S']:
                                        test_delta_x = test_xmax - test_xmin
                                        neighbour_delta_x = neighbour_xmax - neighbour_xmin

                                        if (test_delta_x > 0) and (neighbour_delta_x > 0):
                                            overlap_width = min(int(test_xmax), int(neighbour_xmax)) - max(int(test_xmin), int(neighbour_xmin))
                                            test_overlap_percent = 100 * overlap_width / (test_delta_x)
                                            neighbour_overlap_percent = 100 * overlap_width / (neighbour_delta_x)

                                    elif direction in ['E', 'W']:
                                        test_delta_y = test_ymax - test_ymin
                                        neighbour_delta_y = neighbour_ymax - neighbour_ymin

                                        if (test_delta_y > 0) and (neighbour_delta_y > 0):
                                            overlap_width = min(int(test_ymax), int(neighbour_ymax)) - max(int(test_ymin), int(neighbour_ymin))
                                            test_overlap_percent = 100 * overlap_width / (test_delta_y)
                                            neighbour_overlap_percent = 100 * overlap_width / (neighbour_delta_y)

                                    return test_overlap_percent, neighbour_overlap_percent

                                test_overlap_perc, neighbour_overlap_perc = get_overlap(test_coordinates.astype(int),
                                                                                              neighbour_coordinates.astype(int),
                                                                                              direction)

                                # if overlap is more than the threshold, update the records in the main GDF
                                if (test_overlap_perc > OVERLAP_THRESHOLD) and (neighbour_overlap_perc > OVERLAP_THRESHOLD):
                                    main_gdf.loc[test_idx, 'merge_id'] = neighbour_idx
                                    main_gdf.loc[neighbour_idx, 'merge_id'] = test_idx

                                    # if either test or neighbour gdf has already been updated, use existing dissolve id
                                    if (main_gdf.loc[test_idx, 'dissolve_id'] == -1) and (main_gdf.loc[neighbour_idx, 'dissolve_id'] == -1):
                                        main_gdf.loc[test_idx, 'dissolve_id'] = dissolve_n
                                        main_gdf.loc[neighbour_idx, 'dissolve_id'] = dissolve_n
                                        dissolve_n += 1

                                    elif main_gdf.loc[test_idx, 'dissolve_id'] != -1:
                                        main_gdf.loc[neighbour_idx, 'dissolve_id'] = main_gdf.loc[test_idx, 'dissolve_id']

                                    elif main_gdf.loc[neighbour_idx, 'dissolve_id'] != -1:
                                        main_gdf.loc[test_idx, 'dissolve_id'] = main_gdf.loc[neighbour_idx, 'dissolve_id']


                            if verbose:
                                print(f'Polygon id: {test_idx} updated to merge with {neighbour_idx}.' + \
                                      f' Dissolve id: {main_gdf.loc[test_idx, "dissolve_id"]}.' + \
                                      f' Direction: {direction}.'
                                     )
                            
    main_gdf = pd.concat([
        main_gdf.loc[main_gdf.dissolve_id == -1], main_gdf.loc[main_gdf.dissolve_id != -1].dissolve(by='dissolve_id')
    ], axis=0)
                            
    return main_gdf



# a function to extract row and col values from file names and store in attributes
def get_row_col(gdf):
    temp_gdf = deepcopy(gdf)
    temp_gdf['row_val'] = temp_gdf.name.apply(lambda x: x.split('_')[-4])
    temp_gdf['col_val'] = temp_gdf.name.apply(lambda x: x.split('_')[-5])
    #temp_gdf.drop('name', axis=1, inplace=True)
    temp_gdf.head()

    return temp_gdf



# export the merged GDF
def get_filename(my_gdf):
    outfile = my_gdf.name.values[0].split('_')
    _ = outfile.pop(3)
    #_ = outfile.pop(3)
    return '_'.join(outfile).replace('.gpkg', '_Workflow1Merged.gpkg')



# a function to read files with names in the attributes
def read_file_with_name(infile):
    temp_gdf = gpd.read_file(infile).explode(index_parts=False)
    temp_gdf['name'] = os.path.split(infile)[-1]

    return temp_gdf


# for each polygon in the ground truth, find polygon in the test file that has IoU greater than 0.5
def wflow1_iou_threshold_metrics(gt_row, gdf_gt, test_gdf, spatial_index, threshold=0.5):
    
    # match the bounding boxes of ground truth and predicted polygons
    possible_matches_index = list(spatial_index.intersection(gt_row.geometry.bounds))
    possible_matches = test_gdf.iloc[possible_matches_index]
    precise_matches = possible_matches[possible_matches.intersects(gt_row.geometry)]

    if not precise_matches.empty:
        precise_matches_bbox = precise_matches.geometry.apply(lambda x: box(*x.bounds))
        gt_poly_bbox = box(*gt_row.geometry.bounds)

        # Calculate intersection over union
        bbox_intersection_areas = precise_matches_bbox.geometry.apply(lambda x: x.intersection(gt_poly_bbox).area)
        bbox_union_areas = precise_matches_bbox.geometry.apply(lambda x: x.union(gt_poly_bbox).area)
        bbox_iou_values = bbox_intersection_areas / bbox_union_areas

        # if there is at least one polygon in the test layer that has IoU over 0.5
        if sum(bbox_iou_values > threshold) > 0:
            bbox_max_iou_row = bbox_iou_values.loc[bbox_iou_values == bbox_iou_values.max()]
            test_geom = precise_matches.loc[bbox_max_iou_row.index.values[0]]['geometry']
            gt_geom = gdf_gt.loc[gdf_gt['ID_gt'] == gt_row['ID_gt']].squeeze()['geometry']

            gt_row['max_overlap_id'] = bbox_max_iou_row.index.values[0]

            # previous IoU was using bounding box, use actual polygon area instead
            intersection_area = test_geom.intersection(gt_geom).area
            union_area = test_geom.union(gt_geom).area
            gt_row['iou'] = intersection_area / union_area
            gt_row['precision'] = intersection_area / test_geom.area
            gt_row['recall'] = intersection_area / gt_geom.area
            gt_row['f1score'] = (2 * gt_row['precision'] * gt_row['recall']) / (gt_row['precision'] + gt_row['recall'])

    return gt_row


def make_rectangularish(geometry, simplify_tolerance, buffer_distance):
    # Simplify the geometry to remove small variations
    simplified = geometry.simplify(simplify_tolerance, preserve_topology=True)
    
    # Buffer outwards to "square off" the geometry
    squared = simplified.buffer(buffer_distance, join_style=3)
    
    # Buffer inwards to return to approximately the original size
    return squared.buffer(-buffer_distance, join_style=3)


def overlap_resolution_single(gdf):
    gdf = gdf.reset_index()
    gdf['index'] = gdf.index
    spatial_index = gdf.sindex  # Create a spatial index for the GeoDataFrame

    skip_idx = set()
    remove_idx = set()

    for idx, polygon in gdf.geometry.items():
        if idx in skip_idx or idx in remove_idx:
            continue

        # Use spatial index to find possible overlaps
        possible_matches_index = list(spatial_index.intersection(polygon.bounds))
        possible_matches = gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.geometry.intersects(polygon)]

        # Filter out self-match and already processed
        precise_matches = precise_matches[(precise_matches.index != idx) & (~precise_matches.index.isin(skip_idx)) & (~precise_matches.index.isin(remove_idx))]

        if not precise_matches.empty:
            # Calculate intersection and union areas
            intersection_area = precise_matches.geometry.intersection(polygon).area
            union_area = precise_matches.geometry.union(polygon).area
            iou = intersection_area / union_area

            # Find indexes that satisfy the IoU threshold
            iou_satisfied_index = iou[iou > 0.5].index
            iou_not_satisfied_index = iou[iou <= 0.5].index
            
            # if polygons represent more or less the same area, take one of them
            if not iou_satisfied_index.empty:            
                area_sorted_gdf = precise_matches.loc[iou_satisfied_index]
                
                # keep the polygon that has median area
                keep_median_index = area_sorted_gdf.geometry.area.argsort().index[len(area_sorted_gdf) // 2]
                # remove other ones
                remove_indices = list(set(iou_satisfied_index) - set([keep_median_index]))
                
                remove_idx.update(remove_indices)
                skip_idx.add(keep_median_index)
                
       
    # Drop polygons as per remove_idx
    gdf = gdf.drop(index=list(remove_idx))
    
    # do convex hull for the ones that are retained
    skip_idx = list(skip_idx)
    gdf.loc[skip_idx, 'geometry'] = gdf.loc[skip_idx].convex_hull
    
    return gdf.reset_index(drop=True)

def island_resolution(gdf):
    gdf = gdf.reset_index()
    gdf['index'] = gdf.index
    spatial_index = gdf.sindex  # Create a spatial index for the GeoDataFrame

    skip_idx = set()
    remove_idx = set()

    for idx, polygon in gdf.geometry.items():
        if idx in skip_idx or idx in remove_idx:
            continue

        # Use spatial index to find possible overlaps
        possible_matches_index = list(spatial_index.intersection(polygon.bounds))
        possible_matches = gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.geometry.intersects(polygon)]

        # Filter out self-match and already processed
        precise_matches = precise_matches[(precise_matches.index != idx) & (~precise_matches.index.isin(skip_idx)) & (~precise_matches.index.isin(remove_idx))]

        if not precise_matches.empty:
            # Calculate intersection and union areas
            intersection_area = precise_matches.geometry.intersection(polygon).area
            union_area = precise_matches.geometry.union(polygon).area
            iou = intersection_area / union_area

            # Find indexes that satisfy the IoU threshold
            iou_satisfied_index = iou[iou > 0.5].index
            iou_not_satisfied_index = iou[iou <= 0.5].index
            
            # if small ones are within large one, take the largest one only
            if not iou_not_satisfied_index.empty:
                temp_gdf = precise_matches.loc[iou_not_satisfied_index]
                temp_gdf['area'] = temp_gdf.area
                remove_indices = polygon.convex_hull.contains(temp_gdf.geometry).index
                
                if len(remove_indices) > 0:
                    remove_idx.update(remove_indices)
                    skip_idx.add(idx)
       
    # Drop polygons as per remove_idx
    gdf = gdf.drop(index=list(remove_idx))
    
    # do convex hull for the ones that are retained
    skip_idx = list(skip_idx)
    gdf.loc[skip_idx, 'geometry'] = gdf.loc[skip_idx].convex_hull
    
    return gdf.reset_index(drop=True)


# this function is taken from geoplanar and improved to fit current purpose
def trim_overlaps(gdf, largest=True, inplace=False):
    """Trim overlapping polygons with improved error handling and geometry validation."""

    # Validate geometries before processing
    gdf['geometry'] = gdf['geometry'].apply(make_valid)

    if not inplace:
        gdf = gdf.copy()

    geom_col_idx = gdf.columns.get_loc(gdf.geometry.name)

    # Select the appropriate query method based on the version or availability
    if 'query' in dir(gdf.sindex):
        intersections = gdf.sindex.query(gdf.geometry, predicate="intersects").T
    else:
        intersections = gdf.sindex.query_bulk(gdf.geometry, predicate="intersects").T

    def clean_difference(geom1, geom2):
        """Perform a robust difference operation with geometry cleaning."""
        try:
            result = geom1.difference(geom2)
            if result.is_empty:
                return None
            return make_valid(result)
        except Exception:
            # Try buffering by zero as a last resort to clean the geometry
            result = geom1.buffer(0).difference(geom2.buffer(0))
            if result.is_empty:
                return None
            return make_valid(result)

    if largest is None:  # Don't care which polygon to trim
        for i, j in intersections:
            if i != j and gdf.geometry.iloc[j] is not None:
                diff_result = clean_difference(gdf.geometry.iloc[j], gdf.geometry.iloc[i])
                if diff_result:
                    gdf.iloc[j, geom_col_idx] = diff_result
    elif largest:
        for i, j in intersections:
            if i != j and gdf.geometry.iloc[i] is not None and gdf.geometry.iloc[j] is not None:
                if gdf.geometry.iloc[i].area < gdf.geometry.iloc[j].area:
                    diff_result = clean_difference(gdf.geometry.iloc[j], gdf.geometry.iloc[i])
                    if diff_result:
                        gdf.iloc[j, geom_col_idx] = diff_result
                else:
                    diff_result = clean_difference(gdf.geometry.iloc[i], gdf.geometry.iloc[j])
                    if diff_result:
                        gdf.iloc[i, geom_col_idx] = diff_result
    else:
        for i, j in intersections:
            if i != j and gdf.geometry.iloc[i] is not None and gdf.geometry.iloc[j] is not None:
                if gdf.geometry.iloc[i].area > gdf.geometry.iloc[j].area:
                    diff_result = clean_difference(gdf.geometry.iloc[j], gdf.geometry.iloc[i])
                    if diff_result:
                        gdf.iloc[j, geom_col_idx] = diff_result
                else:
                    diff_result = clean_difference(gdf.geometry.iloc[i], gdf.geometry.iloc[j])
                    if diff_result:
                        gdf.iloc[i, geom_col_idx] = diff_result

    # Filter out any None geometries that may have been created
    gdf = gdf[gdf.geometry.notnull()]

    # Handle MultiPolygons: Optionally, explode them if needed
    gdf = gdf.explode(index_parts=True).reset_index(drop=True)

    return gdf

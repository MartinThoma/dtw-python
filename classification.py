#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from math import sqrt, exp

CLASSIFIER_NAME = "dtw-python"

import logging
logging.basicConfig(filename='classificationpy.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


def get_bounding_box(pointlist):
    """ Get the bounding box of a pointlist.

    >>> get_bounding_box([{'x': 0, 'y': 0}, {'x': 1, 'y': 1}])
    {'minx': 0, 'miny': 0, 'maxx': 1, 'maxy': 1}
    """
    minx = pointlist[0]["x"]
    maxx = pointlist[0]["x"]
    miny = pointlist[0]["y"]
    maxy = pointlist[0]["y"]
    for p in pointlist:
        if p["x"] < minx:
            minx = p["x"]
        if p["x"] > maxx:
            maxx = p["x"]
        if p["y"] < miny:
            miny = p["y"]
        if p["y"] > maxy:
            maxy = p["y"]
    return {"minx": minx, "maxx": maxx, "miny": miny, "maxy": maxy}


def scale_and_center(pointlist, center=False):
    """ Take a list of points and scale and move it so that it's in the unit
        square. Keep the aspect ratio. Optionally center the points inside of
        the unit square.

        >>> scale_and_center([{'x': 0, 'y': 0}, {'x': 10, 'y': 10}])
        [{'y': 0.0, 'x': 0.0}, {'y': 1.0, 'x': 1.0}]
    """
    a = get_bounding_box(pointlist)

    width = a['maxx'] - a['minx']
    height = a['maxy'] - a['miny']

    factorX = 1
    factorY = 1
    if width != 0:
        factorX = 1./width

    if height != 0:
        factorY = 1./height

    factor = min(factorX, factorY)
    addx = 0
    addy = 0

    if center:
        add = (1 - (max(factorX, factorY) / factor)) / 2

        if factor == factorX:
            addy = add
        else:
            addx = add

    for key, p in enumerate(pointlist):
        pointlist[key] = {"x": (p["x"] - a['minx']) * factor + addx,
                          "y": (p["y"] - a['miny']) * factor + addy}

    return pointlist


def distance(p1, p2):
    """ Calculate the squared eucliden distance of two points.
    @param  associative array $p1 first point
    @param  associative array $p2 second point
    @return float

    >>> distance({'x': 0, 'y': 0}, {'x': 10, 'y': 5})
    125
    """
    dx = p1["x"] - p2["x"]
    dy = p1["y"] - p2["y"]
    return dx*dx + dy*dy


def maximum_dtw(var):
    return (var['dtw'] < 20)


def greedyMatchingDTW(A, B):
    """ Calculate the distance of A and B by greedy dynamic time warping.
    @param  list A list of points
    @param  list B list of points
    @return float  Minimal distance you have to move points from A to get B

    >>> greedyMatchingDTW([{'x': 0, 'y': 0}, {'x': 1, 'y': 1}], \
                          [{'x': 0, 'y': 0}, {'x': 0, 'y': 2}])
    2
    """
    global logging
    if len(A) == 0:
        logging.warning("A was empty. B:")
        logging.warning(A)
        logging.warning("B:")
        logging.warning(B)
        return 0
    if len(B) == 0:
        logging.warning("B was empty. A:")
        logging.warning(A)
        logging.warning("B:")
        logging.warning(B)
        return 0

    a = A.pop(0)
    b = B.pop(0)
    d = distance(a, b)
    asV = A.pop(0)
    bsV = B.pop(0)
    while (len(A) > 0 and len(B)):
        l = distance(asV, b)
        m = distance(asV, bsV)
        r = distance(a, bsV)
        mu = min(l, m, r)
        d = d + mu
        if (l == mu):
            a = asV
            asV = A.pop(0)
        elif (r == mu):
            b = bsV
            bsV = B.pop(0)
        else:
            a = asV
            b = bsV
            asV = A.pop(0)
            bsV = B.pop(0)
    if (len(A) == 0):
        for p in B:
            d = d + distance(asV, p)
    elif (len(B) == 0):
        for p in A:
            d = d + distance(bsV, p)
    return d


def LotrechterAbstand(p1, p2, p3):
    """
     * Calculate the distance from $p3 to the line defined by $p1 and $p2.
     * @param array $p1 associative array with "x" and "y" (start of line)
     * @param array $p2 associative array with "x" and "y" (end of line)
     * @param array $p3 associative array with "x" and "y" (point)
    """
    x3 = p3['x']
    y3 = p3['y']

    px = p2['x']-p1['x']
    py = p2['y']-p1['y']

    something = px*px + py*py
    if (something == 0):
        # TODO: really?
        return 0

    u = ((x3 - p1['x']) * px + (y3 - p1['y']) * py) / something

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = p1['x'] + u * px
    y = p1['y'] + u * py

    dx = x - x3
    dy = y - y3

    # Note: If the actual distance does not matter,
    # if you only want to compare what this function
    # returns to other results of this function, you
    # can just return the squared distance instead
    # (i.e. remove the sqrt) to gain a little performance

    dist = sqrt(dx*dx + dy*dy)
    return dist


def DouglasPeucker(PointList, epsilon):
    # Finde den Punkt mit dem größten Abstand
    dmax = 0
    index = 0
    for i in range(1, len(Pointlist)):
        d = LotrechterAbstand(PointList[0], PointList[-1], PointList[i])
        if d > dmax:
            index = i
            dmax = d

    # Wenn die maximale Entfernung größer als Epsilon ist, dann rekursiv
    # vereinfachen
    if dmax >= epsilon:
            # Recursive call
            recResults1 = DouglasPeucker(PointList[0:index], epsilon)
            recResults2 = DouglasPeucker(PointList[index:], epsilon)

            # Ergebnisliste aufbauen
            ResultList = recResults1[:-1] + recResults2
    else:
            ResultList = [PointList[0], PointList[-1]]

    # Ergebnis zurückgeben
    return ResultList


def apply_douglas_peucker(pointlist, epsilon):
    """
     Apply the Douglas-Peucker algorithm to each line of $pointlist seperately.
     @param  array $pointlist see pointList()
     @return pointlist
    """
    for i in range(0, len(pointlist)):
        pointlist[i] = DouglasPeucker(pointlist[i], epsilon)
    return pointlist


def get_path(data, epsilon=0):
    path = ""
    data = pointLineList(data)
    if not (type(data) is list):
        print("This was not an array!")  # TODO debug message
        var_dump(data)
        return False

    if epsilon > 0:
        data = apply_douglas_peucker(data, epsilon)

    for line in data:
        for i, point in enumerate(line):
            if i == 0:
                path += " M " + point['x'] + " " + point['y']
            else:
                path += " L " + point['x'] + " " + point['y']

    return path


def pointLineList(linelistP):
    global logging
    linelist = json.loads(linelistP)
    pointlist = []
    for line in linelist:
        l = []
        for p in line:
            l.append({"x": p['x'], "y": p['y']})
        pointlist.append(l)

    if len(pointlist) == 0:
        logging.waring("Pointlist was empty. Search for '" +
                       linelistP + "' in `wm_raw_draw_data`.")
    return pointlist


def pointList(linelistP):
    linelist = json_decode(linelistP)  # TODO
    pointlist = []
    for line in linelist:
        for p in line:
            pointlist.append({"x": p['x'], "y": p['y']})

    if (len(pointlist) == 0):
        logging.warning("Pointlist was empty. Search for '" +
                        linelistP + "' in `wm_raw_draw_data`.")

    return pointlist


def list_of_pointlists2pointlist(data):
    result = []
    for line in data:
        result += line
    return result


def get_dimensions(pointlist):
    a = get_bounding_box(pointlist) # TODO
    return {"width": a['maxx'] - a['minx'], "height": a['maxy'] - a['miny']}


def get_probability_from_distance(results):
    # check if one distance is 0 and meanwhile build sum of distances.
    sum = 0.0
    modified = []
    for formula_id, dtw in results.items():
        if dtw == 0:
            return {formula_id: 1}
        else:
            modified[formula_id] = exp(-dtw)
            sum += modified[formula_id]

    results = modified

    probabilities = []
    for formula_id, p in results.items():
        probabilities.append({formula_id: p / sum})
    return probabilities


def classify(datasets, A, epsilon=0):
    """
    Classify A with data from datasets and smoothing of epsilon.
    @param  list datasets array(
                                 array('data' => ...,
                                       'accepted_formula_id' => ...,
                                       'id' => ...,
                                       'formula_in_latex' => ...,
                                      )
                             )
    @param  array $A        List of points
    @return array           List of possible classifications, ordered DESC by
                                likelines
    """
    results = []

    for key, dataset in enumerate(datasets):
        B = dataset['data']
        if (epsilon > 0):
            B = apply_douglas_peucker(pointLineList(B), epsilon)
        else:
            B = pointLineList(B)
        B = scale_and_center(list_of_pointlists2pointlist(B))
        results.append({"dtw": greedyMatchingDTW(A, B),
                        "latex": dataset['accepted_formula_id'],
                        "id": dataset['id'],
                        "latex": dataset['formula_in_latex'],
                        "formula_id": dataset['formula_id']})

    results = sorted(results, key=lambda k: k['dtw'])
    results = filter(maximum_dtw, results)

    # get only best match for each single symbol
    results2 = []
    for key, row in enumerate(results):
        if row['formula_id'] in results2:
            results2[row['formula_id']] = min(results2[row['formula_id']],
                                              row['dtw'])
            continue
        else:
            results2[row['formula_id']] = row['dtw']

    results = results2
    results = results[:10]

    results = get_probability_from_distance(results)
    return results

if __name__ == "__main__":
    import doctest
    doctest.testmod()

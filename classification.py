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
    >>> get_bounding_box([{'x': 12, 'y': 10}, {'x': 1, 'y': 1}])
    {'minx': 1, 'miny': 1, 'maxx': 12, 'maxy': 10}
    """
    minx = pointlist[0]["x"]
    maxx = pointlist[0]["x"]
    miny = pointlist[0]["y"]
    maxy = pointlist[0]["y"]
    for p in pointlist:
        if p["x"] < minx:
            minx = p["x"]
        elif p["x"] > maxx:
            maxx = p["x"]
        if p["y"] < miny:
            miny = p["y"]
        elif p["y"] > maxy:
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


def distance(p1, p2, squared=False):
    """ Calculate the squared eucliden distance of two points.
    @param  associative array $p1 first point
    @param  associative array $p2 second point
    @return float

    >>> distance({'x': 0, 'y': 0}, {'x': 3, 'y': 4})
    5.0
    >>> '%.2f' % distance({'x': 0, 'y': 0}, {'x': 1, 'y': 22})
    '22.02'
    """
    dx = p1["x"] - p2["x"]
    dy = p1["y"] - p2["y"]
    if squared:
        return (dx*dx + dy*dy)
    else:
        return sqrt(dx*dx + dy*dy)


def dtw(A, B, simple=True):
    """ Calculate the distance of A and B by greedy dynamic time warping.
    @param  list A list of points
    @param  list B list of points
    @return float  Minimal distance you have to move points from A to get B

    >>> '%.2f' % dtw([{'x': 0, 'y': 0}, {'x': 1, 'y': 1}], \
                          [{'x': 0, 'y': 0}, {'x': 0, 'y': 5}], False)
    '4.12'
    >>> '%.2f' % dtw([{'x': 0, 'y': 0}, {'x':0, 'y': 10}, \
                                    {'x': 1, 'y': 22}, {'x': 2, 'y': 2}], \
                          [{'x': 0, 'y': 0}, {'x': 0, 'y': 5}], False)
    '25.63'
    >>> '%.2f' % dtw( [{'x': 0, 'y': 0}, {'x': 0, 'y': 5}], \
                                    [{'x': 0, 'y': 0}, {'x':0, 'y': 10}, \
                                    {'x': 1, 'y': 22}, {'x': 2, 'y': 2}], \
                      False)
    '25.63'
    """
    global logging
    if len(A) == 0:
        logging.warning("A was empty. B:")
        logging.warning(A)
        logging.warning("B:")
        #logging.warning(B)
        throw
        return 0
    if len(B) == 0:
        logging.warning("B was empty. A:")
        #logging.warning(A)
        logging.warning("B:")
        #logging.warning(B)
        return 0
    from Dtw import Dtw
    a = Dtw(A[:], B, lambda a, b: distance(a, b, True))

    return a.calculate(simple)


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


def douglas_peucker(pointlist, epsilon):
    """
     Apply the Douglas-Peucker algorithm to each line of $pointlist seperately.
     @param  array $pointlist see pointList()
     @return pointlist
    """
    for i in range(0, len(pointlist)):
        pointlist[i] = DouglasPeucker(pointlist[i], epsilon)
    return pointlist


def pointLineList(linelistP):
    """Get a list of lists of tuples from a JSON string.
       Those lists represent lines with control points.
    >>> pointLineList('[[{"x":606,"y":411,"time":33}, {"x":605,"y":411,"time":35}, {"x":605,"y":412,"time":39}]]')
    [[{u'y': 411, u'x': 606, u'time': 33}, {u'y': 411, u'x': 605, u'time': 35}, {u'y': 412, u'x': 605, u'time': 39}]]
    """
    global logging
    linelist = json.loads(linelistP)

    if len(linelist) == 0:
        logging.waring("Pointlist was empty. Search for '" +
                       linelistP + "' in `wm_raw_draw_data`.")
    return linelist


def list_of_pointlists2pointlist(data):
    result = []
    for line in data:
        result += line
    return result


def get_dimensions(pointlist):
    a = get_bounding_box(pointlist)
    return {"width": a['maxx'] - a['minx'], "height": a['maxy'] - a['miny']}


def get_probability_from_distance(results):
    """ Get a list of results with dtw and formula id and return a dict mapping
        formula-ids to probabilities.

    >>> get_probability_from_distance([{'dtw': 5.638895307327028, 'formula_id': 33L}, {'dtw': 0.30368392840347985, 'formula_id': 31L}])
    [{'p': 0.9952042189554645, 'formula_id': 31L}, {'p': 0.0047957810445354, 'formula_id': 33L}]
    """
    # check if one distance is 0 and meanwhile build sum of distances.
    summe = 0.0
    modified = {}
    for result in results:
        formula_id = result['formula_id']
        dtw = result['dtw']
        if dtw == 0:
            logging.warning("Probability of 1!: %s" % str(formula_id))
            logging.warning(results)
            return [{'formula_id': formula_id, 'p': 1}]
        else:
            modified[formula_id] = exp(-dtw)
            summe += modified[formula_id]

    results = modified

    probabilities = []
    for formula_id, p in results.items():
        probabilities.append({'formula_id': formula_id, 'p': p / summe})
    return sorted(probabilities, key=lambda k: k['p'], reverse=True)


def classify(datasets, A, epsilon=0):
    """
    Classify A with data from datasets and smoothing of epsilon.
    @param  list datasets [
                            {'data' => ...,
                             'accepted_formula_id' => ...,
                             'id' => ...,
                             'formula_in_latex' => ...,
                            }
                          ]
    @param  list A   List of points
    @return list     List of possible classifications, ordered DESC by
                       likelines
    """
    results = []
    for key, dataset in enumerate(datasets):
        B = dataset['data']
        if (epsilon > 0):
            B = douglas_peucker(pointLineList(B), epsilon)
        else:
            B = pointLineList(B)
        # TODO: eventuell sollten hier wirklich alle Linien genommen werden
        B = scale_and_center(list_of_pointlists2pointlist(B[:]))
        results.append({"dtw": dtw(A, B),
                        "latex": dataset['accepted_formula_id'],
                        "id": dataset['id'],
                        "latex": dataset['formula_in_latex'],
                        "formula_id": dataset['formula_id']})

    results = sorted(results, key=lambda k: k['dtw'])
    results = filter(lambda var: var['dtw'] < 20, results)
    # get only best match for each single symbol
    results2 = {}
    for row in results:
        if row['formula_id'] in results2:
            results2[row['formula_id']] = min(results2[row['formula_id']],
                                              row['dtw'])
        else:
            results2[row['formula_id']] = row['dtw']

    results = [{'formula_id': key, 'dtw': el} for key, el in results2.items()]
    results = sorted(results, key=lambda k: k['dtw'])[:10]

    return get_probability_from_distance(results)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

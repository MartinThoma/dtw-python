#!/usr/bin/env python

import logging
import MySQLdb
import MySQLdb.cursors
from classification import *
from dbconfig import mysql
import time
import datetime


def crossvalidation():
    # Parameters for self-testing
    MIN_OCCURENCES = 10
    K_FOLD = 10
    EPSILON = 0
    CENTER = False

    # Prepare crossvalidation data set
    crossvalidation = [[], [], [], [], [], [], [], [], [], []]

    sql = "SELECT id, formula_in_latex FROM `wm_formula`"
    cursor.execute(sql)
    datasets = cursor.fetchall()

    symbol_counter = 0
    raw_data_counter = 0
    symbols = []

    for dataset in datasets:
        sql = ("SELECT id, data FROM `wm_raw_draw_data` "
               "WHERE `accepted_formula_id` = " + str(dataset['id']))
        cursor.execute(sql)
        raw_datasets = cursor.fetchall()
        if len(raw_datasets) >= MIN_OCCURENCES:
            symbol_counter += 1
            symbols.append(dataset['formula_in_latex'])
            print("%s (%i)" % (dataset['formula_in_latex'], len(raw_datasets)))
            i = 0
            for raw_data in raw_datasets:
                raw_data_counter += 1
                crossvalidation[i].append({'data': raw_data['data'],
                                           'id': raw_data['id'],
                                           'formula_id': dataset['id'],
                                           'accepted_formula_id': dataset['id'],
                                           'formula_in_latex': dataset['formula_in_latex']
                                           })
                i = (i + 1) % K_FOLD

    # Start getting validation results
    classification_accuracy = []
    print("\n\n")
    execution_time = []

    for testset in range(K_FOLD):
        classification_accuracy.append({'correct': 0,
                                        'wrong': 0,
                                        'c10': 0,
                                        'w10': 0})
        for testdata in crossvalidation[testset]:
            start = time.time()
            raw_draw_data = testdata['data']
            if EPSILON > 0:
                result_path = apply_douglas_peucker(pointLineList(raw_draw_data), EPSILON)
            else:
                result_path = pointLineList(raw_draw_data)

            A = scale_and_center(list_of_pointlists2pointlist(result_path),
                                 CENTER)

            # Prepare datasets the algorithm may use
            datasets = []
            for key, value in enumerate(crossvalidation):
                if key == testset:
                    continue
                else:
                    datasets += value

            results = classify(datasets, A, EPSILON)
            end = time.time()
            execution_time.append(end - start)

            answer_id = 0
            if len(results) == 0 or results[0] is null:
                # That should not happen. Threshold of maximum_dtw might be too
                # high.
                print("\nRaw_data_id = %i\n" % testdata['id'])
                answer_id = key(results)
            else:
                answer_id = key(results[0])

            if answer_id == testdata['formula_id']:
                classification_accuracy[testset]['correct'] += 1
            else:
                classification_accuracy[testset]['wrong'] += 1

            if testdata['formula_id'] in results:
                classification_accuracy[testset]['c10'] += 1
            else:
                classification_accuracy[testset]['w10'] += 1

            print("|")

        classification_accuracy[testset]['accuracy'] = (classification_accuracy[testset]['correct'] / (classification_accuracy[testset]['correct'] + classification_accuracy[testset]['wrong']))
        classification_accuracy[testset]['a10'] = classification_accuracy[testset]['c10'] / (classification_accuracy[testset]['c10'] + classification_accuracy[testset]['w10'])
        print(classification_accuracy[testset])
        print("\n")
        print("Average time:")
        print(sum(execution_time)/len(execution_time))

    print(classification_accuracy)

    t1sum = 0
    t10sum = 0

    for testset in range(K_FOLD):
        t1sum += classification_accuracy[testset]['accuracy']
        t10sum += classification_accuracy[testset]['a10']

    print(str(datetime.date.today()) + "\n")
    print("The following %i symbols with %i raw dataset evaluated to\n" % (symbol_counter, raw_data_counter))
    print(", ".join(symbols) + "\n")
    print("Epsilon: " + EPSILON + "\n")
    print("Center: " + CENTER + "\n")
    print("* Top-1-Classification (" + K_FOLD + "-fold cross-validated): " + (t1sum/K_FOLD) + "\n")
    print("* Top-10-Classification (" + K_FOLD + "-fold cross-validated): " + (t10sum/K_FOLD) + "\n")


if __name__ == '__main__':
    logging.basicConfig(filename='selftest.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s')

    logging.info("Started selftest of classifier %s." % CLASSIFIER_NAME)
    logging.info("start establishing connection")
    connection = MySQLdb.connect(host=mysql['host'],
                                 user=mysql['user'],
                                 passwd=mysql['passwd'],
                                 db=mysql['db'],
                                 cursorclass=MySQLdb.cursors.DictCursor)
    cursor = connection.cursor()
    logging.info("end establishing connection")
    crossvalidation()

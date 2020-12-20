import matplotlib.pyplot as plt
import numpy as np

from grading.serialization import load_gradings


def create_statistics():
    # TODO
    gradings = load_gradings()
    # points per task
    testcases = {}
    for submission in gradings.submissions:
        for testsuite in submission.test_suites:
            for testcase in testsuite.test_cases:
                if not testcases.get(testcase.name):
                    testcases[testcase.name] = []
                testcases[testcase.name].append(testcase.points)
    i = 1
    testcases_deviation = []
    for name, points in testcases.items():
        p = np.array(points)
        max_points = test_points_mapping[name]
        x = np.sum((max_points - p) / max_points)
        testcases_deviation.append(x)

    x = np.arange(1, len(testcases_deviation) + 1)
    y = np.array(testcases_deviation)

    x_labels = np.array([k for k in test_points_mapping.keys()])
    fix, ax = plt.subplots(1, 1)
    ax.bar(x, y)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation="vertical")
    # plt.bar(x, y)
    plt.title("1 Fehlerrate")
    plt.show()

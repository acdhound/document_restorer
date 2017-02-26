import cv2
import numpy as np

from document_restorer.edges.detect import EdgeDetectorFactory
from document_restorer.restore.match import VerticalShiftFragmentsConnector
from document_restorer.restore.match import HarrisFragmentsContentMatcher
from document_restorer.restore.sequence import find_sequence

detector = EdgeDetectorFactory().createClosingMorphEdgeDetector(100, 10)
connector = VerticalShiftFragmentsConnector(detector)
content_matcher = HarrisFragmentsContentMatcher()


def match_pieces(piece1, piece2):
    connection = connector.connectFragments(piece1, piece2)
    content_match_result_1 = content_matcher.matchFragmentsContent(connection.stuck_fragments, connection.gap_line)
    return content_match_result_1, connection.adjacency


def save_normalized(mat, name):
    img = np.zeros(mat.shape, np.uint8)
    img = cv2.normalize(mat, img, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
    cv2.imwrite(name, img)

pieces_num = 33
images = []
print 'reading images...'
for n in range(1, pieces_num + 1):
    images.append(cv2.cvtColor(cv2.imread('../resources/img/documents/2/piece{0}.png'.format(n), 1), cv2.COLOR_BGR2GRAY))

print 'matching fragments...'
results_content = np.zeros([len(images), len(images), 1])
results_edges = np.zeros([len(images), len(images), 1])
for i in range(0, len(images)):
    for j in range(0, len(images)):
        # if j == i + 1 or ((i, j) in [(3, 2), (4, 0), (5, 1), (2, 4), (3, 0), (0, 5), (4, 1)]):
        #     content_matcher.write_result_to = 'match_{0}_{1}.png'.format(i + 1, j + 1)
        #     need_print_result = True
        # else:
        #     content_matcher.write_result_to = None
        result = match_pieces(images[i], images[j])
        results_content[i, j] = result[0]
        results_edges[i, j] = result[1]

save_normalized(results_edges, 'edges_results.bmp')
save_normalized(results_content, 'content_results.bmp')

results_edges = cv2.normalize(results_edges, results_edges, 1.00, 0.00)
results_edges = np.full(results_edges.shape, 1.00) - results_edges
results_content = cv2.normalize(results_content, results_content, 1.00, 0.00)
values = results_content * 0.5 + results_edges * 0.5
save_normalized(values, 'values.bmp')

print 'restoring fragments sequence...'
print find_sequence(values)
exit(0)

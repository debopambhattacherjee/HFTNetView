# MIT License
#
# Copyright (c) 2020 Debopam Bhattacherjee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import networkx as nx

EARTH_RADIUS = 6371  # km


def dms2dd(degrees, minutes, seconds, direction):
    """
    Converts latitude/longitude coordinates from degree-minutes-seconds to decimal degrees
    :param degrees: Coordinate degree
    :param minutes: Coordinate minute
    :param seconds: Coordinate second
    :param direction: N/S for latitude and E/W for longitude
    :return: Decimal degrees
    """
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'S' or direction == 'W':
        dd *= -1
    return format(dd, '.5f');


def get_decimal_coordinates(coord):  #
    """
    Converts coordinate strings in a specified format to decimal degrees
    :param coord: Coordinate in format (example): 41-23-06.4 N, 081-19-32.9 W
    :return: Coordinate tuple in degree decimal
    """
    parts = coord.split(",")
    lat_parts = parts[0].strip().split(" ")
    numeric_parts = lat_parts[0].split("-")
    lat_dec = dms2dd(numeric_parts[0], numeric_parts[1], numeric_parts[2], lat_parts[1])
    long_parts = parts[1].strip().split(" ")
    numeric_parts = long_parts[0].split("-")
    long_dec = dms2dd(numeric_parts[0], numeric_parts[1], numeric_parts[2], long_parts[1])
    # print(lat_dec, long_dec)
    return float(lat_dec), float(long_dec)


def compute_length_ground(node1, node2):
    """
    Computes the distance between two nodes
    :param node1: First node
    :param node2: Second node
    :return:  Distance between nodes in km
    """
    x1 = EARTH_RADIUS * math.cos(node1["lat_rad"]) * math.sin(node1["long_rad"])
    y1 = EARTH_RADIUS * math.sin(node1["lat_rad"])
    z1 = EARTH_RADIUS * math.cos(node1["lat_rad"]) * math.cos(node1["long_rad"])
    x2 = EARTH_RADIUS * math.cos(node2["lat_rad"]) * math.sin(node2["long_rad"])
    y2 = EARTH_RADIUS * math.sin(node2["lat_rad"])
    z2 = EARTH_RADIUS * math.cos(node2["lat_rad"]) * math.cos(node2["long_rad"])
    dist = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2) + math.pow((z2 - z1), 2))
    return dist


def generate_undirected_graph(grph):
    """
    Generates undirected graph for the entity
    :param grph: The directed graph
    :return: The undirected graph
    """
    grph2 = nx.Graph()
    for node in grph.nodes(data=True):
        print(node)
        grph2.add_node(node[0],
                       elevation=node[1]['elevation'],
                       lat_deg=node[1]['lat_deg'],
                       long_deg=node[1]['long_deg'],
                       lat_rad=node[1]['lat_rad'],
                       long_rad=node[1]['long_rad'])
    for edge in grph.edges(data=True):
        if grph2.has_edge(edge[0], edge[1]):
            for freq in edge[2]['frequency_list']:
                grph2[edge[0]][edge[1]]['frequency_list'].append(freq)
        else:
            grph2.add_edge(edge[0], edge[1],
                           frequency_list=edge[2]['frequency_list'],
                           length=edge[2]['length'])

    return grph2

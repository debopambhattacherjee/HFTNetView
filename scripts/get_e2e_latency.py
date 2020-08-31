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

"""
Finds end-to-end latencies between data centers in the Chicago - NY corridor
"""

import networkx as nx
import math

try:
    from . import util
except (ImportError, SystemError):
    import util

EARTH_RADIUS = 6371  # km

# Date when you want to get the end-to-end latency; Format: mm_dd_yyyy
SNAPSHOT_DATE = "01_01_2013"

# Output data directory
OUTPUT_DIR = "../output_entity_wise/"

# Output file
OUT_FILE = OUTPUT_DIR + SNAPSHOT_DATE + "_ny4/NY4_dist_stretch_pathcount.txt"

# Data centers DC[0] is CME CyrusOne, DC[1] can be NY4/NYSE/NASDAQ
DC = {}
DC[0] = {
    "lat_deg": 41.7965645,
    "lat_rad": math.radians(41.7965645),
    "long_deg": -88.243012,
    "long_rad": math.radians(-88.243012),
}  # CME



DC[1] = {
    "lat_deg": 40.7772608,
    "lat_rad": math.radians(40.7772608),
    "long_deg": -74.071748,
    "long_rad": math.radians(-74.071748)
}  # NY4

"""
DC[1] = {
    "lat_deg": 41.0783577,
    "lat_rad": math.radians(41.0783577),
    "long_deg": -74.1529141,
    "long_rad": math.radians(-74.1529141)
}  # NYSE
"""
"""
DC[1] = {
    "lat_deg": 40.5843303,
    "lat_rad": math.radians(40.5843303),
    "long_deg": -74.2434266,
    "long_rad": math.radians(-74.2434266)
}  # NASDAQ
"""

# Entities which operate in the Chicago-NJ corridor
ENTITY_NAMES = [
    "AlarmNet, Inc",
    "Transmission Holdings, Inc.",
    "BNSF Railway Co.",
    "COMMONWEALTH EDISON COMPANY",
    "MPX, Inc",
    "Illinois Central Railroad Company",
    "Eastern MLG LLC",
    "Jefferson Microwave, LLC",
    "New Line Networks",
    "Webline Holdings LLC",
    "GTT Americas LLC",
    "EG Broadcast Newco Corp",
    "National Tower Company LLC",
    "Wireless Internetwork, LLC",
    "DC2A LLC",
    "Geodesic Networks LLC",
    "Blueline Comm",
    "Argos Engineering, LLC",
    "xWave Engineering LLC",
    "North Central Tower Co, LLC",
    "NeXXCom Wireless LLC",
    "Fundamental Broadcasting LLC",
    "AQ2AT LLC",
    "World Class Wireless, LLC",
    "Pierce Broadband, LLC",
    "Spectrum Holding Company LLC",
    "SW Networks",
    "iSignal",
    "Newgig networks"
]


def find_inter_DC_min_lat(wr, corr_name):
    """
    Gets shortest path latency between data centers assuming that
    data centers have shortest length fiber connectivity with towers
    within a radius of 50 km
    :param wr: Output writer
    :param corr_name: Entity name
    :return: None; writes output to a file
    """
    nearby_towers = {}
    tower_dists = {}
    for id in DC:
        nearby_towers[id] = []
        tower_dists[id] = []
    for node in G.nodes(data=True):
        G.nodes[node[0]]["lat_rad"] = math.radians(float(node[1]['lat_deg']))
        G.nodes[node[0]]["long_rad"] = math.radians(float(node[1]['long_deg']))
        for id in DC:
            dist = util.compute_length_ground(DC[id], node[1])
            if dist < 50.0:  # towers within a 50 km radius
                nearby_towers[id].append(node)
                tower_dists[id].append(dist)
    G2 = G.to_undirected()
    for dc_id in range(1, len(DC)):
        nearest_tower_dc_0 = None
        nearest_tower_dc_1 = None
        min_aggr_stretch = 99999.0
        min_dist_fiber = 99999.0
        for id1 in range(len(nearby_towers[0])):
            for id2 in range(len(nearby_towers[dc_id])):
                try:
                    path = nx.shortest_path(G2, nearby_towers[0][id1][0], nearby_towers[dc_id][id2][0], weight='length')
                    path_length = nx.shortest_path_length(G2, nearby_towers[0][id1][0], nearby_towers[dc_id][id2][0],
                                                          weight='length')
                    # print(date, path)
                    geo_dist_towers = util.compute_length_ground(nearby_towers[0][id1][1], nearby_towers[dc_id][id2][1])
                    geo_dist_dc = util.compute_length_ground(DC[0], DC[dc_id])
                    stretch = path_length / geo_dist_towers
                    dist_fiber = tower_dists[0][id1] + tower_dists[dc_id][id2]
                    stretch_aggr = ((dist_fiber / 200) + (path_length / 300)) / (geo_dist_dc / 300)
                    if stretch_aggr < min_aggr_stretch:
                        min_aggr_stretch = stretch_aggr
                        nearest_tower_dc_0 = nearby_towers[0][id1]
                        nearest_tower_dc_1 = nearby_towers[dc_id][id2]
                        min_dist_fiber = dist_fiber
                        # print(date, stretch_aggr)
                except:
                    pass
        path = nx.shortest_path(G2, nearest_tower_dc_0[0], nearest_tower_dc_1[0], weight='length')
        path_length = nx.shortest_path_length(G2, nearest_tower_dc_0[0], nearest_tower_dc_1[0], weight='length')
        hop_count = nx.shortest_path_length(G2, nearest_tower_dc_0[0], nearest_tower_dc_1[0])
        simple_path_counter = 0
        geo_dist_towers = util.compute_length_ground(nearest_tower_dc_0[1], nearest_tower_dc_1[1])
        geo_dist_dc = util.compute_length_ground(DC[0], DC[id])
        stretch = path_length / geo_dist_towers
        dist_fiber = min_dist_fiber
        stretch_aggr = ((dist_fiber / 200) + (path_length / 300)) / (geo_dist_dc / 300)

        sel_edges = {}
        for p in nx.shortest_simple_paths(G2, nearest_tower_dc_0[0], nearest_tower_dc_1[0], weight='length'):
            p_len = 0
            for i in range(len(p) - 1):
                p_len += G2[p[i]][p[i + 1]]['length']
            p_stretch = ((dist_fiber / 200) + (p_len / 300)) / (geo_dist_dc / 300)
            #if p_stretch < (1 + 1.1 * (stretch_aggr - 1)):
            if p_stretch < 1.05:
                for i in range(len(p) - 1):
                    sel_edges[p[i], p[i + 1]] = 1
                #print(p_stretch, stretch_aggr)
                simple_path_counter += 1
            else:
                break

        path_diversity_counter = 0
        # print(path)
        for i in range(len(path) - 1):
            # print(path[i], path[i+1])
            try:
                G3 = G2.copy()
                G3.remove_edge(path[i], path[i + 1])
                red_path_length = nx.shortest_path_length(G3, nearest_tower_dc_0[0], nearest_tower_dc_1[0],
                                                          weight='length')
                red_path_stretch = ((dist_fiber / 200) + (red_path_length / 300)) / (geo_dist_dc / 300)
                if red_path_stretch < 1.05:
                    path_diversity_counter += 1
            except:
                pass
        path_diversity = path_diversity_counter / (len(path) - 1)

        writer1 = open(OUTPUT_DIR + corr_name + "/" + SNAPSHOT_DATE + "/link_lengths_red.txt", "w")
        writer2 = open(OUTPUT_DIR + corr_name + "/" + SNAPSHOT_DATE + "/link_freqs_red.txt", "w")
        for k1, k2 in sel_edges:
            writer1.write(str(G2[k1][k2]['length']) + "\n")
            list = G2[k1][k2]['frequency_list']
            for elem in list:
                try:
                    freq = float(elem.replace("'", ""))
                    writer2.write(str(freq) + "\n")
                except:
                    pass
        writer1.close()
        writer2.close()


        link_lens = []
        frequencies = []
        for i in range(0, len(path) - 1):
            link_lens.append(G2[path[i]][path[i + 1]]['length'])
            list = G2[path[i]][path[i + 1]]['frequency_list']
            for elem in list:
                try:
                    freq = float(elem.replace("'", ""))
                    frequencies.append(freq)
                except:
                    pass
        link_lens.sort()
        frequencies.sort()
        median_link_len = link_lens[math.floor(len(link_lens) / 2)]
        median_freq = frequencies[math.floor(len(frequencies) / 2)]

        # if dist_fiber < 10.0:
        print(corr_name, geo_dist_dc, path_length, dist_fiber, stretch, stretch_aggr, simple_path_counter, hop_count)
        wr.write(corr_name
                 + "," + str(geo_dist_dc)
                 + "," + str(path_length)
                 + "," + str(dist_fiber)
                 + "," + str(stretch)
                 + "," + str(stretch_aggr)
                 + "," + str(simple_path_counter)
                 + "," + str(median_link_len)
                 + "," + str(median_freq)
                 + "," + str(path_diversity)
                 + "," + str(hop_count)
                 + "\n")

        writer1 = open(OUTPUT_DIR + corr_name + "/" + SNAPSHOT_DATE + "/link_lengths.txt", "w")
        writer2 = open(OUTPUT_DIR + corr_name + "/" + SNAPSHOT_DATE + "/link_freqs.txt", "w")
        for i in range(0, len(path) - 1):
            writer1.write(str(G2[path[i]][path[i + 1]]['length']) + "\n")
            list = G2[path[i]][path[i + 1]]['frequency_list']
            for elem in list:
                try:
                    freq = float(elem.replace("'", ""))
                    writer2.write(str(freq) + "\n")
                except:
                    pass
        writer1.close()
        writer2.close()


writer = open(OUT_FILE, 'w')

for entity in ENTITY_NAMES:
    corr_name = entity.replace(" ", "_").replace("/", "_").replace(".", "_").replace(",", "_").replace("&", "_")
    IN_FILE_GRAPH = OUTPUT_DIR +corr_name.replace(" ", "_")+"/"+SNAPSHOT_DATE+"/graph_active.yaml"
    try:
        G = nx.read_yaml(IN_FILE_GRAPH)
        find_inter_DC_min_lat(writer, corr_name)
    except:
        pass
writer.close()

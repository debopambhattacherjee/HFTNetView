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
Reconstructs networks on a specific date from licenses which were active on that date
"""

from datetime import datetime
import networkx as nx
import math
import os

try:
    from . import util
except (ImportError, SystemError):
    import util

# Date when you want to reconstruct the network; Format: mm_dd_yyyy
RECONSTRUST_DATE = "01_01_2020"

# Output data directory
OUTPUT_DIR = "../output_entity_wise/"

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

EARTH_RADIUS = 6371  # km

# Input: HTML header and footer files to generate visualizations
topFile = "static_html/top.html"
bottomFile = "static_html/bottom.html"

G = nx.DiGraph()
valid_licenses = []
nodes = {}
nodes_by_id = {}
global_node_counter = 0
edges = {}


def find_valid_license():
    """
    Find licenses which are active
    :return: None; active license appended to valid_licenses
    """
    rec_date = datetime.strptime(RECONSTRUST_DATE, '%m_%d_%Y').date()
    print("Reconstruction date", rec_date)
    lines = [line.rstrip('\n') for line in open(license_file)]
    for i in range(len(lines)):
        parts = lines[i].split(",")
        #3322637,Terminated,10/05/2011,08/30/2013,09/14/2014,10/05/2021
        license_id = parts[0]
        license_status = parts[1]
        grant_date = datetime.strptime(parts[2], '%m/%d/%Y').date()
        #effective_date = datetime.strptime(parts[3], '%m/%d/%Y').date()
        try:
            cancel_date = datetime.strptime(parts[4], '%m/%d/%Y').date()
        except:
            cancel_date = None
        expiry_date = datetime.strptime(parts[5], '%m/%d/%Y').date()
        isLicenseValid = False
        if grant_date <= rec_date and expiry_date > rec_date:
            if cancel_date != None:
                if cancel_date > rec_date:
                    isLicenseValid = True
            else:
                isLicenseValid = True
        #print(license_id, license_status, isLicenseValid, grant_date, cancel_date, expiry_date)
        if isLicenseValid:
            valid_licenses.append(license_id)


def add_to_graph(transmitter, receiver, frequencies):
    """
    Adds tower-tower MW hops to the graph
    :param transmitter: Transmitting tower
    :param receiver: Receiving tower
    :param frequencies: Link operating frequencies
    :return: None; graph G is updated
    """
    global G, nodes, nodes_by_id, global_node_counter, edges
    geo_dist = util.compute_length_ground(transmitter, receiver)
    #print(transmitter, receiver)
    transmitter_id = -1
    receiver_id = -1
    try:
        transmitter_id = nodes[transmitter['lat_deg'], transmitter['long_deg']]
    except:
        nodes[transmitter['lat_deg'], transmitter['long_deg']] = global_node_counter
        nodes_by_id[global_node_counter] = transmitter
        transmitter_id = global_node_counter
        G.add_node(transmitter_id,
                   lat_deg=transmitter['lat_deg'],
                   long_deg=transmitter['long_deg'],
                   elevation=transmitter['elevation'])
        global_node_counter += 1
    try:
        receiver_id = nodes[receiver['lat_deg'], receiver['long_deg']]
    except:
        nodes[receiver['lat_deg'], receiver['long_deg']] = global_node_counter
        nodes_by_id[global_node_counter] = receiver
        receiver_id = global_node_counter
        G.add_node(receiver_id,
                   lat_deg=receiver['lat_deg'],
                   long_deg=receiver['long_deg'],
                   elevation=receiver['elevation'])
        global_node_counter += 1
    # Add/Update edge
    try:
        frequency_list = G[transmitter_id][receiver_id]['frequency_list']
        for f in frequencies:
            frequency_list.append(f)
        G[transmitter_id][receiver_id]['frequency_list'] = frequency_list
    except:
        G.add_edge(transmitter_id, receiver_id, frequency_list=frequencies, length=geo_dist)


def reconstruct_network():
    """
    Reconstructs network on the specific date using licenses active on that date
    :return: None
    """
    lines = [line.rstrip('\n') for line in open(network_file)]
    for lic_id in valid_licenses:
        for i in range(len(lines)):
            parts = lines[i].split(";")
            if parts[0].strip() == lic_id.strip():
                transmitter = {
                    "lat_deg": float(parts[2]),
                    "lat_rad": math.radians(float(parts[2])),
                    "long_deg": float(parts[3]),
                    "long_rad": math.radians(float(parts[3])),
                    "elevation": parts[4]
                }
                receiver = {
                    "lat_deg": float(parts[5]),
                    "lat_rad": math.radians(float(parts[5])),
                    "long_deg": float(parts[6]),
                    "long_rad": math.radians(float(parts[6])),
                    "elevation": parts[7]
                }
                frequencies_text = parts[8].replace("[","").replace("]","").replace(" ","").split(",")
                frequencies = []
                for freq in frequencies_text:
                    frequencies.append(freq)
                #print(transmitter, receiver, frequencies)
                add_to_graph(transmitter, receiver, frequencies)


def visualize_graph(writer):
    """
    Generates HTML file for visualizing the MW network
    :param writer: Writer for the HTML file
    :return: None; the HTML file is generated
    """

    # CME - CyrusOne
    writer.write("createNode( 41.7965645 , -88.243012 , 'orange', 8);\n")

    # CBOE (NY4)
    writer.write("createNode( 40.7772608 , -74.071748 , 'orange', 8);\n")

    # NYSE
    writer.write("createNode( 41.0783577 , -74.1529141 , 'orange', 8);\n")

    # NASDAQ
    writer.write("createNode( 40.5843303 , -74.2434266 , 'orange', 8);\n")

    for node in G.nodes(data=True):
        writer.write("createNode( "
                     + str(node[1]["lat_deg"])
                     + " ,  " + str(node[1]["long_deg"])
                     + " , 'black', 2);\n")

    for edge in G.edges(data=True):
        print(edge)
        writer.write("createEdge( "
                     + str(nodes_by_id[edge[0]]["lat_deg"])
                     + " , " + str(nodes_by_id[edge[0]]["long_deg"])
                     + " , " + str(nodes_by_id[edge[1]]["lat_deg"])
                     + " , " + str(nodes_by_id[edge[1]]["long_deg"])
                     + " , 'red', 1.4);\n")


def visualize():
    """
    Visualizes the MW network by generating HTML file
    :return: None; the HTML file is generated
    """
    writer = open(OUT_FILE_HTML, 'w')
    with open(topFile, 'r') as fi:
        writer.write(fi.read())
    visualize_graph(writer)
    with open(bottomFile, 'r') as fb:
        writer.write(fb.read())
    writer.close()


for entity in ENTITY_NAMES:
    G = nx.DiGraph()
    valid_licenses = []
    nodes = {}
    nodes_by_id = {}
    global_node_counter = 0
    edges = {}

    corr_name = entity.replace(" ", "_").replace("/", "_").replace(".", "_").replace(",", "_").replace("&", "_")

    # Input license and network files
    license_file = OUTPUT_DIR + corr_name + "/2020_04/license_status_dates.txt"
    network_file = OUTPUT_DIR + corr_name + "/2020_04/network.txt"

    directory = OUTPUT_DIR + corr_name + "/" + RECONSTRUST_DATE
    if not os.path.exists(directory):
        os.makedirs(directory)
    OUT_FILE_HTML = OUTPUT_DIR + corr_name + "/" + RECONSTRUST_DATE + "/viz_active.html"
    OUT_FILE_GRAPH = OUTPUT_DIR + corr_name + "/" + RECONSTRUST_DATE + "/graph_active.yaml"

    find_valid_license()
    reconstruct_network()
    visualize()
    nx.write_yaml(G, OUT_FILE_GRAPH)

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
Gets license details for each entity in ENTITY_NAMES by scraping public FCC filing data
"""

import requests
import math
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import networkx as nx
import os

try:
    from . import util
except (ImportError, SystemError):
    import util


# FCC License Search URL
FCC_BASE_URL = "https://wireless2.fcc.gov/UlsApp/UlsSearch/"

# Input: HTML header and footer files to generate visualizations
topFile = "static_html/top.html"
bottomFile = "static_html/bottom.html"

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


def add_to_graph(transmitter, receiver, frequencies):
    """
    Adds tower-tower MW hops to the graph
    :param transmitter: Transmitting tower
    :param receiver: Receiving tower
    :param frequencies: Link operating frequencies
    :return: None; graph G is updated
    """
    global G, nodes, nodes_by_id, global_node_counter, edges
    los_dist = util.compute_length_ground(transmitter, receiver)
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
        G.add_edge(transmitter_id, receiver_id, frequency_list=frequencies, length=los_dist)


def visualize_graph(writer):
    """
    Generates HTML file for visualizing the MW network
    :param writer: Writer for the HTML file
    :return: None; the HTML file is generated
    """
    for node in G.nodes(data=True):
        writer.write("var redSphere = viewer.entities.add({name : '"
                     + str(node[0])
                     + "', position: Cesium.Cartesian3.fromDegrees("
                     + str(node[1]["long_deg"]) + ", "
                     + str(node[1]["lat_deg"]) + ", 0), "
                     + "ellipsoid : {radii : new Cesium.Cartesian3(5000.0, 5000.0, 5000.0), "
                     + "material : Cesium.Color.RED.withAlpha(1),}});\n")

    for edge in G.edges(data=True):
        print(edge)
        writer.write("viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights(["
                     + str(nodes_by_id[edge[0]]["long_deg"]) + ","
                     + str(nodes_by_id[edge[0]]["lat_deg"]) + ",0,"
                     + str(nodes_by_id[edge[1]]["long_deg"]) + ","
                     + str(nodes_by_id[edge[1]]["lat_deg"]) + ",0]), "
                     + "width: 2.0, arcType: Cesium.ArcType.NONE, "
                     + "material: new Cesium.PolylineOutlineMaterialProperty({ "
                     + "color: Cesium.Color.YELLOW.withAlpha(1.0), outlineWidth: 0, outlineColor: Cesium.Color.BLACK})}});\n")


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


def get_license_list():
    """
    Generates license list for an entity
    :return: None; the corresponding file with all licenses is generated
    """
    writer = open(OUT_FILE_LICENSE_LIST, 'w')
    print(FCC_LICENSE_LIST_URL)
    resp = requests.get(FCC_LICENSE_LIST_URL)
    print(resp.text)
    writer.write(str(resp.text))
    writer.close()


def get_license_dates(licDetailURL):
    """
    Get various dates (grant date, expiry date, effective date, cancel date) associated with a license
    :param licDetailURL: License URL
    :return: Dates associated with the license
    """
    resp = requests.get(licDetailURL)
    soup = BeautifulSoup(resp.text, features="lxml")
    keys = soup.find_all('b')
    grant_date = None
    effective_date = None
    cancel_date = None
    exp_date = None
    for key in keys:
        if key.text.find('Dates') != -1:
            grant_key = key.findNext('td').findNext('td')
            grant_date = grant_key.text.strip()
            exp_key = grant_key.findNext('td').findNext('td')
            exp_date = exp_key.text.strip()
            effective_key = exp_key.findNext('td').findNext('td')
            effective_date = effective_key.text.strip()
            cancel_key = effective_key.findNext('td').findNext('td')
            cancel_date = cancel_key.text.strip()
            break
    return grant_date, effective_date, cancel_date, exp_date


def get_path_detail(licenseID, link_txt, status, writer_network):
    """
    Gets tower details and frequency list for individual licenses by parsing scraped data
    :param licenseID: ID of the license
    :param link_txt: Text associated with the license
    :param status: License status
    :param writer_network: Writer for the corresponding output file
    :return: None
    """
    path_url = FCC_BASE_URL + link_txt
    resp = requests.get(path_url)
    soup = BeautifulSoup(resp.text, features="lxml")
    keys = soup.find_all('b')

    transmitter = None
    receiver = None
    frequencies = []
    for key in keys:
        if key.text.find('Transmit')!= -1 and key.text.find('Location')!= -1:
            coordLabelTag = key
            while coordLabelTag.contents[0].find("Coordinates") == -1:
                coordLabelTag = coordLabelTag.findNext('td')
            coordTag = coordLabelTag.findNext('td')
            coord = coordTag.contents[0].strip()
            elevationLabelTag = coordTag
            while elevationLabelTag.contents[0].find("Elevation") == -1:
                elevationLabelTag = elevationLabelTag.findNext('td')
            elevationTag = elevationLabelTag.findNext('td')
            elevation = elevationTag.contents[0].strip()
            # print("Transmitter:", coord, elevation)
            lat_deg, long_deg = util.get_decimal_coordinates(coord)
            transmitter = {
                "lat_deg": lat_deg,
                "lat_rad": math.radians(lat_deg),
                "long_deg": long_deg,
                "long_rad": math.radians(long_deg),
                "elevation": elevation
            }
        if key.text.find('Receiver')!= -1 and key.text.find('Location')!= -1:
            coordLabelTag = key
            while coordLabelTag.contents[0].find("Coordinates") == -1:
                coordLabelTag = coordLabelTag.findNext('td')
            coordTag = coordLabelTag.findNext('td')
            coord = coordTag.contents[0].strip()
            elevationLabelTag = coordTag
            while elevationLabelTag.contents[0].find("Elevation") == -1:
                elevationLabelTag = elevationLabelTag.findNext('td')
            elevationTag = elevationLabelTag.findNext('td')
            elevation = elevationTag.contents[0].strip()
            lat_deg, long_deg = util.get_decimal_coordinates(coord)
            # print("Receiver:", coord, elevation)
            receiver = {
                "lat_deg": lat_deg,
                "lat_rad": math.radians(lat_deg),
                "long_deg": long_deg,
                "long_rad": math.radians(long_deg),
                "elevation": elevation
            }
    tables = soup.findAll("table", {"summary": "Frequencies table"})
    for table in tables:
        rows = table.find_all('tr', recursive=False)
        row_counter = 0
        for row in rows:
            row_counter += 1
            if row_counter >= 3:
                columns = row.find_all('td', recursive=False)
                column_counter = 0
                for column in columns:
                    column_counter += 1
                    if column_counter == 2:
                        frequencies.append(column.contents[0].strip())
    if status == 'Active':
        try:
            add_to_graph(transmitter, receiver, frequencies)
        except:
            pass
    if transmitter != None and receiver != None:
        print(transmitter, receiver, frequencies)
        writer_network.write(str(licenseID)
                 + ";" + str(status)
                 + ";" + str(transmitter['lat_deg'])
                 + ";" + str(transmitter['long_deg'])
                 + ";" + str(transmitter['elevation'])
                 + ";" + str(receiver['lat_deg'])
                 + ";" + str(receiver['long_deg'])
                 + ";" + str(receiver['elevation'])
                 + ";" + str(frequencies) + "\n")
    writer_network.flush()


def get_license_detail(licenseID, status, writer_network):
    """
    Get license details by ID by scraping Web pages
    :param licenseID: ID of the license
    :param status: License status
    :param writer_network: Writer of the corresponding output file
    :return: None
    """
    url = "https://wireless2.fcc.gov/UlsApp/UlsSearch/licensePathsSum.jsp?licKey="+licenseID
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features="lxml")
    for link in soup.findAll('a'):
        link_txt = str(link.get('href'))
        if link_txt.find("licensePathsDetail") != -1:
            try:
                get_path_detail(licenseID, link_txt, status, writer_network)
            except:
                pass


def parse_license_list():
    """
    Parse individual licenses sequentially, scrape data, and generate graph
    :return: None
    """
    writer_status = open(OUT_FILE_LICENSE_STATUS, 'w')
    writer_network = open(OUT_FILE_NETWORK, 'w')
    root = ET.parse(OUT_FILE_LICENSE_LIST).getroot()
    for child1 in root:
        if child1.tag.find('Licenses')!= -1:
            for child2 in child1:
                if child2.tag.find('License')!= -1:
                    status = child2[5].text
                    licenseID = child2[7].text
                    licDetailURL = child2[8].text
                    grant_date, effective_date, cancel_date, exp_date = get_license_dates(licDetailURL)
                    print(status, licenseID, grant_date, effective_date, cancel_date, exp_date)
                    if status != 'Unknown':
                        writer_status.write(str(licenseID)
                                        + "," + str(status)
                                        + "," + str(grant_date)
                                        + "," + str(effective_date)
                                        + "," + str(cancel_date)
                                        + "," + str(exp_date)
                                        + "\n")
                        writer_status.flush()
                        get_license_detail(licenseID, status, writer_network)
    writer_status.close()
    writer_network.close()


for entity in ENTITY_NAMES:
    corr_name = entity.replace(" ", "_").replace("/", "_").replace(".", "_").replace(",", "_").replace("&", "_")
    os.makedirs(OUTPUT_DIR + corr_name +"/2020_04")
    G = nx.DiGraph()
    nodes = {}
    nodes_by_id = {}
    global_node_counter = 0
    edges = {}
    FCC_LICENSE_LIST_URL = "https://data.fcc.gov/api/license-view/basicSearch/getLicenses?searchValue="+entity
    OUT_FILE_LICENSE_LIST = OUTPUT_DIR + corr_name +"/2020_04/license_list.xml"
    OUT_FILE_LICENSE_STATUS = OUTPUT_DIR + corr_name +"/2020_04/license_status_dates.txt"
    OUT_FILE_HTML = OUTPUT_DIR + corr_name +"/2020_04/viz_active.html"
    OUT_FILE_NETWORK = OUTPUT_DIR + corr_name +"/2020_04/network.txt"
    OUT_FILE_GRAPH = OUTPUT_DIR + corr_name +"/2020_04/graph_active.yaml"

    get_license_list()
    parse_license_list()
    visualize()
    nx.write_yaml(G, OUT_FILE_GRAPH)

HFTNetView
==========
[![GitHub license](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://raw.githubusercontent.com/Carthage/Carthage/master/LICENSE.md)

A python-based scraping and visualization tool for uncovering **High Frequency Trading (HFT)** networks, consisting of point-to-point line-of-sight microwave (MW) links, operating in the **Chicago - New Jersey** trading corridor.

Our data scraping tool gets the list of all licenses for each company operating in the corridor from **FCC**'s license search Web pages, and for each license ID collects the following information by scraping the license details Web page:
*   **License grant date**: Date when a license was formally granted by the FCC.
*   **License cancellation date**: Date when a license was cancelled by either the licensor or licensee.
*   **License termination date**: Date when a license is terminated, if it is not cancelled or extended before that date.
*   **Tower end-points**: Coordinates and altitude of the towers involved. Typically, each license has a central transmitting end-point, and one or more receiving end-points.
*   **Operating frequencies**: A transmitter can use a list of frequencies to communicate with each receiver.

Based on the collected information, the tool can generate (YAML) and visualize (HTML) HFT networks for any arbitrary date in the past. We use Python `networkx` to reconstruct the network graphs and compute shortest paths, and `Google Maps API` to visualize them.

## Installation

HFTNetView has the following dependencies: `requests`, `bs4`, and `networkx`.

To generate visualizations, one needs a [Google Maps API Key](https://developers.google.com/maps/documentation/javascript/get-api-key).
The key should replace <YOUR_KEY_HERE> in file [bottom.html](https://github.com/debopambhattacherjee/HFTNetView/blob/master/scripts/static_html/bottom.html)

## Directory structure

* **output_entity_wise**: This directory contains data collected in April, 2020, and the corresponding YAML human-readable HFT network graphs.
* **visualizations**: This directory contains the PNG images of network visualizations for 01-Jan-2016 and 01-Apr-2020. The scripts generate HTML visualizations while the repository contains PNG images in order to avoid sharing the Google Maps API key.
* **scripts**: This directory contains the scripts needed to scrape FCC license data, and generate and visualize HFT networks.

## Generated networks

**output_entity_wise** directory contains the collected data and generated networks in YAML format.
For each entity operating HFT networks in the Chicago - New Jersey corridor, as of April 2020, the directory contains the following files:
* **2020_04/license_list.xml**: This file contains list of all FCC licenses for the entity, as of April 2020.
* **2020_04/license_status_dates.txt**: This file contains license dates for all licenses as in the above file. The format is:
```
License ID, Status, Grant date, Effective date, Cancel date, Expiry date
```
* **2020_04/network.txt**: This file contains individual link details in a simple text format. It does not represent the network on a specific date, but rather contains all MW links that have been part of the network at some point. The file format is:
```
License ID, Status, Tower1 Latitude, Tower1 Longitude, Tower1 Elevation, Tower2 Latitude, Tower2 Longitude, Tower2 Elevation, List of operating frequencies
```
* **mm_dd_yyyy/graph_active.yaml**: For arbitrary dates in the past (mm_dd_yyyy), this file contains graphs corresponding to the HFT networks in human-readable form.
```
Node (tower) properties: Latitude, Longitude, Elevation
Edge (MW link) properties: Length (km), Operating frequencies
```

## Generated visualizations

**visualizations** directory contains network visualizations for 2 dates: 01-Jan-2016 and 01-Apr-2020.

Visualization of **New Line Networks**' HFT network as of 01-Apr-2020
![NLN network, 01-Apr-2020](https://raw.githubusercontent.com/debopambhattacherjee/HFTNetView/master/visualizations/New_Line_Networks/04_01_2020/viz_active_links.png)

Visualization of **Jefferson Microwave**'s HFT network as of 01-Apr-2020
![JM network, 01-Apr-2020](https://raw.githubusercontent.com/debopambhattacherjee/HFTNetView/master/visualizations/Jefferson_Microwave__LLC/04_01_2020/viz_active_links.png)

## Scripts

**scripts** directory contains all the scripts, as follows:

* **generate_license_history.py**: Gets license details for each entity in ENTITY_NAMES by scraping public FCC filing data.
* **get_e2e_latency.py**: Finds end-to-end latencies between data centers in the Chicago - NJ corridor.
* **get_e2e_latency_temporal.py**: Finds end-to-end latencies between data centers in the Chicago - NJ corridor
over all networks for list of dates.
* **reconstruct_by_date.py**: Reconstructs networks on a specific date from licenses which were active on that date.
* **util.py**: Contains few utility functions.
* **static_html**: This directory holds the static html files needed to generate the HTML visualizations. As mentioned above, bottom.html should be updated with the Google Maps API key.

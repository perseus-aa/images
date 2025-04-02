"""
Generate rdf linking artifacts to thumbnails

"""

from pathlib import Path
import json
from rdflib import Graph, Namespace, Literal


# Namespaces
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
AA = Namespace("http://perseus.tufts.edu/ns/aa/")
IMAGE = Namespace("https://iiif.perseus.tufts.edu/iiif/3/")
SCHEMA = Namespace("https://schema.org/")

AA_NAMESPACES = {
    "crm" : CRM,
    "aa" : AA,
    "image" : IMAGE
    }



def artifact_index(map_file):
    with open(map_file, 'r') as f:
       index = json.load(f)
    return index


def base_graph() -> Graph:
    graph:Graph = Graph()
    [graph.bind(k,v) for k,v in AA_NAMESPACES.items()]
    return graph


def thumbnail_url(image):
    url = str(image)
    return Literal(f"{url}/full/max/0/default.jpg")
    

def graph_map(index:dict) -> Graph:
    """Generate a graph of images and artifacts.

    The function takes an index {artifactid : [imgid], a2: [im2] ...}
    and adds relating statements to the graph.
    """

    g:Graph = base_graph()
    for artifact_id, image_ids in index.items():
        if artifact_id and image_ids:
            artifact = AA[artifact_id]
            # take first image arbitrarily
            g.add((artifact, SCHEMA['thumbnail'], thumbnail_url(IMAGE[image_ids[0]])))
                
    return g

if __name__ == "__main__":
    afiles = ['building_map.json', 'coin_map.json', 'gem_map.json', 'sculpture_map.json', 'site_map.json', 'vase_map.json']
    jsondir = Path('/Users/wulfmanc/repos/gh/perseus-aa/json/indexes')
    rdfdir = Path('/Users/wulfmanc/repos/gh/perseus-aa/rdf')

    for jsonfile in afiles:
        a_map = artifact_index(jsondir / Path(jsonfile))
        g = graph_map(a_map)
        print(f"saving thumbs for {jsonfile}")
        outfile = rdfdir / Path(f"{jsonfile}_thumbs").with_suffix('.ttl')
        g.serialize(outfile)

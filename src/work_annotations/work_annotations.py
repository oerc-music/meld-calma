# create RDF (turtle) files in folder 'annotations', one file per artist. 
# Files include one Work per song, and one Annotation per respective etree Track


from rdflib import Graph, URIRef, RDF, RDFS, Namespace, Literal, BNode
from artistgraph import getArtistGraph
import sys, os
from uuid import uuid4
from SPARQLWrapper import SPARQLWrapper, JSON
from multiprocessing import Pool
from slugify import slugify
import pickle, bz2

mc_uri = 'http://example.com/meldedcalma/'
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
mo = Namespace('http://purl.org/ontology/mo/')
oa = Namespace('http://www.w3.org/ns/oa#')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
mc = Namespace(mc_uri)

def queryArtistNames():
    artist_query = '''
            PREFIX etree: <http://etree.linkedmusic.org/vocab/>
            PREFIX mo: <http://purl.org/ontology/mo/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT ?artist_name {{
            ?s a mo:MusicArtist ;
                skos:prefLabel ?artist_name . }}'''
    sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(artist_query)
    artists = []
    for res in sparql.query().convert()["results"]["bindings"]:
        artists.append(res['artist_name']['value'])
    return artists


def add2graph3(g, artist):
    # one Annotation per track
    if len(artist.songs) == 0:
        return
    for song in artist.songs:
        work_uri = URIRef(mc_uri + 'work_' + str(uuid4()))
        g.add((work_uri, RDF.type, mo.MusicalWork))
        g.add((work_uri, RDFS.label, Literal(song)))
        agent = BNode()
        g.add((work_uri, mo.artist, agent))
        g.add((agent, foaf.name, Literal(artist.name)))
        for target in artist.songs[song]:
            annotation_uri = URIRef(mc_uri + 'annotation_' + str(uuid4()))
            g.add((annotation_uri, RDF.type, oa.Annotation))
            g.add((annotation_uri, oa.hasTarget, work_uri))
            g.add((annotation_uri, oa.hasBody, URIRef(target)))
    serializeArtist(g, artist.name)

'''
def add2graph2(g, artist):
    # one Annotation per work
    if len(artist.songs) == 0:
        return
    for song in artist.songs:
        work_uri = URIRef(mc_uri + 'work_' + str(uuid4()))
        g.add((work_uri, RDF.type, mo.MusicalWork))
        g.add((work_uri, RDFS.label, Literal(song)))
        agent = BNode()
        g.add((work_uri, mo.artist, agent))
        g.add((agent, foaf.name, Literal(artist.name)))
        annotation_uri = URIRef(mc_uri + 'annotation_' + str(uuid4()))
        g.add((annotation_uri, RDF.type, oa.Annotation))
        g.add((annotation_uri, oa.hasTarget, work_uri))
        for target in artist.songs[song]:
            g.add((annotation_uri, oa.hasBody, URIRef(target)))
    serializeArtist(g, artist.name)
'''

def initGraph():
    g = Graph()
    g.bind('mo', 'http://purl.org/ontology/mo/')
    g.bind('oa', 'http://www.w3.org/ns/oa#')
    g.bind('mc', 'http://example.com/meldedcalma/')
    g.bind('skos', 'http://www.w3.org/2004/02/skos/core#')
    g.bind('foaf', 'http://xmlns.com/foaf/0.1/')
    return g

def serializeArtist(g, artname):
    fname = 'annotations/' + slugify(artname) + '.ttl'
    print(fname)
    g.serialize(fname, format='turtle')


def makeTurtle(artname):
    if artname == '': artname = 'unknown'
    artist = getArtistGraph(artname)
    g = initGraph()
    add2graph3(g, artist)
    

def main(multi=True):
    if not os.path.exists('annotations'):
        os.makedirs('annotations')
    print('querying artists')
    artists = sorted(queryArtistNames())
    if multi == True:
        pool = Pool()
        pool.map(makeTurtle, artists, chunksize=1)
        pool.close()
        pool.join()
    elif multi == False:
        for a in artists:
            makeTurtle(a)

main(multi=False)


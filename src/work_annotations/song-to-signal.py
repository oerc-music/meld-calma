from rdflib import Graph, URIRef, RDF, RDFS, Namespace, Literal, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import requests, os, sys
from urllib.parse import urljoin
from uuid import uuid4

CONTAINER = "https://localhost:8443/public/"
if (os.environ["CONTAINER"]): CONTAINER = os.environ["CONTAINER"]
SPARQL = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
SPARQL.setReturnFormat(JSON)
MC = Namespace('http://example.com/meldedcalma/')
OA = Namespace('http://www.w3.org/ns/oa#')


def getRequestHeaders(slug, link='<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'):
    return { "Content-Type": "text/turtle",
             "Link": link,
             "Slug": slug.replace(' ', '_') }


def UuidUri(s):
    return s + '_' + str(uuid4()).replace('-','')


def getArtistId(artist_name):
    q = '''SELECT ?artistId {{ ?artistId foaf:name "{0}" . }}'''.format(artist_name)
    SPARQL.setQuery(q)
    return SPARQL.query().convert()["results"]["bindings"][0]['artistId']['value']


def getEtreeTracks(artist_id, song_name):
    q = ''' PREFIX mo: <http://purl.org/ontology/mo/>
            PREFIX calma: <http://calma.linkedmusic.org/vocab/>
            SELECT ?trackId ?calmaId {{ 
            ?trackId mo:performer <{0}> ;
                skos:prefLabel "{1}" ;
                calma:data ?calmaId }}'''.format(artist_id, song_name)
    SPARQL.setQuery(q)
    track_ids = []
    for res in SPARQL.query().convert()["results"]["bindings"]:
        track_ids.append((res['trackId']['value'], res['calmaId']['value']))
    return track_ids


def createArtistLDP(artist_name):
    req_headers = getRequestHeaders(slug=artist_name)
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    loc = r.headers["Location"]
    print("Artist add:", loc)
    return loc


def createSongLDP(artist_name, song_name):
    loc = createArtistLDP(artist_name)
    artist_cont = urljoin(CONTAINER, loc)
    song_id = UuidUri('song')
    g = Graph()
    g.bind('mc', MC)
    g.add((MC[song_id], RDF.type, MC.Song))
    g.add((MC[song_id], RDFS.label, Literal('{0} by {1}'.format(song_name, artist_name))))
    g.add((MC[song_id], MC.performer_name, Literal(artist_name)))
    g.add((MC[song_id], MC.song_name, Literal(song_name)))
    turtl = g.serialize(None, base=MC[song_id], format='turtle')
    req_headers = getRequestHeaders(slug=song_id, link='')
    print(req_headers)
    r = requests.post(artist_cont, data=turtl, headers=req_headers, verify=False)
    loc = r.headers["Location"] if (r.status_code == 201) else None
    print("Song add:", loc)
    return MC[song_id]


def createSongTrackAnnotation(artist_name, artist_id, song_name, track_ids, song_uri):
    req_headers = getRequestHeaders(slug='{0} by {1} Etree'.format(song_name, artist_name))
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    loc = r.headers["Location"]
    annotations_cont = urljoin(CONTAINER, loc)
    print(annotations_cont)
    for track_id, calma_id in track_ids:
        g = Graph()
        g.bind('mc', MC)
        g.bind('oa', OA)
        annotation_id = UuidUri('annotation')
        annotation_uri = MC[annotation_id]
        g.add((annotation_uri, RDF.type, OA.Annotation))
        g.add((annotation_uri, OA.hasTarget, song_uri))
        body_bnode = BNode()
        g.add((annotation_uri, OA.hasBody, body_bnode))
        g.add((body_bnode, MC.etree_performer, URIRef(artist_id)))
        g.add((body_bnode, MC.calma, URIRef(calma_id)))
        g.add((body_bnode, MC.etree_track, URIRef(track_id)))
        g.add((annotation_uri, OA.motivatedBy, MC.SongToRecording))
        turtl = g.serialize(None, base=annotation_uri, format='turtle')
        req_headers["Link"] = ''
        req_headers["Slug"] = annotation_id
        r = requests.post(annotations_cont, data=turtl, headers=req_headers, verify=False)
        loc = r.headers["Location"] if (r.status_code == 201) else None
        print("Annotation add:", loc)
  

def main():
    artist_name = sys.argv[1] # 'Mogwai'
    song_name = sys.argv[2]   # 'Acid Food'
    artist_id = getArtistId(artist_name)
    track_ids = getEtreeTracks(artist_id, song_name)
    song_uri = createSongLDP(artist_name, song_name)
    createSongTrackAnnotation(artist_name, artist_id, song_name, track_ids, song_uri)


main()

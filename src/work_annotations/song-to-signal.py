from rdflib import Graph, URIRef, RDF, RDFS, Namespace, Literal
from uuid import uuid4
from SPARQLWrapper import SPARQLWrapper, JSON
import requests, os, sys
from urllib.parse import urljoin

CONTAINER = "https://localhost:8443/public/"
if (os.environ["CONTAINER"]): CONTAINER = os.environ["CONTAINER"]
SPARQL = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
SPARQL.setReturnFormat(JSON)
MC = Namespace('http://example.com/meldedcalma/')
OA = Namespace('http://www.w3.org/ns/oa#')


def getArtistId(artist_name):
    q = ''' PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT ?artistId {{ ?artistId foaf:name "{0}" . }}'''.format(artist_name)
    SPARQL.setQuery(q)
    return SPARQL.query().convert()["results"]["bindings"][0]['artistId']['value']


def getEtreeTracks(artist_id, song_name):
    q = ''' PREFIX mo: <http://purl.org/ontology/mo/>
            PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?trackId {{ 
            <{0}> mo:performed [ event:hasSubEvent ?trackId ] .
            ?trackId skos:prefLabel "{1}" . }}'''.format(artist_id, song_name)
    SPARQL.setQuery(q)
    track_ids = []
    for res in SPARQL.query().convert()["results"]["bindings"]:
        track_ids.append(res['trackId']['value'])
    return track_ids


def createArtistLDP(artist_name):
    req_headers = { "Content-Type": "text/turtle",
                    "Link": '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"',
                    "Slug": artist_name.replace(' ', '_') }
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    loc = r.headers["Location"]
    print("Artist add:", loc)
    return loc


def createSongLDP(artist_name, song_name):
    loc = createArtistLDP(artist_name)
    artistCont = urljoin(CONTAINER, loc)
    song_id = 'song_' + str(uuid4()).replace('-','')
    g = Graph()
    g.bind('mc', 'http://example.com/meldedcalma/')
    g.add((MC[song_id], RDF.type, MC.Song))
    g.add((MC[song_id], RDFS.label, Literal('{0} by {1}'.format(song_name, artist_name))))
    #g.add((MC[song_id], MC.etree_performer_id, URIRef(artist_id)))
    g.add((MC[song_id], MC.performer_name, Literal(artist_name)))
    g.add((MC[song_id], MC.song_name, Literal(song_name)))
    turtl = g.serialize(None, base=MC[song_id], format='turtle')
    req_headers = { "Content-Type": "text/turtle", "Link": '', "Slug": song_id }
    r = requests.post(artistCont, data=turtl, headers=req_headers, verify=False)
    loc = r.headers["Location"] if (r.status_code == 201) else None
    print("Song add:", loc)
    return MC[song_id]


def createSongTrackAnnotation(artist_name, artist_id, song_name, track_ids, song_uri):
    req_headers = { "Content-Type": "text/turtle",
                    "Link": '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"',
                    "Slug": '{0} by {1} Etree'.format(song_name, artist_name).replace(' ', '_') }
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    loc = r.headers["Location"]
    annotationsCont = urljoin(CONTAINER, loc)
    print(annotationsCont)
    for t in track_ids:
        g = Graph()
        g.bind('mc', 'http://example.com/meldedcalma/')
        g.bind('oa', 'http://www.w3.org/ns/oa#')
        annotation_id = 'annotation_' + str(uuid4()).replace('-','')
        annotation_uri = MC[annotation_id]
        g.add((annotation_uri, RDF.type, OA.Annotation))
        g.add((annotation_uri, OA.hasTarget, song_uri))
        g.add((annotation_uri, MC.etree_performer_id, URIRef(artist_id)))
        g.add((annotation_uri, OA.hasBody, URIRef(t)))
        g.add((annotation_uri, OA.motivatedBy, MC.SongToRecording))
        turtl = g.serialize(None, base=annotation_uri, format='turtle')
        req_headers["Link"] = ''
        req_headers["Slug"] = annotation_id
        r = requests.post(annotationsCont, data=turtl, headers=req_headers, verify=False)
        loc = r.headers["Location"] if (r.status_code == 201) else None
        print("Annotation add:", loc)
  

def main():
    artist_name = sys.argv[1] # 'Grateful Dead'
    song_name = sys.argv[2] # 'Sugaree'
    artist_id = getArtistId(artist_name)
    track_ids = getEtreeTracks(artist_id, song_name)
    song_uri = createSongLDP(artist_name, song_name)
    createSongTrackAnnotation(artist_name, artist_id, song_name, track_ids, song_uri)


main()

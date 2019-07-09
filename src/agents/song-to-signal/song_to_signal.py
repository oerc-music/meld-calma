from rdflib import Graph, URIRef, RDF, RDFS, Namespace, Literal, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import requests, os, sys
from urllib.parse import urljoin
from uuid import uuid4
import warnings
warnings.filterwarnings('ignore')

CONTAINER = "https://localhost:8443/public/"
if (os.environ["CONTAINER"]): CONTAINER = os.environ["CONTAINER"]
SPARQL = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
SPARQL.setReturnFormat(JSON)

MC = Namespace('http://example.com/meldedcalma/')
OA = Namespace('http://www.w3.org/ns/oa#')
LDP = Namespace('http://www.w3.org/ns/ldp#')

ETREE_QUERY = '''
PREFIX mo: <http://purl.org/ontology/mo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX calma: <http://calma.linkedmusic.org/vocab/>
PREFIX etree: <http://etree.linkedmusic.org/vocab/>
SELECT ?artist_uri ?track_uri ?calma ?date
{{  ?artist_uri a mo:MusicArtist ;
        foaf:name "{0}" ;
        mo:performed ?performance .
    ?performance event:hasSubEvent ?track_uri ;
        etree:date ?date .
    ?track_uri calma:data ?calma ;
        skos:prefLabel ?song .
    FILTER (lcase(str(?song)) = "{1}") }}
    ORDER by ?date
'''


NEWHEADER = { "Accept": "text/turtle" }

def queryTracks(artist_name, song_name):
    # if multiple recordings for one dat, try to find SBD flac16
    result_dict = {}
    q = ETREE_QUERY.format(artist_name, song_name.lower())
    SPARQL.setQuery(q)
    res = SPARQL.query().convert()
    for r in res["results"]["bindings"]:
        artist_id = str(r['artist_uri']['value'])
        date = str(r['date']['value'])
        if date not in result_dict: result_dict[date] = []
        result_dict[date].append((r['track_uri']['value'], r['calma']['value']))
    result = []
    for date, v in result_dict.items():
        if len(v) == 1: 
            result.append(v[0])
        else:
            p = None
            for i in v:
                if '.sbd.' in i[0] and 'flac24' not in i[0]:
                    p = i
                    break
            if p == None:
                s = [j for j in i if i[0].find('.sbd.') != -1]
                if s != []: p = s[0]
            if p == None: p = v[0]
            result.append(p)
    return (artist_id, result)


def getRequestHeaders(slug='', link='<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'):
    return { "Content-Type": "text/turtle",
             "Link": link,
             "Slug": slug.replace(' ', '_') }


def randomId(s):
    return s + '_' + str(uuid4()).replace('-','')


def createSongLDP(artist_name, song_name, artist_loc, artist_song_loc):
    artist_song_loc = urljoin(CONTAINER, artist_song_loc)
    #song_id = randomId('song')
    song_id = '{0} by {1}'.format(song_name, artist_name) 
    g = Graph()
    g.bind('mc', MC)
    g.add((URIRef(''), RDF.type, MC.Song))
    g.add((URIRef(''), RDFS.label, Literal(song_id)))
    g.add((URIRef(''), MC.performer, URIRef(artist_loc)))
    g.add((URIRef(''), MC.song_name, Literal(song_name)))
    turtl = g.serialize(None, base=artist_song_loc, format='turtle')
    req_headers = getRequestHeaders(slug=song_id, link='')
    r = requests.post(artist_song_loc, data=turtl, headers=req_headers, verify=False)
    song_loc = r.headers["Location"] if (r.status_code == 201) else None
    print("Song add:", song_loc)
    return song_loc


def createArtistLDPs(artist_name, artist_etree, artists_loc):
    artists_cont = urljoin(CONTAINER, artists_loc)
    #artist_id = randomId('artist')
    g = Graph()
    g.bind('mc', MC)
    g.add((URIRef(''), RDF.type, MC.Artist))
    g.add((URIRef(''), MC.performer_name, Literal(artist_name)))
    g.add((URIRef(''), MC.etree,URIRef(artist_etree)))
    turtl = g.serialize(None, base=artists_cont, format='turtle')
    req_headers = getRequestHeaders(slug=artist_name, link='')
    r = requests.post(artists_cont, data=turtl, headers=req_headers, verify=False)

    meta_loc = r.headers["Location"] if (r.status_code == 201) else None
    print("Artist metadata:", meta_loc)

    req_headers = getRequestHeaders(slug=artist_name)
    r = requests.post(CONTAINER + 'artists_songs', headers=req_headers, verify=False)
    artist_song_loc = r.headers["Location"]
    print("Artist (Songs) add:", artist_song_loc)
    return meta_loc, artist_song_loc
    

def createSongTrackAnnotation(artist_loc, track_ids, song_loc, songs_to_recordings_loc):
    annotations_cont = urljoin(CONTAINER, songs_to_recordings_loc)
    for track_id, calma_id in track_ids:
        g = Graph()
        g.bind('mc', MC)
        g.bind('oa', OA)
        annotation_id = randomId('annotation')
        g.add((URIRef(''), RDF.type, OA.Annotation))
        g.add((URIRef(''), OA.hasTarget, URIRef(song_loc)))
        body_bnode = BNode()
        g.add((URIRef(''), OA.hasBody, body_bnode))
        g.add((body_bnode, MC.performer, URIRef(artist_loc)))
        g.add((body_bnode, MC.calma, URIRef(calma_id)))
        g.add((body_bnode, MC.etree_track, URIRef(track_id)))
        g.add((URIRef(''), OA.motivatedBy, MC.SONG_TO_RECORDING))
        turtl = g.serialize(None, base=annotations_cont, format='turtle')
        req_headers = getRequestHeaders()
        req_headers["Link"] = ''
        req_headers["Slug"] = annotation_id
        r = requests.post(annotations_cont, data=turtl, headers=req_headers, verify=False)
        loc = r.headers["Location"] if (r.status_code == 201) else None
        print("Annotation add:", loc)


def createTopLDPs():
    req_headers = getRequestHeaders(slug='artists')
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    artists_loc = r.headers["Location"]
    print("artists add:", artists_loc)
    req_headers = getRequestHeaders(slug='artists_songs')
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    songs_loc = r.headers["Location"]
    print("artists_songs add:", songs_loc)
    req_headers = getRequestHeaders(slug='song_to_recording')
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    recordings_loc = r.headers["Location"]
    print("songs_to_recordings add:", recordings_loc)
    req_headers = getRequestHeaders(slug='song_number_of_occurrences')
    r = requests.post(CONTAINER, headers=req_headers, verify=False)
    occurrences_loc = r.headers["Location"]
    print("song_number_of_occurrences add:", occurrences_loc)
    return artists_loc, songs_loc, recordings_loc, occurrences_loc


def main():
    artist_name = sys.argv[1]
    song_name = sys.argv[2]
    artists_loc, songs_loc, recordings_loc, occurrences_loc = createTopLDPs()
    artist_etree, track_etrees = queryTracks(artist_name, song_name)
    artist_loc, artist_song_loc = createArtistLDPs(artist_name, artist_etree, artists_loc)

    song_loc = createSongLDP(artist_name, song_name, artist_loc, artist_song_loc)
    createSongTrackAnnotation(artist_loc, track_etrees, song_loc, recordings_loc)



main()
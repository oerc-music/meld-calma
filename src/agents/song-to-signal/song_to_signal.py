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


TTLHEADER = { "Accept": "text/turtle" }

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
    g.add((URIRef(artist_song_loc), RDF.type, MC.Song))
    g.add((URIRef(artist_song_loc), RDFS.label, Literal(song_id)))
    g.add((URIRef(artist_song_loc), MC.performer, URIRef(artist_loc)))
    g.add((URIRef(artist_song_loc), MC.song_name, Literal(song_name)))
    turtl = g.serialize(None, base=artist_song_loc, format='turtle')
    req_headers = getRequestHeaders(slug=song_id, link='')
    r = requests.post(artist_song_loc, data=turtl, headers=req_headers, verify=False)
    song_loc = r.headers["Location"] if (r.status_code == 201) else None
    print("Song add:", song_loc)
    return song_loc


def createArtistLDPs(artist_name, artist_etree, artists_loc, songs_loc):
    meta_loc = checkResource(artists_loc, predicate=MC.performer_name, obj=Literal(artist_name))
    if meta_loc:
        print("Artist metadata exists:", meta_loc)
    else:
        artists_cont = urljoin(CONTAINER, artists_loc)
        g = Graph()
        g.bind('mc', MC)
        g.add((URIRef(artists_cont), RDF.type, MC.Artist))
        g.add((URIRef(artists_cont), MC.performer_name, Literal(artist_name)))
        g.add((URIRef(artists_cont), MC.etree,URIRef(artist_etree)))
        turtl = g.serialize(None, base=artists_cont, format='turtle')
        req_headers = getRequestHeaders(slug=artist_name, link='')
        r = requests.post(artists_cont, data=turtl, headers=req_headers, verify=False)
        meta_loc = r.headers["Location"] if (r.status_code == 201) else None
        print("Artist metadata add:", meta_loc)

    songs_cont = urljoin(CONTAINER, songs_loc)

    artist_song_loc = checkResource(songs_loc, predicate=MC.performer, obj=meta_loc)
    if artist_song_loc:
        print("Artist song exists:", artist_song_loc)
    else:
        g = Graph()
        g.add((URIRef(songs_cont), MC.performer, URIRef(meta_loc)))
        turtl = g.serialize(None, base=songs_cont, format='turtle')
        req_headers = getRequestHeaders(slug=artist_name)
        r = requests.post(songs_cont, data=turtl, headers=req_headers, verify=False)
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
        g.add((URIRef(annotations_cont), RDF.type, OA.Annotation))
        g.add((URIRef(annotations_cont), OA.hasTarget, URIRef(song_loc)))
        g.add((URIRef(annotations_cont), OA.hasBody, URIRef(track_id)))
        g.add((URIRef(annotations_cont), OA.motivatedBy, MC.SONG_TO_RECORDING))
        turtl = g.serialize(None, base=annotations_cont, format='turtle')
        req_headers = getRequestHeaders()
        req_headers["Link"] = ''
        req_headers["Slug"] = annotation_id
        r = requests.post(annotations_cont, data=turtl, headers=req_headers, verify=False)
        loc = r.headers["Location"] if (r.status_code == 201) else None
        print("Annotation add:", loc)


def checkResource(cntnr, subject=None, predicate=None, obj=None):
    cont = urljoin(CONTAINER, cntnr)
    r = requests.get(cont , headers=TTLHEADER, verify=False)
    #print(r.content.decode())
    g = Graph()
    g.parse(data=r.content, format='turtle', publicID=cont)
    resources = g.objects(predicate=LDP.contains)
    for res in resources:
        r = requests.get(res, headers=TTLHEADER, verify=False)
        #print(r.content.decode())
        g = Graph()
        g.parse(data=r.content, format='turtle', publicID=res)  
        turtl = g.serialize(None, format='turtle')
        #print(turtl.decode())
        #print(predicate, 'PRED')
        saved_obj = list(g.objects(subject, predicate))
        if saved_obj != []: saved_obj = saved_obj[0]
        if saved_obj == obj: return res


def checkLDP(sl):
    cont = CONTAINER + sl + '/'
    r = requests.get(cont , headers=TTLHEADER, verify=False)
    if r.status_code == 200:
        loc = cont
        print('{0} exists:'.format(sl), loc)
    else:
        req_headers = getRequestHeaders(slug=sl)
        r = requests.post(CONTAINER, headers=req_headers, verify=False)
        loc = r.headers["Location"]
        print('{0} add:'.format(sl), loc)
    return loc


def createTopLDPs():
    artists_loc = checkLDP('artists')
    songs_loc = checkLDP('artists_songs')
    recordings_loc = checkLDP('song_to_recording')
    return artists_loc, songs_loc, recordings_loc


def main():
    artist_name = sys.argv[1]
    song_name = sys.argv[2]
    artists_loc, songs_loc, recordings_loc = createTopLDPs()
    artist_etree, track_etrees = queryTracks(artist_name, song_name)
    artist_loc, artist_song_loc = createArtistLDPs(artist_name, artist_etree, artists_loc, songs_loc)
    song_loc = createSongLDP(artist_name, song_name, artist_loc, artist_song_loc)
    #createSongTrackAnnotation(artist_loc, track_etrees, song_loc, recordings_loc)



main()
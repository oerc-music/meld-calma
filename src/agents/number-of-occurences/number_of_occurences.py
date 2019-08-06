from rdflib import Graph, URIRef, RDF, RDFS, Namespace, Literal, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import requests, os, sys
from urllib.parse import urljoin
from uuid import uuid4
import warnings
warnings.filterwarnings('ignore')

CONTAINER = "https://localhost:8443/public/"
if (os.environ["CONTAINER"]): CONTAINER = os.environ["CONTAINER"]

TTLHEADER = { "Accept": "text/turtle" }
LDP = Namespace('http://www.w3.org/ns/ldp#')
MC = Namespace('http://example.com/meldedcalma/')
OA = Namespace('http://www.w3.org/ns/oa#')


def getRequestHeaders(slug='', link='<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'):
    return { "Content-Type": "text/turtle",
             "Link": link,
             "Slug": slug.replace(' ', '_') }


def ldpContains(cont):
    cont = urljoin(CONTAINER, cont)
    r = requests.get(cont , headers=TTLHEADER, verify=False)
    g = Graph()
    g.parse(data=r.content, format='turtle', publicID=cont)
    resources = g.objects(predicate=LDP.contains)
    g = Graph()
    for res in resources:
        #print(res)
        r = requests.get(res, headers=TTLHEADER, verify=False)
        g.parse(data=r.content, format='turtle', publicID=res)
    return g


def randomId(s):
    return s + '_' + str(uuid4()).replace('-','')

    
def checkArtist(artist_name):
    g = ldpContains(CONTAINER + 'artists/')
    artist_res = list(g.subjects(MC.performer_name, Literal(artist_name)))
    if len(artist_res) == 0: print('artist not found')
    else: return artist_res[0]  


def artistSong(artist_res, song_name):
    g = ldpContains('artists_songs/')
    performer = list(g.subjects(MC.performer, artist_res))[0]
    g = ldpContains(performer)
    song_res = list(g.subjects(MC.song_name, Literal(song_name)))
    if len(song_res) == 0: print('song not found')
    else: return song_res[0]  
    

def numberOfSongs(song_res):
    g = ldpContains('song_to_recording/')
    n = len(list(g.subjects(OA.hasTarget, song_res)))
    if n == 0: print('No occurrences found.')
    else: return n
    

def checkLdp(sl):
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


def postNumber(song_res, n, occur_cont):
    occur_id = randomId('song_occurrence')
    song_occur_cont = urljoin(occur_cont, occur_id)
    print(song_occur_cont)
    g = Graph()
    g.add((URIRef(song_occur_cont), RDF.type, OA.Annotation))
    g.add((URIRef(song_occur_cont), OA.hasTarget, URIRef(song_res)))
    g.add((URIRef(song_occur_cont), OA.motivatedBy, MC.SONG_NUM_RECORDINGS))
    bnode = BNode()
    g.add((URIRef(song_occur_cont), OA.hasBody, bnode))
    g.add((bnode, MC.number_of_recordings, Literal(n)))
    turtl = g.serialize(None, base=song_occur_cont, format='turtle')
    req_headers = getRequestHeaders()
    req_headers["Link"] = ''
    req_headers["Slug"] = occur_id
    r = requests.post(urljoin(CONTAINER, occur_cont), data=turtl, headers=req_headers, verify=False)
    loc = r.headers["Location"] if (r.status_code == 201) else None
    print("Annotation add:", loc)


def checkOccurrence(song_res, occur_cont):
    print(occur_cont)
    g = ldpContains(occur_cont)
    occur_res = list(g.subjects(OA.hasTarget, URIRef(song_res)))
    if len(occur_res) != 0: 
        print('number of occurrences resource already exists')
        return True
    else: 
        return False


def main():
    artist_name = sys.argv[1]
    song_name = sys.argv[2] 
    artist_res = checkArtist(artist_name)
    print(artist_res)
    song_res = artistSong(artist_res, song_name)
    print(song_res)
    occur_cont = checkLdp('song_number_of_occurrences')
    if not checkOccurrence(song_res, occur_cont):
        n = numberOfSongs(song_res)
        #print(n)
        if n: postNumber(song_res, n, occur_cont)

   


main()
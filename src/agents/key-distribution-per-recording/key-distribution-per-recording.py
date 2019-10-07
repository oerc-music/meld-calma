# TODO: write to server, currently writes local rdf

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, BNode, Literal, XSD
import re, tarfile, urllib.request, os, sys, requests
from uuid import uuid4
from progressbar import ProgressBar
import multiprocessing as mp
from itertools import repeat
from urllib.parse import urljoin
import warnings
warnings.filterwarnings('ignore')

THREADS = 10
manager = mp.Manager()
count = manager.Value('i', 0)

CONTAINER = "https://localhost:8443/public/"
if (os.environ["CONTAINER"]): CONTAINER = os.environ["CONTAINER"]

TTLHEADER = { "Accept": "text/turtle" }

LDP = Namespace('http://www.w3.org/ns/ldp#')


SPARQL = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
SPARQL.setReturnFormat(JSON)

ETREE_TRACK = Namespace('http://etree.linkedmusic.org/track/')
PROV = Namespace('http://www.w3.org/ns/prov#')
EVENT = Namespace('http://purl.org/NET/c4dm/event.owl#')
TL = Namespace('http://purl.org/NET/c4dm/timeline.owl#')
AF = Namespace('http://purl.org/ontology/af/')
VAMP_PLUGINS = Namespace('http://vamp-plugins.org/rdf/plugins/')
VAMP = Namespace('http://purl.org/ontology/vamp/')
MO = Namespace('http://purl.org/ontology/mo/') 
MC = Namespace('http://example.com/meldedcalma/')
ETREE = Namespace('http://etree.linkedmusic.org/vocab/')


FEATURE = AF.KeyChange
VAMP_OUTPUT = 'qm-vamp-plugins#qm-keydetector_output_key'

ETREE_QUERY = '''
PREFIX mo: <http://purl.org/ontology/mo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX calma: <http://calma.linkedmusic.org/vocab/>
PREFIX etree: <http://etree.linkedmusic.org/vocab/>
SELECT ?track ?calma ?date
{{  ?artist a mo:MusicArtist ;
        foaf:name "{0}" ;
        mo:performed ?performance .
    ?performance event:hasSubEvent ?track ;
        etree:date ?date .
    ?track calma:data ?calma ;
        skos:prefLabel ?song .
    FILTER (lcase(str(?song)) = "{1}") }}
    ORDER by ?date
'''

ETREE_SOLID_QUERY = '''

'''

TRANSFORM_QUERY = '''
PREFIX vamp: <http://purl.org/ontology/vamp/>
PREFIX x: <urn:ex:>
CONSTRUCT { ?s ?p ?o }
{   ?t a vamp:Transform ; (x:|!x:)* ?s . ?s ?p ?o . } '''


SONG_QUERY = '''
PREFIX mc: <http://example.com/meldedcalma/>
SELECT ?song
{{  ?song mc:performer <{0}> ; mc:song_name "{1}" . }} '''


bar = None

def getRequestHeaders(slug='', link='<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'):
    return { "Content-Type": "text/turtle",
             "Link": link,
             "Slug": slug.replace(' ', '_') }

def queryTracks(artist, song):
    # if multiple recordings for one date, try to find SBD flac16
    result_dict = {}
    q = ETREE_QUERY.format(artist, song.lower())
    SPARQL.setQuery(q)
    res = SPARQL.query().convert()
    for r in res["results"]["bindings"]:
        date = str(r['date']['value'])
        if date not in result_dict: result_dict[date] = []
        result_dict[date].append((r['track']['value'], r['calma']['value']))
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
    return result


def calmaRdf(t, f):
    url = t + '/' + f + '.ttl'
    #print(url)
    g = Graph()
    return g.parse(url, format='turtle')


def analysisRdf(g, t):
    analysis_uri = list(g.subjects(PROV.wasAssociatedWith, VAMP_PLUGINS[VAMP_OUTPUT]))[0]
    analysis = re.findall(r'analysis_(.*?)#activity', analysis_uri)[0]
    blobfile = t + '/analysis_blob_' + analysis + '.tar.bz2'
    tempfile = 'temp/' + str(uuid4()).replace('-', '')
    urllib.request.urlretrieve(blobfile, tempfile)
    tar = tarfile.open(tempfile, mode="r|bz2")
    ttl = tar.extractfile(tarInfo(tar)).read()
    tar.close()
    os.remove(tempfile)
    g = Graph()
    return g.parse(data=ttl, format='turtle')


def tarInfo(tar):
    for tarinfo in tar:
        return tarinfo


def featureEvents(g):
    events = []
    event_uris = g.subjects(RDF.type, FEATURE)
    for e in event_uris:
        event = str(e).split('_')[-1]
        feature = int(list(g.objects(e, AF.feature))[0])
        key = str(list(g.objects(e, RDFS.label))[0])
        at = float(list(g.objects(list(g.objects(e, EVENT.time))[0], TL.at))[0][2:-1])
        events.append([event, feature, key, at])
    return [[(e[1], e[2]), e[3]] for e in sorted(events)]


def featureDuration(f, audio_dur):
    dur_dict = {}
    i = -1
    for i, n in list(enumerate(f))[:-1]:
        if n[0] not in dur_dict: dur_dict[n[0]] = 0
        dur_dict[n[0]] += (f[i+1][1] - f[i][1])
    if f[i+1][0] not in dur_dict: dur_dict[f[i+1][0]] = 0
    dur_dict[f[i+1][0]] += (audio_dur - f[i+1][1])
    return {k: v/audio_dur for k, v in dur_dict.items()}



def checkLDP(sl):
    cont = CONTAINER + sl + '/'
    r = requests.get(cont , headers=TTLHEADER, verify=False)
    if r.status_code == 200:
        loc = cont
        print('{0} exists:'.format(sl), loc)
    elif r.status_code == 401:
        raise "Need to run Solid server with webid=false"
    else:
        req_headers = getRequestHeaders(slug=sl)
        r = requests.post(CONTAINER, headers=req_headers, verify=False)
        loc = r.headers["Location"]
        print('{0} add:'.format(sl), loc)
    return loc



def makeTrackRdf(durations):#, transform_triples):
    bar = ProgressBar(max_value=len(durations)).start()
    signal_uri = URIRef('#signal_0')
    timeline_uri = URIRef('#timeline_0')
    for i, d in enumerate(durations):
        transform_triples = d[-1]
        g = initGraph()
        [g.add(t) for t in transform_triples]
        g.add(( d[3], RDF.type, MO.AudioFile ))
        g.add(( d[3], MO.encodes, signal_uri ))
        g.add(( signal_uri, RDF.type, MO.Signal ))
        time_uri = BNode()
        g.add(( signal_uri, MO.Time, time_uri ))
        g.add(( time_uri, RDF.type, TL.Interval ))
        g.add(( time_uri, TL.onTimeLine, timeline_uri ))
        g.add(( time_uri, TL.duration, Literal('PT{0}S'.format(d[4]), datatype=XSD.duration) ))
        g.add(( URIRef(d[0]), ETREE.audio, URIRef(d[3]) ))
        j = 0
        for k, v in d[2].items():
            duration_uri = MC['#feature_duration_{0}'.format(j)]
            g.add(( duration_uri, RDF.type, MC.FeatureDurationRatio ))
            g.add(( duration_uri, RDFS.label, Literal(k[1]) ))
            g.add(( duration_uri, MC.on_timeline, timeline_uri ))
            g.add(( duration_uri, MC.transform, URIRef('#transform_0') ))
            g.add(( duration_uri, MC.key_id, Literal(k[0]) ))
            g.add(( duration_uri, MC.duration_ratio, Literal(v, datatype=XSD.double) ))
            j += 1
        g.serialize('rdf/{0}_{1}.ttl'.format(d[0].replace(ETREE_TRACK, ''), VAMP_OUTPUT.replace('#', '_')), format='turtle')
        bar.update(i)
    bar.finish()


def initGraph():
    g = Graph()
    g.bind('vamp', VAMP)
    g.bind('event', EVENT)
    g.bind('etree', ETREE)
    g.bind('tl', TL)
    g.bind('mc', MC)
    g.bind('mo', MO)
    g.bind('', '#')
    return g


def trackDur(g):
    return float(list(g.objects(predicate=TL.duration))[0][2:-1])


def transformTriples(track):
    g_analyses = calmaRdf(track, 'analyses')
    g_analysis = analysisRdf(g_analyses, track)
    triples = list(g_analysis.query(TRANSFORM_QUERY))
    for i, t in enumerate(triples):
        if 'transform_' in str(t[0]): 
            triples[i] = (URIRef('#transform_0'), t[1], t[2])
        elif 'transform_' in str(t[2]): 
            triples[i] = (t[0], t[1], URIRef('#transform_0'))
    return triples
        

def listener(q):
    global bar
    while 1:
        g = q.get()
        if g == 1:
            count.value += 1
            bar.update(count.value)
        elif g == 'stop': 
            break


def getFeatures(args):
    return _getFeatures(*args)


def _getFeatures(t, q):
    etree_track = t[0]#.replace(ETREE_TRACK, '')
    calma_track = t[1]
    transform_triples = transformTriples(t[1])
    g_metadata = calmaRdf(calma_track, 'metadata')
    audio_dur = trackDur(g_metadata)
    g_analyses = calmaRdf(calma_track, 'analyses')
    g_analysis = analysisRdf(g_analyses, calma_track)
    feature_events = featureEvents(g_analysis)
    durations = featureDuration(feature_events, audio_dur)
    audio_uri = list(g_analysis.subjects(RDF.type, MO.AudioFile))[0]
    q.put(1)
    return [etree_track, audio_dur, durations, audio_uri, audio_dur, transform_triples]


def keyCorpusProportions(features_list):
    durs = {}
    for t in features_list:
        for k, v in t[2].items():
            if k not in durs: durs[k] = 0
            durs[k] += v * t[4]
    ckmax = max(durs.values())
    return {k: v/ckmax for k, v in durs.items()}
        

def keyTypicalities(features_list, corpus_props):
    typs = []
    for t in features_list:
        typ = 0
        etree_track = t[0]
        audio_dur = t[1]
        typ = sum([v * corpus_props[k] for k, v in t[2].items()])
        typs.append((etree_track, typ))
    typs.sort(key=lambda i: i[1], reverse=True)
    return typs


def createDirectory(d):
    if not os.path.exists(d):
        os.mkdir(d)


def checkArtist(artist):
    artist_cont = CONTAINER + 'artists/'
    r = requests.get(artist_cont , headers=TTLHEADER, verify=False)
    g = Graph()
    g.parse(data=r.content, format='turtle', publicID=artist_cont)
    resources = g.objects(predicate=LDP.contains)
    for res in resources:
        r = requests.get(res, headers=TTLHEADER, verify=False)
        g = Graph()
        g.parse(data=r.content, format='turtle', publicID=res)  
        saved_name = list(g.objects(predicate=MC.performer_name))[0]
        if artist == str(saved_name): return res


def checkSong(artist_uri, song):
    artist_song_cont = CONTAINER + 'artists_songs/'
    r = requests.get(artist_song_cont , headers=TTLHEADER, verify=False)
    g = Graph()
    g.parse(data=r.content, format='turtle', publicID=artist_song_cont)
    resources = g.objects(predicate=LDP.contains)
    for res in resources:
        print(res)
        r = requests.get(res, headers=TTLHEADER, verify=False)
        g = Graph()
        g.parse(data=r.content, format='turtle', publicID=res)    
        ttls = g.objects(predicate=LDP.contains)
        for ttl in ttls:
            r = requests.get(ttl, headers=TTLHEADER, verify=False)
            g = Graph()
            g.parse(data=r.content, format='turtle', publicID=ttl)
            q = SONG_QUERY.format(artist_uri, song)
            qr = list(g.query(q))
            if qr != []: return qr[0][0]


def getEtreeRecordings(songUri):
    song_rec_cont = CONTAINER + 'song_to_recording/'
    r = requests.get(song_rec_cont , headers=TTLHEADER, verify=False)
    g = Graph()
    g.parse(data=r.content, format='turtle', publicID=song_rec_cont)
    resources = g.objects(predicate=LDP.contains)
    
    for res in resources:
        print(res)



    return

def main():
    global bar
    createDirectory('temp')
    createDirectory('rdf') 
    artist = 'Mogwai'   # sys.argv[1]
    song = 'Acid Food'  # sys.argv[2]
    song = song.lower()

    artist_uri = checkArtist(artist)
    if artist_uri:
        print(artist_uri)
        song_uri = checkSong(artist_uri, song)
        if song_uri: print(song_uri)
        else: return

    #getEtreeRecordings(song_uri)
        
    #return

    tracks = queryTracks(artist, song)
    print(tracks)
    #transform_triples = transformTriples(tracks)
    print('fetching audio features')
    bar = ProgressBar(max_value=len(tracks)).start()
    q = manager.Queue()
    pool = mp.Pool(THREADS + 1)
    watcher = pool.apply_async(listener, (q,))
    features_list = pool.map(getFeatures, zip(tracks, repeat(q)), chunksize=1)
    q.put('stop')
    pool.close()
    pool.join()
    bar.finish()

    print('serialising RDF')
    makeTrackRdf(features_list)#, transform_triples)

    #key_dist_rec_loc = checkLDP('key distribution per recording')
    


    #key_corpus_proportions = keyCorpusProportions(features_list)  # check if working correctly
    #key_typicalities = keyTypicalities(features_list, key_corpus_proportions)

    #[print(k) for k in key_typicalities]
     

main()

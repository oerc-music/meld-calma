from SPARQLWrapper import SPARQLWrapper, JSON

class Artist():
    prefixes = '''
            PREFIX etree: <http://etree.linkedmusic.org/vocab/>
            PREFIX mo: <http://purl.org/ontology/mo/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX calma: <http://calma.linkedmusic.org/vocab/>'''
    
    def __init__(self, artist_name):
        artist_query = '''{0}
            SELECT DISTINCT ?artist_uri {{
            ?artist_uri a mo:MusicArtist ;
                skos:prefLabel """{1}""" . }}'''
        sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(artist_query.format(self.prefixes, artist_name))
        self.name = artist_name
        artist_uri = sparql.query().convert()["results"]["bindings"]
        if artist_uri != []:
            self.uri = sparql.query().convert()["results"]["bindings"][0]['artist_uri']['value']
            self.getSongs(self.uri)
        else:
            self.songs = {}
        
    def getSongs(self, uri):
        song_query = '''{0}
            SELECT DISTINCT ?track_uri ?track_name {{
            ?track_uri a etree:Track ;
                calma:data ?calma ;
                mo:performer <{1}> ;
                skos:prefLabel ?track_name . }}''' # only tracks with calma data
        sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(song_query.format(self.prefixes, uri))
        self.songs = {}
        for res in sparql.query().convert()["results"]["bindings"]:
            track_name = self.processTrackName(res['track_name']['value'])
            if track_name not in self.songs:
                self.songs[track_name] = [res['track_uri']['value']]
            else:
                self.songs[track_name].append(res['track_uri']['value'])

    def processTrackName(self, name):
        return name


def getArtistGraph(artistname):
    return Artist(artistname)




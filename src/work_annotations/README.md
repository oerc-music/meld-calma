# meld-calma/src/work_annotations

Python 3 script creating RDF (turtle) files in folder 'annotations', one file per artist. Files include one Work per song, and one Annotation per respective etree Track. Only etree tracks with CALMA data are considered. 

## RDF example for one annotation/work

mc:annotation_0000e0c7-4b4e-4ea2-9003-b2579d3ce71f a oa:Annotation ;\
&nbsp;&nbsp;&nbsp;&nbsp; oa:hasBody <http://etree.linkedmusic.org/track/donna2005-07-23.flacf-8> ;\
&nbsp;&nbsp;&nbsp;&nbsp; oa:hasTarget mc:work_f31b7544-2d41-4aa2-86b1-9317308048a2 .

mc:work_f31b7544-2d41-4aa2-86b1-9317308048a2 a mo:MusicalWork ;\
&nbsp;&nbsp;&nbsp;&nbsp; rdfs:label "Killing A Man" ;\
&nbsp;&nbsp;&nbsp;&nbsp; mo:artist <http://etree.linkedmusic.org/artist/4231b840-4aac-012f-19e9-00254bd44c28> .


## Python dependencies:

- rdflib
- SPARQLwrapper
- python-slugify
- requests

## Run: 

$ export CONTAINER=<URI-OF-LDP-CONTAINER>

$ python work_annotations.py

Changing "main(multi=False)" to "main(multi=True)" runs the script with multiprocessing (does not break on errors).
[Not currently used]


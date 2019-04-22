# meld-calma/src/work_annotations

Python 3 script creating RDF (turtle) files in folder 'annotations', one file per artist. Files include one Work per song, and one Annotation per respective etree Track. Only etree tracks with CALMA data are considered. 

## RDF example for one annotation/work

mc:annotation_0000e0c7-4b4e-4ea2-9003-b2579d3ce71f a oa:Annotation ;
    oa:hasBody <http://etree.linkedmusic.org/track/donna2005-07-23.flacf-8> ;
    oa:hasTarget mc:work_f31b7544-2d41-4aa2-86b1-9317308048a2 .

mc:work_f31b7544-2d41-4aa2-86b1-9317308048a2 a mo:MusicalWork ;
    rdfs:label "Killing A Man" ;
    mo:artist [ foaf:name "Donna the Buffalo" ] .

## Python dependencies:

- rdflib
- SPARQLwrapper
- python-slugify

## Run: 
 
$ python work_annotations.py

Changing "main(multi=False)" to "main(multi=True)" runs the script with multiprocessing, which does not break when encoutnering errors.


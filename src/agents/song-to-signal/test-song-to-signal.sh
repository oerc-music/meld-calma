#
# To run these tests:
#
# 1. Install node version manager (`nvm`), and a recent version of nodejs.
#
# 2. Install meld-tool (clone from https://github.com/oerc-music/meld-cli-tools)
#
# 3. Change to directory where meld-tool is installed, 
#           comthen to subdirectory `src/meld-tool/`
#
# 4. Run Solid server as described in README.md
#
# 5. Set up meld-tool. environment:
#
#        . setenv.sh
#
# 6. Remove containers created by agent:
#
#       node $MELD_TOOL remove-container /public/artists/
#       node $MELD_TOOL remove-container /public/artists_songs/
#       node $MELD_TOOL remove-container /public/song_to_recording/
#
# 7. Run Solid server and song-to-signal agent as described in README.md
#
# 8. Run this script
#

# Disable meld-tool attempt to authenticate
export MELD_USERNAME=

# Test containers created

node $MELD_TOOL test-is-container /public/artists/
node $MELD_TOOL test-is-container /public/artists_songs/
node $MELD_TOOL test-is-container /public/artists_songs/Mogwai
node $MELD_TOOL test-is-container /public/song_to_recording/
#@@ test existence of recording workset

# Test resource content

RESOURCE="/public/artists/Mogwai.ttl"
# node $MELD_TOOL show-resource $RESOURCE
node $MELD_TOOL --stdinurl="$RESOURCE" test-rdf-resource $RESOURCE - <<END
@prefix mc: <http://example.com/meldedcalma/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<> a mc:Artist ;
    mc:etree <http://etree.linkedmusic.org/artist/422aecc0-4aac-012f-19e9-00254bd44c28> ;
    mc:performer_name "Mogwai" .
END

RESOURCE="/public/artists_songs/Mogwai/acid_food_by_Mogwai.ttl"
# node $MELD_TOOL show-resource $RESOURCE
node $MELD_TOOL --stdinurl="$RESOURCE" test-rdf-resource $RESOURCE - <<END
@prefix mc: <http://example.com/meldedcalma/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<> a mc:Song ;
    rdfs:label "acid food by Mogwai" ;
    mc:performer </public/artists/Mogwai.ttl> ;
    mc:song_name "acid food" .
END

# Test annotation content

#@@ Select annotation by target + body

RESOURCE=/public/song_to_recording/
ANNOTATIONS=$(node $MELD_TOOL list-container $RESOURCE)
for anno in $ANNOTATIONS; do
    # Pick off first annotation
    ANNOTATION=$anno
    break
done

#@@ Test specific body

node $MELD_TOOL --stdinurl="$ANNOTATION" test-rdf-resource $ANNOTATION - <<END
@prefix mc: <http://example.com/meldedcalma/> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<> a oa:Annotation ;
    oa:hasBody _:body ;     # Wildcard match etree URI; how to test URI domain?
    oa:hasTarget </public/artists_songs/Mogwai/acid_food_by_Mogwai.ttl> ;
    oa:motivatedBy mc:SONG_TO_RECORDING .
END

#@@ Test entry created in recording workset

# End.

#
# To run these tests:
#
# 1. Install node version manager (`nvm`), and a recent version of nodejs.
#
# 2. Activate recent node version in current shell
#
#       . ~/.nvm/nvm.sh             # Activate required node version
#       . ~/.nvm/bash_completion
#
# 3. Install meld-tool (clone from https://github.com/oerc-music/meld-cli-tools)
#
# 4. Change to directory where meld-tool is installed, 
#    then to subdirectory `src/meld-tool/`
#
# 5. Set up meld-tool. environment:
#
#        . setenv.sh
#
# 6. Run Solid server as described in README.md
#
# 7. Remove containers created by agent:
#
#       node $MELD_TOOL remove-container /public/artists/
#       node $MELD_TOOL remove-container /public/artists_songs/
#       node $MELD_TOOL remove-container /public/song_to_recording/
#
# 8. Run Solid server and song-to-signal agent as described in README.md
#
# 9. Run this script
#

# Disable meld-tool attempt to authenticate
export MELD_USERNAME=

# Test containers created

node $MELD_TOOL test-is-container /public/artists/
node $MELD_TOOL test-is-container /public/artists_songs/
node $MELD_TOOL test-is-container /public/artists_songs/Mogwai
node $MELD_TOOL test-is-container /public/song_to_recording/
# test existence of recording workset
node $MELD_TOOL test-is-container /public/recording_workset/
node $MELD_TOOL test-is-container /public/recording_workset/acid_food_by_Mogwai/

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

RESOURCE="/public/artists_songs/Mogwai/Acid_food_by_Mogwai.ttl"
# node $MELD_TOOL show-resource $RESOURCE
node $MELD_TOOL --stdinurl="$RESOURCE" test-rdf-resource $RESOURCE - <<END
@prefix mc: <http://example.com/meldedcalma/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<> a mc:Song ;
    rdfs:label "Acid food by Mogwai" ;
    mc:performer </public/artists/Mogwai.ttl> ;
    mc:song_name "Acid food" .
END

# Test annotation content

RESOURCE="/public/song_to_recording/"
ETREE_NAME="mogwai2006-04-09.sony.flac16-5"
ETREE_REF="http://etree.linkedmusic.org/track/${ETREE_NAME}"
TARGET="/public/artists_songs/Mogwai/Acid_food_by_Mogwai.ttl"
WORKSET_REF="/public/recording_workset/Acid_food_by_Mogwai/recordingref_$ETREE_NAME.ttl"

# echo node $MELD_TOOL find-annotation "$RESOURCE" "$TARGET" meld:ref "$BODY"
# ANNOTATION=$(node $MELD_TOOL find-annotation "$RESOURCE" "$TARGET" "$BODY")
# echo "Find annotation: $ANNOTATION"

ANNOTATION="/public/song_to_recording/song_to_rec_${ETREE_NAME}.ttl"

# node $MELD_TOOL show-resource $ANNOTATION

node $MELD_TOOL --stdinurl="$ANNOTATION" test-rdf-resource $ANNOTATION - <<END
@prefix mc: <http://example.com/meldedcalma/> .
@prefix meld: <http://example.com/meld/> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<> a oa:Annotation ;
    oa:hasTarget <$TARGET> ;
    oa:motivatedBy mc:SONG_TO_RECORDING ;
    oa:hasBody
        [ meld:ref       <$ETREE_REF>
        ; mc:workset_ref <$WORKSET_REF>
        ]
    .
END

# Test entry created in recording workset

# node $MELD_TOOL show-resource $WORKSET_REF

node $MELD_TOOL --stdinurl="$WORKSET_REF" test-rdf-resource $WORKSET_REF - <<END
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix ldp: <http://www.w3.org/ns/ldp#> .
@prefix mc: <http://example.com/meldedcalma/> .
@prefix meld: <http://example.com/meld/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<> a meld:ItemRef,
        mc:RecordingRef,
        ldp:Resource ;
    meld:ref <$ETREE_REF> ;
    mc:artist_song_ref </public/artists_songs/Mogwai/Acid_food_by_Mogwai.ttl> ;
    .
END

# End.

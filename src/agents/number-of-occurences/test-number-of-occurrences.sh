# Tests for song-to-signal agent
#
# To run these tests:
#
# 1. Install node version manager (`nvm`), and a recent version of nodejs.
#
# 2. Install meld-tool (clone from https://github.com/oerc-music/meld-cli-tools)
#
# 3. Change to directory where meld-tool is installed, then to subdirectory `src/meld-tool/`
#
# 4. Set up meld-tool. environment:
#
#       . setenv.sh
#
# 5. Remove containers created by agent:
#
#       node $MELD_TOOL remove-container /public/artists/
#       node $MELD_TOOL remove-container /public/artists_songs/
#       node $MELD_TOOL remove-container /public/song_to_recording/
#       node $MELD_TOOL remove-container /public/song_number_of_occurrences/
#
# 6. Run Solid server and song-to-signal agent as described in README.md, 
#    using a different terminal window.
#
# 7. Change to this directory and run this script
#

# Disable meld-tool attempt to authenticate
export MELD_USERNAME=

# Test containers created

node $MELD_TOOL test-is-container /public/artists/
node $MELD_TOOL test-is-container /public/artists_songs/
node $MELD_TOOL test-is-container /public/artists_songs/Mogwai
node $MELD_TOOL test-is-container /public/song_to_recording/
node $MELD_TOOL test-is-container /public/song_number_of_occurrences/

# Test annotation content

RESOURCE=/public/song_number_of_occurrences/
ANNOTATIONS=$(node $MELD_TOOL list-container $RESOURCE)
for anno in $ANNOTATIONS; do
    # Pick off first annotation
    ANNOTATION=$anno
    break
done

node $MELD_TOOL --stdinurl="$ANNOTATION" test-rdf-resource $ANNOTATION - <<END
@prefix : <#>.
@prefix oa: <http://www.w3.org/ns/oa#>.
@prefix mc: <http://example.com/meldedcalma/>.

<>
    a oa:Annotation;
    oa:hasBody [ mc:number_of_recordings 26 ];
    oa:hasTarget <../artists_songs/Mogwai/acid_food_by_Mogwai.ttl>;
    oa:motivatedBy mc:SONG_NUM_RECORDINGS
    .

END

# End.

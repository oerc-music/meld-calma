MELD/CALMA data model notes

Initially copied from [20190604 meeting notes](planning/20190604-meeting.md).

These are working/tentative design notes, not yet a fixed design.


# Supporting structures

## Annotation container index details

@@TODO.  

See also "workset_feature_index" in "Song selection agent" below?

The intent here is that a specified or directly discoverable container will contain references to all other containers referenced directly or indirectly by the various annotation agents and display (remixer) client software.  There should be enough information to allow containers to be located without explicit prior knowledge beyond the general data model schema - the software should be able to work with annotation containers (and worksets) stored at arbitrary, distriburted locations.

## Song workset

At some point, we may want to add a notion of a "song workset", which follows the general structure of a SOFA workset, but references songs rather than to fragments.  The members of a song workset could look something like this:

    @prefix ldp:  <http://www.w3.org/ns/ldp#>.
    @prefix dc:   <http://purl.org/dc/elements/>.
    @prefix dct:  <http://purl.org/dc/terms/>.
    @prefix meld: <http://example.com/meld/>.         @@@TODO proper namespace URI
    @prefix mc:   <http://example.com/meldedcalma/>.  @@@TODO proper namespace URI
    
    <>
        a mc:SongRef, meld:ItemRef, ldp:Resource;
        dc:creator "John";
        dct:created "2019-06-01T14:09:58+0100";
        meld:ref <artists_songs/Mogwai_xyz/song_xyz.ttl>
        .


# Agent landscape

We discussed what further agents will be needed, and data models for the annotations they would create.

![MELD/CALMA music flows](images/20190604-MELD-CALMA-flows.jpg)

Thenotes below focus on the data models for the annotations produced by trhe various agents.

## Song-to-signal agent

Includes structure to allow us to associate artist resources with artist names.

Proposed, then, is something like:

    /public

      /artists_songs
        /Mogwai_xyz
          /song_xyz.ttl
            <> a mc:Song (?) ;
              rdfs:label "Acid Food by Mogwai" ;
              mc:song_name "Acid Food" ;
              mc:artist_name "Mogwai" ;
              .
         :

      /song_to_recording
        /song_annotation_xyz.ttl
          <> a oa:Annotation ;
            oa:motivatedBy mc:SONG_TO_RECORDING ;
            oa:hasTarget <song_xyz.ttl>
            oa:hasBody <etree_recording_id>
            .

      /artist_name_to_id
        /artist_annotation_xyz.ttl
          <> a oa:Annotation ;
            oa:motivatedBy mc:ARTIST_ID_NAME ;
            oa:hasTarget <...artists_songs/Mogwai_xyz>
            oa:hasBody   [ mc:artist_name "Mogwai" ]    <-- body is bnode; could (should?) have URI
            .

And maybe later...

      /song_name_to_id
        /song_annotation_xyz.ttl
          <> a oa:Annotation ;
            oa:motivatedBy mc:SONG_ID_NAME ;
            oa:hasTarget <...artists_songs/Mogwai_xyz/song_xyz.ttl...> or "song reference" (see below)
            oa:hasBody   [ mc:song_name "Acid Food", "acid food", "AcidFood", etc. ]
            .

Note that the structure of container names here is illustrative: agents and clients should discover container references by following indexes rather than knowledge of the naming structure used.

Otherwise, there seems to have been good progress on the agent, with data extracted from CALMA being written to contaimners on a Solid server, though some design decisions still need to be finalized.

We discussed introducing the notion of a "song reference" as a way to populate worksets of songs (see below).  (See also "fragment reference": https://thalassa2.oerc.ox.ac.uk:4443/public/DEMO/FragRef-009362d3-45d3-469b-be15-c4646f335525.ttl)


## Number of occurrences agent

Create a container of annotations that target songs, and record a count of recordings available for each song.

    /public

      /song_number_of_occurrences
        /anno_song_xyz.ttl
          <> a oa:Annotation ;
            oa:motivatedBy mc:SONG_NUM_RECORDINGS ;
            oa:hasTarget <song_xyz> ;
            oa:hasBody   [ mc:number_of_recordings "n" ] ;
            .


## Fetch-and-unpack agent

(Mentioned by TW in 2019-06-12 meeting)

@@TODO


## Song selection agent

Uses the number of occurrences annotations to create new worksets containing recordings of songs that satisfy the >=100 recordings criteria.  The "workset feature index" container contains annotation resources that connect "Recording workset containers" (see below) with feature annotation containers that relate to that workset.

    /public

      /recording_workset_container
        /recording_xyz
          <recording reference (see below)>
          :

      /workset_feature_index
        /anno_workset_xyz
          <> a oa:Annotation ;
            oa:motivatedBy mc:WORKSET_FEATURE_INDEX ;
            oa:hasTarget <recording_workset_container>
            oa:hasBody   <workset_feature_container>
            .

A separate "Recording workset container" is created for each song identified in the data.  (Later, the annotations may be extended to allow different songs to be treated as variations of the same Work.)

Any agent that subsequently creates a feature annotation container for a workset should also add an entry for that container 


### Recording workset

We add here a notion of a "recording workset", which follows the structure of a SOFA workset that contains references to CALMA recordings rather than to fragments.  The members of a recording workset container look something like this:

    @prefix ldp:  <http://www.w3.org/ns/ldp#>.
    @prefix dc:   <http://purl.org/dc/elements/>.
    @prefix dct:  <http://purl.org/dc/terms/>.
    @prefix meld: <http://example.com/meld/>.         @@@TODO proper namespace URI
    @prefix mc:   <http://example.com/meldedcalma/>.  @@@TODO proper namespace URI
    
    <>
        a mc:RecordingRef, meld:ItemRef, ldp:Resource;
        dc:creator "John";
        dct:created "2019-06-01T14:09:58+0100";
        meld:ref <CALMA recording URI>
        .

The intent is that as each recording is processed by the Song selection agent, its details are stored in the "Recording workset", which can be used to enumerate (or scope) the subsequent activities of annaotation agents and the display (remixer) client.


## Key distribution per recording agent

For a given song-workset (created by Song selection agent), accesses the CALMA data for each recording and writes an annotation for each recording describing the key detection information (containing detected keys and duration within recording).

The resulting annotations would have this general form:

    <> a oa:Annotation ;
      oa:motivatedBy mc:KEY_DISTRIBUTION ;
      oa:hasTarget (recording reference in recording workset)
      oa:hasBody (details @@TBD, based on key disribution data for recording obtained from CALMA)
      .


## Similar occurrences agent (key typicality)

For all recordings, compute an "average" key distribution across all recordings of a given song (workset), and create a per-song annotation recording this.  Then for each recording, calculate a "key typicality" measure that represents deviation from average key distribution of that recording, and create a per-recording annotation for this.

    <> a oa:Annotation ;
      oa:motivatedBy mc:SONG_KEY_PREVALANCE ;
      oa:hasTarget (song reference in song workset)
      oa:hasBody 
        [ mc:key_info 
          [ mc:key_id (key id) ;
            mc:average_prevalence "(fraction)"^(xsd:double)
          ]
        ]
      .

    <> a oa:Annotation ;
      oa:motivatedBy mc:RECORDING_KEY_TYPICALITY ;
      oa:hasTarget (recording reference in recording workset)
      oa:hasBody [ 
          mc:key_typicality "(fraction)"^(xsd:double) ;
          mc:key_info [ 
            mc:key_id (key id) ;
            mc:prevalence "(fraction)"^xsd:double ;
            mc:average_prevalence "(fraction)"^xsd:double ;
          ]
        ]
      .

Also, add a record of the annotation container to a "feature index" container (to allow selection of alternative features for typicality displays).


## SOFA display client

Allow selection of a feature (initially just key typicality) from the "feature index", and read the corresponding typicality annotations and use these to create an appropriate comparative display.







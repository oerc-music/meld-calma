# A decentralised MELD [agent] framework for computational analysis of Live 
Music Archive

## Background

MELD [1] allows various music-related media to be connected/synchronized with each other via musically meaningful structure ,independently of vagaries such as timing within particular performances.  SOFA [2] is a tool originally developed for guided music composition from semantically described music fragments.

We have been using ideas from SOFA to re-implement the logic of rCALMA, a tool for displaying musicological analyses over multiple performances of a work.


## Implementation

SOFA operates on a workset of broadly homogeneous elements with semantic annotations (***LDP containers***), and employs multiple independent analyses of workset elements (***agents***) to create new containers of annotations that are used to inform selection options and to provide values for display, and a web application that reads these annotations to discover selection options, and build a corresponding user interface (***REST, uniform interface, and hypermedia-based discovery***).  The resulting display is in the form of a grid, whose visible contents are rendered by independent agents.  Element descriptions are generally based on existing generic linked data vocabularies, such as MELD [1], FRBR [3], MO [4], etc.

This design allows separation of analysis from presentation, allow a single presentation application to present new forms of analysis as new agents are implemented.

Existing linked data standards are re-used, notably the Web Annotations vocabulary [5] and Linked Data Platform protocol [6], which in turn are layered over RDF [7] and HTTP [8] respectively.  This allows server-side elements to run in an existing software infrastructure, with no special platform-dependent server applications, and the used interface to run in any modern browser, again with no special code needed.  (We successfully moved a previous version of the SOFA application from an earlier implementation of LDP (Gold) to a more modern one (Solid), without any fundamental change to the application logic.)

By building on these standards, the (meta)data created is also available for repurposing by other applications.


## Future work

For the most part, future work would consist of adding new agents to support new forms of analysis and presentation within the existing framework.  These would be self-contained, so not require any changes to existing software components, unless some new capability is required that doesn't fit within the workset and grid presentation model.

Currently missing is a mechanism for orchestrating agent activation.  Experiments with LDP container notifications indicate that we can arrange for agents to be activated automatically when data is updated given some means to connect agents to data elements, probably involving some additional linked data hypermedia structures, which have not yet been designed.

The current implementation makes no concessions to efficiency.  But by building on a uniform interface (LDP), we can identify common access patterns and create optimized paths (in the form of specialized LDP implementations) to overcome any inefficiencies in the current implementation.


## References

[1] MELD, JCDL paper

[2] DMRN SOFA paper/poster

[3] FRBR

[4] MO (Music Ontology)

[5] Web Annotations

[6] LDP - Linked Data Platform

[7] RDF

[8] HTTP




<!--
# 20191108-meld-calma-sofa-features - raw notes

(background...)

1. MELD allows various media to be connected/synchronized with each other via musically meaningful structure.  The connection is thus not dependent on vagaries such as timing within a particular performance.
 
@@see MELD papers; especially the JCDL layered library paper

2. SOFA is being (re-)conceived as a generalized data analysis and presentation platform for interactive construction of data presentations.

@@elucidate aspects of SOFA remixer and MELD/CALMA that are similar:
@@ref DMRN submission last year

(a) applications select data from some workset of broadly homogeneous elements, and create grid presentation based on selected data (fragments, recordings)
(b) read workset annotation metadata to discover selection options, and create UI accordingly.
(c) use of multiple independent analyses of data elements to inform selection options and to provide values for display
(d) re-use of existing, more-or-less generic, vocabularies across different applications (MELD, sonic annotator, ...)

Realization:
(a) LDP containers (ala MELD)
(b) REST, hypermedia-based discovery
(c) agents
(d) MELD, ++

...

(current focus...)

2. Separation of analysis from presentation;  allow a single presentation application to present new forms of analysis as they become available.
 
@@something about hypermedia and REST architecture

3. Builds on existing standards, notably Web Annotations (vocabulary) and Linked Data Platform (protocol), which in turn are layers on RDF and HTTP respectively.  This allows server-side elements to run in existing infrastructure (no special platform-dependent server applications needed), and client presentation code to run in any any modern browser (again, no special platform-dependent code needed).

We successfully moved a previous version of the SOFA application from an earlier implementation of LDP (Gold) to a more modern one (Solid), without any fundamental change to the application logic.

...

(future possibilities...)

4. By building on linked data standards, the (meta)data used by SOFA can be accessed and remixed by different applications for different purposes.

5. Distributed application; analyses can be performed on host systems with appropriate source material access and compute power, while the presentation aspects can be run on any desktop/laptop.
 
@@This potentially can avoid some constraints of access to copyright material

6. Use of existing platform software (SoLiD).

@@something about re-decentralize the web, breaking out of walled gardens


7. Performance optimization: the use of raw LDP by the client software means that some operations result in necessary amounts of network traffic.  One of the future directions for this work will be to identify LDP access patterns that are common across MELD applications, or that are simply inefficient, and implement new API layers over LDP that can be hosted closer to the data to avoid some of the network transfer inefficiencies.  In some cases, optimizations might even be built into an LDP hosting platform, e.g. to take advantage of indexing that isn't normally accessible directly via LDP, while still retaining the possibility of running the application over LDP.  These might, in turn, lead to possible LDP enhancements that could be recommended for incorporated into LDP and/or SoLiD implementations.


....


DMRN submission: 1 page A4 using template - really short - 

https://www.qmul.ac.uk/dmrn/dmrn-14/
https://www.qmul.ac.uk/dmrn/media/dmrn/1page-dmrn14-template.docx

Focus on what has happened, not would could be done.

Suggest GK draft V1, ask for minor revisions
Aim for ~600 words.

...

background/concept

what happened

future work

KP, JPNP, DDeR, TW, GK

JPNP, TW to make poster?
Schedule time to do poster, including script for demo
-->


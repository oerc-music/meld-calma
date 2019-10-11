"""
Support routines for creating and testing LDP containers
"""

import requests, os, sys
from urllib.parse import urljoin

CONTAINER_BASE = os.environ["CONTAINER"] or "https://localhost:8443/public/"

GET_TURTLE_HEADER = { "Accept": "text/turtle" }


def check_container_exists(path):
    """
    Function tests to see if a specified LDP container exists, 
    and returns its URL if it does, otherwise None.

    path    is path (may be relative to service base URL)

    """
    cont_url    = urljoin(CONTAINER_BASE, path)
    r = requests.get(cont_url, headers=TTLHEADER, verify=False)
    if r.status_code == 200:
        print('{0} exists:'.format(path), cont_url)
    elif r.status_code == 401:
        raise "Need to run Solid server with webid=false"
    else:
        cont_url = None
    return cont_url

def create_container_headers(
    slug='', 
    link='<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'):
    """
    Create a header dictionary to be used when creating a cointainer resource.

    The slug is a string used to identify the container, which may be
    modified to be a valid URL path segment

    """
    return { "Content-Type": "text/turtle",
             "Link": link,
             "Slug": slug.replace(' ', '_') }

def ensure_container_exists(parent_ref, slug):
    """
    Function tests to see if a specified LDOP container exists, 
    and creates it if it does not.  Returns the container URL.

    parent_ref  is path (may be relative to container base URL) of parent
    slug        name for new container;
                may be modified to valid path segment syntax.
    """
    parent_url = check_container_exists(parent_ref)
    if not parent_url:
        return parent_url
    req_headers = create_container_headers(slug=slug)
    cont_url    = check_container_exists(urljoin(parent_url, req_headers["Slug"]))
    if not cont_url:
        r = requests.post(parent_url, headers=req_headers, verify=False)
        cont_url = r.headers["Location"]
        print('{0} add:'.format(slug), cont_url)
    return cont_url

def check_referenced_resource(container_ref, subj, pred, value):
    """
    Checks the RDF contents of a container to see if a statement within 
    any contained resource references a specified resource value with
    the supplied subject and predicate.

    If a match is found, returns the URL of the referencing resource,
    otherwise returns None.
    """
    cont_url = check_container_exists(container_ref)
    if not cont_url:
        return cont_url
    # Get list of contained resources
    r = requests.get(cont_url, headers=GET_TURTLE_HEADER, verify=False)
    #print(r.content.decode())
    g = Graph()
    g.parse(data=r.content, format='turtle', publicID=cont_url)
    contents = g.objects(predicate=LDP.contains)
    for res_url in contents:
        r = requests.get(res_url, headers=GET_TURTLE_HEADER, verify=False)
        #print(r.content.decode())
        g = Graph()
        g.parse(data=r.content, format='turtle', publicID=res_url)  
        # turtl = g.serialize(None, format='turtle')
        #print(turtl.decode())
        #print(predicate, 'PRED')
        for referenced_value in g.objects(subj, pred):
            if referenced_value == value:
              return res_url
    # Value not found
    return None

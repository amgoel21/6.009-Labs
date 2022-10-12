import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass




def download_file(url, chunk_size=8192):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    urlcache={} # cache is dictionary with url as keys
    for link in urlchecker(url,chunk_size,urlcache):
        yield link


def check_redirects(url):
    ''' Given a url, checks status code to see if redirect, and then makes sure there is a repeated redirect causing infinite chain '''
    links = set()
    newurl=url
    c=True # Is a redirect
    while(c):
        links.add(newurl) # Add to set of new links
        try: 
            r=http_response(newurl)
        except Exception:
            raise HTTPRuntimeError
        c=((r.status==301) or (r.status == 302) or (r.status == 307))
        if(c==False): # New link not redirect, so done
            return True
        if(newurl in links): # Repeated redirect link error
            return False



def get_resman(url):
    ''' Given url, returns HTTPresponse object and boolean of whether this is manifest type
    May also return error if status code says so. Will return response/manifest of redirect is indicated by status code'''
    try:
        r = http_response(url)
    except Exception:
        raise HTTPRuntimeError
    s = r.status
    if(s == 404):
        raise HTTPFileNotFoundError
    elif(s == 500):
        raise HTTPRuntimeError
    elif(s == 200):
        if(url[len(url)-6:]=='.parts'): # If url ends in .parts
            return r,True
        if (r.getheader('content-type') == 'text/parts-manifest'): 
            return r,True
        return r,False
    else:
        """ repeatedredirects = check_redirects(url)
        if(repeatedredirects==False):
            raise HTTPRuntimeError """
        return get_resman(r.getheader('location'))

def urlchecker(url,chunk_size,cache):
    ''' This takes in a url, chunk_size, cache dictionary
    Directly yields portion of bytestring if not manifest
    If manifest, then creates sets of urls contained within the same block
    Runs the urls in each set through this again until one fully works'''
    r,manifest = get_resman(url)
    if(manifest==False):
        thing = r.read(chunk_size)
        while (thing != b''): # Empty bytestring
            yield thing
            thing = r.read(chunk_size)
    else:
        def manifestgenerators(r):
            newline= r.readline()
            while (newline != b''):
                link = set()
                while (newline != b'') and (newline != b'--\n'): # Either reached end or new type of links
                    link.add(newline.strip()) # Removes spaces and \n characters
                    newline = r.readline()
                yield link
                newline = r.readline()
        for i in manifestgenerators(r):
            for j in manifestfiles(i,chunk_size,cache): # Try links one at a time to see if they work
                yield j


def manifestfiles(urls, chunk_size, urlcache):
    '''Take in set of urls, and cache (and chunk size)
    If not cache, just checks each link in urls until one fully works (no exceptions thrown) and is done
    If cache, first checks if cache dictionary contains any link in set. If so we just return that
    Otherwise, we just go through links one at a time and add it to cache. If all parts fully go through, we stop'''
    if b'(*)' in urls:
        repeats = set(urlcache.keys()).intersection(urls)
        if (len(repeats)!=0): # We already have one of the links in cache
            for i in repeats:
                yield urlcache[i]
        else:
            urls.remove(b'(*)')
            for url in urls:
                try:
                    for j in urlchecker(url, chunk_size, urlcache): 
                        if url in urlcache:
                            urlcache[url] += j
                        else:
                            urlcache[url] = j
                        yield j
                    break # One link in block works so we can stop
                except:
                    continue # Was some error so try next link
    else:
        for url in urls:
            try:
                for j in urlchecker(url, chunk_size, urlcache):
                    yield j
                break
            except:
                continue

def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    
    current = next(stream)
    file = b''
    pos=b''
    def streamchecker(strand4,bytes,file):
        '''pos is 4 bits for length of file, bytes is bytestring, and file to return even if not completed
        This is a recursive function that would return a tuple of completed file, bytestring not accounted for in file, pos of 4 or less, and file in progress '''
        if len(strand4)==4: #strand is full
            length = strand4[3] + strand4[2]*256**1 + strand4[0]*256**3 + strand4[1]*256**2 # calculate file length
            if length>(len(file)+len(bytes)): #Not enough info for completed file
                return (None,strand4,file+bytes)
            else:
                fullfile = file+bytes[:(length - len(file))] # File completed
                fullbytes = bytes[(length - len(file)):] #Remaining kept in bytestring
                return (fullfile,fullbytes)
        else:
            if((len(strand4)+len(bytes))<4):
                return (None,strand4+bytes,file) # put everything into strand and continue with empty bytestring
            else:
                return streamchecker(strand4+bytes[:4-len(strand4)],bytes[(4-len(strand4)):],file)
    while current != b'':
        newinfo = streamchecker(pos,current,file)
        if(newinfo[0] is None): # No completed file
            file = newinfo[2]
            pos = newinfo[1]
            current = next(stream)
        else:
            yield newinfo[0] # Release completed file
            if newinfo[1]==b'': # Check if bytestring has content
                current=next(stream)
            else:
                current=newinfo[1] 
            pos=b'' #Reset
            file=b''#Reset
            
            

if __name__ == "__main__":
    with open(sys.argv[2], 'ab') as f:
        count = 1
        for file in files_from_sequence(download_file(sys.argv[1], chunk_size=8192)):
            with open(sys.argv[2]+'-file'+str(count),'wb') as q:
                q.write(file)
            count+=1

#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    '''
    Given an image and the 2d coordinates of a pixel, get_pixel returns the pixel in the 1d pixel array
    '''
    return image['pixels'][image['width']*x+y]


def set_pixel(image, x, y, c):
    '''
    Given an image and the 2d coordinates of a pixel, set_pixel changes the pixel in the 1d pixel array to c
    '''
    image['pixels'][image['width']*x+y] = c


def apply_per_pixel(image, func):
    '''
    Given a function and an image, we replace each element in the pixel array with the image of the pixel under the function.
    '''
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color) # applies func on the pixel and saves it as another variable in the loop
            result['pixels'].append(newcolor)

    return result


def inverted(image):
    '''
    This function shows the contrasting image by replacing each pixel with its complement (255-i)
    It implements the apply_per_pixel function
    '''
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    The kernel is represented by a 2D list (list of lists) corresponding to kernel square matrix structure.
    """
    copy = image['pixels'][:] #New version of pixels for final image
    height=image['height']
    width = image['width']
    n = len(kernel)
    k  = int((n-1)/2)
    for i in range(height):
        for j in range(width): # These too loops iterate through whole array of pixels
            copy[width*i+j]=0 #Resets our copied pixel so we can add to it
            for a in range(n):
                for b in range(n):
                    copy[width*i+j]+=(kernel[a][b])*(getpixel_1(image,i-k+a,j-k+b,boundary_behavior)) #For each pixel, we add each effect of the kernel. getpixel_1 determines output of each kernel effect
    d={'height':image['height'],'width':image['width'],'pixels':copy}
    return d


def getpixel_1(image,i,j,boundary_behavior):
    '''
    Given an image and the length and width corresponding to kernel and boundary behavior, returns the pixel value.
    i and j could be out of the image dimensions so we find their values corresponding to boundary_behavior
    '''
    height = image['height']
    width = image['width']
    if((0<=i<height) and (0<=j<width)):
        return image['pixels'][i*width+j]
    elif(boundary_behavior == 'zero'):
        return 0
    elif(boundary_behavior == 'wrap'):
        return image['pixels'][(i % height)*width + (j % width)] # Applies modular arithmetic to find height and width in dimensions
    elif(boundary_behavior == 'extend'):
        x=max(0,i)
        y=max(0,j)
        if(x>=(height-1)): #Finds if valid height or if too small or too large
            x=height-1
        if (y >= (width - 1)): #Finds if valid width or if too small or too large
            y = width - 1
        return image['pixels'][x*width+y]
    




def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i in range(len(image['pixels'])):
        image['pixels'][i]=round(image['pixels'][i])
        if(image['pixels'][i]>255):
            image['pixels'][i]=255
        if (image['pixels'][i] < 0):
            image['pixels'][i] = 0


# FILTERS

def basicblur(image,n):

    '''
    Blurs an image by creating appropraite kernel given n and then applying correlate with said kernel.
    DOES NOT ROUND-AND_CLIP
    '''
    kernel = nkernel(n)

    newimage = correlate(image, kernel, 'extend')

    return newimage

def blurred(image, n):
    """
    Identical to basicblur, but also round and clips.
    """
    newimage=basicblur(image,n)

    round_and_clip_image(newimage)

    return newimage


def nkernel(n):
    '''
    creates a square nxn kernel where each element equals 1/n^2
    '''
    copy=[]
    for i in range(n):
        copy.append([])
        for j in range(n):
            copy[i].append(1/(n**2))
    return copy

def sharpened(image,n):
    '''
    Creates a blurred image of image given n, but then subtracts from "doubled" copy of image where pixel lightness is doubled
    '''
    blur = basicblur(image,n)
    copy=[]
    for i in range(len(image['pixels'])):
        copy.append(2*image['pixels'][i]-blur['pixels'][i])
    d={'height':image['height'],'width':image['width'],'pixels':copy}
    round_and_clip_image(d)
    return d


def edges(image):
    '''
    Applies two separate kernels to image one at a time
    Then takes total geometric length of two pixels together to determine edges.
    '''
    kernel1 = [[-1,0,1],[-2,0,2],[-1,0,1]]
    kernel2 = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    o1=correlate(image, kernel1, 'extend')
    o2 = correlate(image, kernel2, 'extend')
    copy=[]
    for i in range(len(image['pixels'])):
        copy.append(math.sqrt((o1['pixels'][i])**2+(o2['pixels'][i])**2)) #Takes square root of sum of squares of corresponding pixels
    d={'height':image['height'],'width':image['width'],'pixels':copy}
    round_and_clip_image(d)
    return d



# COLOR FILTERS

def color_filter_from_greyscale_filter(filt):
    '''
    Given a greyscale filter, creates a filter that takes a color image and applies the grey-scale filter to each color
    Then recombines all three colors together to that filter has been applied to color image to get another color image.
    '''

    def colorfilt(image):
        copy1=[]
        copy2=[]
        copy3=[]
        for i in range(len(image['pixels'])):
            copy1.append(image['pixels'][i][0])
            copy2.append(image['pixels'][i][1])
            copy3.append(image['pixels'][i][2])
        d1={'height':image['height'],'width':image['width'],'pixels':copy1}
        d2 = {'height': image['height'], 'width': image['width'], 'pixels': copy2}
        d3 = {'height': image['height'], 'width': image['width'], 'pixels': copy3}
        newd1=filt(d1)
        newd2 = filt(d2)
        newd3 = filt(d3)
        colorp = []
        for i in range((len(image['pixels']))):
            tu=(newd1['pixels'][i],newd2['pixels'][i],newd3['pixels'][i])
            colorp.append(tu)
        newcolorimage = {'height': image['height'], 'width': image['width'], 'pixels': colorp}
        return newcolorimage
    return colorfilt


def make_blur_filter(n):
    '''
    Takes a number for the blurred function, and creates a blur function just for the n
    It can then be used in the color_filter from greyscale filter function
    '''
    def blur_filter(image):
        return blurred(image,n)
    return blur_filter


def make_sharpen_filter(n):
    '''
    Has the same use/implementation as the blur_filter
    '''
    def sharpen_filter(image):
        return sharpened(image,n)
    return sharpen_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def totalcascade(image):
        d={'height':image['height'],'width':image['width'],'pixels':image['pixels']}
        for i in range(len(filters)):
            d=filters[i](d)
        return d
    return totalcascade
def threshold(n):
    '''
    Creates a function that takes in n between 0 and 255
    For each pixel, if it is larger than 255, it becomes 255
    Otherwise it becomes 0
    Thus, all pixels are either 255 or 0
    '''
    def threshold_filter(image):
        a=image['pixels'][:]
        d = {'height': image['height'], 'width': image['width'], 'pixels': a}
        for i in range(len(image['pixels'])):
            if (image['pixels'][i]>n):
                d['pixels'][i]=255
            else:
                d['pixels'][i]=0
        return d
    return threshold_filter

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # kernel = [[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[1,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0]]
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # frog = load_color_image('test_images/frog.png')
    # blueg=load_greyscale_image('test_images/bluegill.png')
    # save_greyscale_image(inverted(blueg),'invertedblue.png')
    # save_color_image(filt(frog),'frogcascade.png')
    a = threshold(140)
    frog = load_greyscale_image('test_images/frog.png')
    save_greyscale_image(a(frog), 'newfrog.png')
    

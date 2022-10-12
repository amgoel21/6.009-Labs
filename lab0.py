# No Imports Allowed!


def backwards(sound):
    """
    Reverse the list of samples of a sound

    Parameter:
    sound dictionary with a rate and a list of samples

    Returns:
    A sound dictionary with the same rate as input, but sample has a reversed list
    """

    # a copy of the list of samples from our sound
    copysamples=sound['samples'][:] # Doesn't modify original object
    # reverse the list
    copysamples.reverse()
    # create a new sound object
    newsound = {'rate':sound['rate'],'samples':copysamples}
    return newsound
    


def mix(sound1, sound2, p):
    """
    Take a weighted average of the two sounds to mix them.

    Parameters:
    Two sounds and the weight p of of sound1

    THe output returns a single sound with samples of sound1 having weight p and sound2 having weight 1-p
    """
    if(sound1['rate']!=sound2['rate']): # makes sure both have same sampling rate
        return None
    n=min(len(sound1['samples']),len(sound2['samples']))
    mixed=[] # sample list for final sound
    for i in range(n):
        weighted=p*sound1['samples'][i]+(1-p)*sound2['samples'][i] # weighs each of the n indexes one at a time
        mixed.append(weighted)
    new={'rate':sound1['rate'],'samples':mixed}
    return new


def convolve(sound, kernel):
    """
    Implements a convolution on the sound sample list corresponding to the kernel

    Parameters: Sound object, 1xn kernel list

    Returns: new sound object
    """
    con=[] #new sound sample list
    for i in range(len(sound['samples'])+len(kernel)-1): # length of con is kernel length * list lenght -1
        con.append(0)
    for i in range(len(kernel)): # Looks at  each kernel element one at a time
        for j in range(len(sound['samples'])): # For each kernel element, look at each element in sample list
            con[i+j]=con[i+j]+kernel[i]*sound['samples'][j] # Skip appropriate amount and add scaled value of sample list
    new = {'rate':sound['rate'],'samples':con}
    return new


def echo(sound, num_echoes, delay, scale):
    """
    Adds eacho feature to sound where sound repeats after a period, but scaled down

    Parameters: The sound object, the number of echoes, the time delay between start of each echo, and the scale down of each echo
    """
    sample_delay = round(delay * sound['rate']) # Calculates the number of sample between each echo
    copy = sound['samples'][:]
    n=len(copy)
    new=[]
    for i in range(sample_delay*num_echoes+n):# This is the total length with the echoes
        new.append(0)
    for i in range(n):
        new[i]=copy[i]
    scaler=1 #Used to keep track of how much the echo is scaled down
    for i in range(num_echoes):
        scaler*=scale   #Each echo is scaled down by the scale each time
        for j in range(n):
            new[(i+1)*sample_delay+j]+=scaler*copy[j]
    d={'rate':sound['rate'],'samples':new}
    return d
    


def pan(sound):
    """
    Switches the magnitudes of the left and right sample lists as time increases.
    """
    n=len(sound['left'])
    left=[]
    right=[]
    for i in range(n):
        left.append(sound['left'][i]*(1-i/(n-1))) # The left sample lists keeps linearly decreasing
        right.append(sound['right'][i] * i / (n-1)) # The right sample lists keep linearly increasing
    d={'rate':sound['rate'],'left':left,'right':right}
    return d


def remove_vocals(sound):
    """
    Takes the difference between the left and right lists to remove the vocals

    Parameter: Stereo sound object

    Returns mono sound object of one sample list without vocals
    """
    mono = []
    for i in range(len(sound['left'])):
        mono.append(sound['left'][i]-sound['right'][i]) # takes difference of left and right sample lists
    d = {'rate':sound['rate'],'samples':mono}
    return d


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()

# if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    # synth = load_wav('sounds/synth.wav')
    # water = load_wav('sounds/water.wav')
    # write_wav(mix(synth,water,0.2), 'mixed.wav')
    # chillpill = load_wav('sounds/ice_and_chilli.wav')
    # kernel = bass_boost_kernel(1000, scale=1.5)
    # write_wav(convolve(chillpill, kernel), 'chillpill.wav')
    # chord = load_wav('sounds/chord.wav')
    # write_wav(echo(chord,5,0.3,0.6), 'chord.wav')
    # car = load_wav('sounds/car.wav', stereo=True)
    # write_wav(pan(car), 'car.wav')
    # mount = load_wav('sounds/lookout_mountain.wav', stereo=True)
    # write_wav(remove_vocals(mount), 'mount.wav')

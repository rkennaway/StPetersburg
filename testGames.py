# See the accompanying file README.md for documentation.
# Written by [redacted], July 2020.

import numpy as np
from scipy.stats import skew
from scipy.stats import kurtosis

import importlib
haveMT = importlib.util.find_spec('MersenneTwister') is not None
if haveMT:
    import MersenneTwister as MT

import argparse
import sys

haveMatplotlib = importlib.util.find_spec('matplotlib') is not None
if haveMatplotlib:
    import matplotlib.pyplot as plt
    import matplotlib.patches


def testGames( game,
               fat=False,
               trunc=16,
               runlength=1000,
               numruns=10000,
               feeratio=0.97,
               firstpassage=None,
               seed=None,
               output="",
               plot=False,
               ownrand=False ):
    if ownrand:
        if not haveMT:
            print( "MersenneTwister.py not found. Try without the -ownrand option.\n" );
            return
        
    gamenames = {
        'stp': 'St. Petersburg',
        'astp': 'Alternating St. Petersburg',
        'pastp': 'Permuted Alternating St. Petersburg',
        'cstp': 'Convergent St. Petersburg',
        'acstp': 'Alternating Convergent St. Petersburg',
        'dull': 'Dull',
        'adull': 'Alternating Dull',
        'pasa': 'Pasadena',
        'ppasa': 'Permuted Pasadena',
        'alta': 'Altadena',
        'palta': 'Permuted Altadena',
        'aix': 'Aix-to-Ghent',
        'paix': 'Permuted Aix-to-Ghent',
        'pdnk': 'Podunk',
        'smlv': 'Smallville',
        'sudd': 'Sudden Death' }

    game = game.lower()
    
    if not gamenames.__contains__(game):
        print( "Game {:s} not recognised.\n".format(game) )
        return;
    gn = gamenames[game]
    
    havefilename = output != ""
    if havefilename:
        append = output[0]=="+"
        if append:
            output = output[1:];
            havefilename = output != ""
    if havefilename:
        f = open( output, "a" if append else "w" );
    else:
        f = sys.stdout
        
    haveFirstPassage = firstpassage != None;

    [prizes,eprizes,probs] = eachPayoff( game, trunc, fat );
    expect = np.sum(eprizes);
    stddev = np.sqrt( np.sum( (prizes**2)*(probs*(1-probs)) ) );
    skewness = sum( probs*((prizes-expect)/stddev)**3 );
    kurt = sum( probs * (prizes-expect)**4 )/stddev**4
    fee = expect * feeratio;
    
    if ownrand:
        MT.initialize_generator(seed)
    else:
        np.random.seed( seed )
    
    turns = numTurns( probs, runlength, numruns, ownrand );
    truncations = np.sum(np.reshape(turns,-1) > trunc);
    payoffs = prizes[ turns-1 ];
    
    net = payoffs-fee;
    cnet = np.cumsum(net,1);

#   The "first downside" is the largest value either player loses before
#   first breaking even.
#
#   Assuming the entry fee is positive, player 1's first downside is necessarily at
#   least equal to the fee, since he must have the resources to pay that before
#   collecting any payoff.
#
#   For player 2, we do not count his receipt of the fee as "breaking even", but only
#   his position at the end of each game, since he is contractually bound to honour
#   the result after accepting the fee.
#
#   For negative fees, these details are reversed.

    firstdownside1 = np.zeros(numruns);
    firstdownside2 = np.zeros(numruns);
    fp = np.zeros(numruns);
    
    for i in range(numruns):
        if fee > 0:
            position1 = np.minimum( cnet[i,:],
                                    np.concatenate([[0], cnet[i,0:(-1)]])-fee );
        else:
            position1 = cnet[i,:];
        wh1 = np.where( cnet[i,:] >= 0 );
        if np.size(wh1)==0:
            firstdownside1[i] = np.min(position1);
        else:
            j1 = wh1[0][0];
            if j1==0:
                # The player is immediately in profit. There is no
                # first downside.
                firstdownside1[i] = 0;
            else:
                firstdownside1[i] = np.min(position1[0:j1]);
                
        if fee < 0:
            position2 = np.maximum( cnet[i,:],
                                    np.concatenate([[0], cnet[i,0:(-1)]])-fee );
        else:
            position2 = cnet[i,:];
        wh2 = np.where( cnet[i,:] <= 0 );
        if np.size(wh2)==0:
            firstdownside2[i] = np.max(position2);
        else:
            j2 = wh2[0][0];
            if j2==0:
                firstdownside2[i] = 0;
            else:
                firstdownside2[i] = np.max(position2[0:j2]);
                
        if haveFirstPassage:
            if firstpassage >= 0:
                zz = np.argwhere( cnet[i,:] >= firstpassage );
            else:
                zz = np.argwhere( cnet[i,:] <= firstpassage );
            if zz.size==0:
                fp[i] = -1
            else:
                fp[i] = zz[0]+1;

    # The "whole downside" is the largest amount either player has lost at
    # any point in a run of RUNLENGTH games.
    wholedownside1 = np.min(cnet,axis=1);
    wholedownside2 = np.max(cnet,axis=1);
    
    payoffPerRun = cnet[:,-1];
    
    np.seterr(divide='ignore')  # We expect to sometimes be dividing by zero.
    

    f.write( "{:s}{:s}\n".format( gn, " (fat-tailed)" if fat else "" ) )
    f.write( "The game is truncated to {:d} turns.\n".format( trunc ) )
    f.write( "Truncation probability is 1 in {:g}.\n".format(1/probs[-1]) );
    f.write( 'Expectation value {:f}, fee to play {:f}.\n'.format( expect, fee ) );
    f.write( 'Std. dev. {:g}, skewness {:g}, kurtosis {:g}.\n'.format( stddev, skewness, kurt ) );
    f.write( "{:d} runs of {:d} games are played.\n".format(
        numruns, runlength ) )
    f.write( 'Expected payoff per run {:f}.\n'.format( (expect-fee)*runlength ) );
    f.write( 'Random numbers were generated with {:s}.\n'.format(
        "a custom generator" if ownrand else "Python's built-in generator" ) );
    if seed==None:
        f.write( 'The seed was automatically chosen.\n' );
    else:
        f.write( 'The seed was {:d}.\n'.format( seed ) );

    f.write( "\nResults:\n\n" )

    f.write( '{:d} games were terminated by truncation.\n\n'.format(truncations) );
    f.write( 'First downside for player 1:\n'
        '    median: {:f}\n      mean: {:f}\n     worst: {:f}\n'
        '   std dev: {:f}\n  skewness: {:f}\n  kurtosis: {:f}\n\n'.format(
        np.median(firstdownside1),
        np.mean(firstdownside1),
        np.min(firstdownside1),
        np.std(firstdownside1),
        skew(firstdownside1),
        kurtosis(firstdownside1,fisher=False) ) );
    f.write( 'Run-length downside for player 1:\n'
        '    median: {:f}\n      mean: {:f}\n     worst: {:f}\n'
        '   std dev: {:f}\n  skewness: {:f}\n  kurtosis: {:f}\n\n'.format(
        np.median(wholedownside1),
        np.mean(wholedownside1),
        np.min(wholedownside1),
        np.std(wholedownside1),
        skew(wholedownside1),
        kurtosis(wholedownside1,fisher=False) ) );
    f.write( 'First downside for player 2:\n'
        '    median: {:f}\n      mean: {:f}\n     worst: {:f}\n'
        '   std dev: {:f}\n  skewness: {:f}\n  kurtosis: {:f}\n\n'.format(
        np.median(firstdownside2),
        np.mean(firstdownside2),
        np.min(firstdownside2),
        np.std(firstdownside2),
        skew(firstdownside2),
        kurtosis(firstdownside2,fisher=False) ) );
    f.write( 'Run-length downside for player 2:\n'
        '    median: {:f}\n      mean: {:f}\n     worst: {:f}\n'
        '   std dev: {:f}\n  skewness: {:f}\n  kurtosis: {:f}\n\n'.format(
        np.median(wholedownside2),
        np.mean(wholedownside2),
        np.min(wholedownside2),
        np.std(wholedownside2),
        skew(wholedownside2),
        kurtosis(wholedownside2,fisher=False) ) );
    f.write( 'Fraction of runs in profit: {:f}\n'.format( np.sum(cnet[:,-1]>0)/len(cnet) ) );
    f.write( 'Total profit over all runs: {:f}\n'.format( np.sum(cnet[:,-1]) ) );

    m = np.mean( payoffPerRun );
    s = np.std( payoffPerRun );
    f.write( 'Profit per run:\n'
        '      mean: {:f}\n'
        '   std dev: {:f}\n'
        '  std/mean: {:f}\n'
        '  skewness: {:f}\n'
        '  kurtosis: {:f}\n'.format(
        m, s, abs(s/m), skew(payoffPerRun), kurtosis(payoffPerRun,fisher=False) ) );
    f.write( 'Mean payoff per game, excluding fee {:f}\n'.format( m/runlength + fee ) );
    
    if haveFirstPassage:
        numfp = np.sum( fp != -1 )
        fp[ fp==-1 ] = runlength+1
        fp = fp[ fp != -1 ]
        f.write( '\nFirst passage to {:f} in {:d} of {:d} runs:\n'.format(
            firstpassage, numfp, numruns ) );
        f.write( '    mean {:f}\n     std {:f}\n'.format(np.mean( fp ), np.std( fp )) );
        
    if havefilename:
        f.write( "\n\n\n" );
        f.close();

    if plot:
        if haveMatplotlib:
            plotgames( cnet[0:min(100,np.shape(cnet)[0]),:], expect-fee );
            if haveFirstPassage:
                plotfirstpassage( fp )
            plt.show(block=True)
        else:
            print( "To see a plot of some of the games, you need to have the "
                   "matplotlib\n"
                   "module installed. See https://matplotlib.org." )



def plotgames( cnet, v ):
# Plot the first 100 of a set of runs, or however many there are.
# Each run is plotted as a line of a different arbitrary colour.
# Also plot a dashed black line whose gradient is v, the expected profit
# per game.

    numRuns = min(100,np.shape(cnet)[0]);
    pointsPerLine = np.shape(cnet)[1];
    nanrow = np.nan+np.zeros( (1,numRuns) );
    
    t1 = range(pointsPerLine)
    plt.ioff();
    fig, ax = plt.subplots()
    ax.cla;
    
    for i in range(numRuns):
        p = ax.plot( t1, cnet[i,:], linewidth=0.75)



def plotfirstpassage( fp ):
# Plot the first 100 of a set of runs, or however many there are.
# Each run is plotted as a line of a different arbitrary colour.
# Also plot a dashed black line whose gradient is v, the expected profit
# per game.

    plt.ioff();
    fig, ax = plt.subplots()
    ax.cla;
    
    ax.hist( fp , log=True );



def eachPayoff( game, n, fat ):
#[prizes,eprizes,probs] = eachPayoff( game, n )
# For each game truncated to n steps, calculate the payoff made if the game
# ends at any point from 1 to n+1, and the expected value of each payoff,
# i.e. the product of each payoff and the probability that that payoff will
# happen. The n+1'th value of each is zero.
#
# For some games it is simplest to compute the prizes and from them derive
# the expected prizes. For other games the reverse is true.

    nn = np.arange(1,n+1,1,'float64')
    prizes = [];
    eprizes = [];
    if fat:
        probs = 1 / (nn * (nn+1))
    else:
        probs = 2**(-nn);
    
    if game=='stp':
        eprizes = np.ones(n);
    elif game=='astp':
        eprizes = -((-1)**np.arange(1,n+1,1))
    elif game=='pastp':
        h = int( np.floor( (n+1)/2 ) );
        eprizes = np.concatenate( [ -np.ones(h), np.ones(n-h) ] );
    elif game=='cstp':
        prizes = np.arange(1,n+1,1)
    elif game=='acstp':
        prizes = -((-1)**np.arange(1,n+1,1))
    elif game=='dull':
        prizes = np.ones(n);
    elif game=='adull':
        prizes = -((-1)**np.arange(1,n+1,1)) * np.ones(n);
    elif game=='pasa':
        eprizes = -((-1)**nn)/nn;
    elif game=='ppasa':
        eprizes = np.sort( -((-1)**nn)/nn );
    elif game=='alta':
        eprizes = probs - ((-1)**nn)/nn;
    elif game=='palta':
        eprizes = np.sort( -((-1)**nn)/nn );
        prizes = 1 + eprizes / probs;
        eprizes = [];
    elif game=='aix':
        eprizes = -((-2)**nn);
    elif game=='paix':
        eprizes = np.sort( -((-2)**nn) );
    elif game=='pdnk':
        eprizes = 1/(nn**2);
    elif game=='smlv':
        eprizes = 1/(nn**4);
    elif game=='sudd':
        eprizes = np.concatenate([np.zeros(n-1),np.ones(1)])
    
    if np.size(prizes)==0:
        prizes = eprizes / probs;
        prizes[ np.isinf(prizes) ] = 0
    elif np.size(eprizes)==0:
        eprizes = prizes * probs;
        
    prizes = np.concatenate( [prizes, np.zeros(1,'float64')] );
    eprizes = np.concatenate( [eprizes, np.zeros(1,'float64')] );
    truncationProb = 1 - np.sum(probs)
    probs = np.concatenate( [probs, np.zeros(1,'float64') + truncationProb] );
    
    return( (prizes,eprizes,probs) );



def numTurns( probs, runlength, numruns, ownrand ):
    cprobs = np.cumsum(probs);
    n = cprobs.size-1;
    if ownrand:
        a = MT.rand_real( [numruns, runlength] );
    else:
        a = np.random.rand( numruns, runlength );

#    turns = np.ones( [numruns, runlength] );
#    for i in range( cprobs.size-1 ):
#        turns += a >= cprobs[i]
        
        
        
        
        
    turns = np.searchsorted(cprobs, a) + 1
    
#    b = -np.log2( 1-a )
#    c = np.ceil( b )
#    print( "b", b );
#    print( "c", c );
#    turns2 = np.minimum( c, n+1 )
#    turns2 = np.ndarray.astype( turns2, 'int' );
#    print( "turns2", turns2 );

    turns = np.ndarray.astype( turns, 'int' );
    
    return( turns )



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game",
        help="The game to be simulated.", type=str)
    parser.add_argument("-fat",
        dest='fat', action='store_true', default=False,
        help="A flag to use a fat-tailed distribution.")
    parser.add_argument("-trunc",
        help="The time to truncate the game.", type=int, default=16)
    parser.add_argument("-runlength",
        help="The number of games in each run.", type=int, default=1000)
    parser.add_argument("-numruns",
        help="The number of runs.", type=int, default=10000)
    parser.add_argument("-feeratio",
        help="The entry fee as a proportion of expectation.", type=float, default=0.97)
    parser.add_argument("-firstpassage",
        help="Calculate statistics for the first passage to this profit.", type=float, default=1)
    parser.add_argument("-seed",
        help="The random number seed.", type=int)
    parser.add_argument("-output",
        help="The file to write results to.", type=str, default="")
    parser.add_argument('-plot',
        dest='plot', action='store_true', default=False,
        help="Plot some of the games.")
    parser.add_argument('-ownrand',
        dest='ownrand', action='store_true', default=False,
        help="Use the accompanying random number generator.")
    args = parser.parse_args()
    testGames( args.game,
               fat=args.fat,
               trunc=args.trunc,
               runlength=args.runlength,
               numruns=args.numruns,
               feeratio=args.feeratio,
               firstpassage=args.firstpassage,
               seed=args.seed,
               output=args.output,
               plot=args.plot,
               ownrand=args.ownrand )

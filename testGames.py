# See the accompanying file testGames.txt for documentation.
# Written by [redacted], July 2020.

import numpy as np
from scipy.stats import kurtosis
from scipy.stats import skew

import importlib
haveMT = importlib.util.find_spec('MersenneTwister') is not None
if haveMT:
    import MersenneTwister as MT

import argparse
import sys



def testGames( game,
               trunc=16,
               runlength=1000,
               numruns=10000,
               feeratio=0.97,
               seed=None,
               filename="",
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
        'pasa': 'Pasadena',
        'ppasa': 'Permuted Pasadena',
        'alta': 'Altadena',
        'palta': 'Permuted Altadena',
        'aix': 'Aix-to-Ghent',
        'paix': 'Permuted Aix-to-Ghent',
        'sudd': 'Sudden Death' }

    game = game.lower()
    
    if not gamenames.__contains__(game):
        print( "Game {:s} not recognised.\n".format(game) )
        return;
    gn = gamenames[game]
    
    havefilename = filename != ""
    if havefilename:
        f = open( filename, "w" );
    else:
        f = sys.stdout

    [prizes,eprizes,probs] = eachPayoff( game, trunc );
    expect = np.sum(eprizes);
    stddev = np.sqrt( np.sum( (prizes[0:(-1)]**2)*(probs*(1-probs)) ) );
    fee = expect * feeratio;
    
    
    
    if ownrand:
        MT.initialize_generator(seed)
    else:
        np.random.seed( seed )
    
    turns = numTurns( trunc, runlength, numruns, ownrand );
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

    # The "whole downside" is the largest amount either player has lost at
    # any point in a run of RUNLENGTH games.
    wholedownside1 = np.min(cnet,axis=1);
    wholedownside2 = np.max(cnet,axis=1);
    
    payoffPerRun = cnet[:,-1];
    
    np.seterr(divide='ignore')  # We expect to sometimes be dividing by zero.
    

    f.write( "The game {:s} is truncated to {:d} turns,\nand played in runs of "
             "{:d} games, {:d} times over.\n".format(
        gn, trunc, runlength, numruns ) )

    f.write( 'Expectation value {:f}, fee to play {:f}, std.dev. {:g}\n'.format( expect, fee, stddev ) );

    if expect != 0:
        # Calculate (roughly) the number N of games that must be played before the
        # profiting player has a 95% chance of being in profit. This is estimated
        # as the point where the expectation of the series, (expect-fee)*N, is at
        # least equal to twice the standard deviation, 2*stddev*sqrt(N).
        
        numstdclear = 2; # Number of standard deviations of drift required.
        gamesToClear = np.ceil( (stddev/(numstdclear * (expect-fee)))**2 )
        player = 1 if expect>0 else 2
        f.write( '{:.0f} games must be played for player {:d} to have a 95% chance of '
                 'being in profit.\n'.format(gamesToClear,player) );
    
    f.write( '{:d} games were terminated by truncation.\n'.format(truncations) );
    f.write( 'Expectation value {:f}, fee to play {:f}, std.dev. {:g}\n'.format( expect, fee, stddev ) );
#    f.write( 'Long-term number of games {:g}.\n'.format( stddev/(expect-fee) ) );
    f.write( 'First downside for player 1:\n    median: {:f}\n      mean: {:f}\n       max: {:f}\n  skewness: {:f}\n'.format(
        np.median(firstdownside1),
        np.mean(firstdownside1),
        np.min(firstdownside1),
        skew(firstdownside1) ) );
    f.write( 'Run-length downside for player 1:\n    median: {:f}\n      mean: {:f}\n       max: {:f}\n  skewness: {:f}\n'.format(
        np.median(wholedownside1),
        np.mean(wholedownside1),
        np.min(wholedownside1),
        skew(wholedownside1) ) );
    f.write( 'First downside for player 2:\n    median: {:f}\n      mean: {:f}\n       max: {:f}\n  skewness: {:f}\n'.format(
        np.median(firstdownside2),
        np.mean(firstdownside2),
        np.min(firstdownside2),
        skew(firstdownside2) ) );
    f.write( 'Run-length downside for player 2:\n    median: {:f}\n      mean: {:f}\n       max: {:f}\n  skewness: {:f}\n'.format(
        np.median(wholedownside2),
        np.mean(wholedownside2),
        np.min(wholedownside2),
        skew(wholedownside2) ) );
    f.write( 'Fraction of runs in profit: {:f}\n'.format( np.sum(cnet[:,-1]>0)/len(cnet) ) );
    f.write( 'Total profit over all runs: {:f}\n'.format( np.sum(cnet[:,-1]) ) );

    m = np.mean( payoffPerRun );
    s = np.std( payoffPerRun );
    f.write( 'Mean payoff per run {:f}, std {:f}, std/mean {:f}, skewness {:f}\n'.format(
        m, s, abs(s/m), skew(payoffPerRun) ) );
    f.write( 'Expected payoff per run {:f}\n'.format( (expect-fee)*runlength ) );
    
    if havefilename:
        f.close();
    
    if plot:
        plotgames(cnet[0:min(100,np.shape(cnet)[0]),:]);



def plotgames( cnet ):
# Plot the first 100 of a set of runs, or however many there are.
# Each run is plotted as a line of a different arbitrary colour.

    haveMatplotlib = importlib.util.find_spec('matplotlib') is not None
    if haveMatplotlib:
        import matplotlib.pyplot as plt
        import matplotlib.patches
    
        numRuns = min(100,np.shape(cnet)[0]);
        pointsPerLine = np.shape(cnet)[1];
        nanrow = np.nan+np.zeros( (1,numRuns) );
        
        t1 = range(pointsPerLine)
        plt.ioff();
        fig, ax = plt.subplots()
        ax.cla;
        
        for i in range(numRuns):
            p = ax.plot( t1, cnet[i,:], linewidth=0.75 )

        plt.show(block=True)
    else:
        print( "To see a plot of some of the games, you need to have the matplotlib\n"
               "module installed. See https://matplotlib.org." )



def eachPayoff( game, n ):
#[prizes,eprizes,probs] = eachPayoff( game, n )
# For each game truncated to n steps, calculate the payoff made if the game
# ends at any point from 1 to n+1, and the expected value of each payoff,
# i.e. the product of each payoff and the probability that that payoff will
# happen. The n+1'th value of each is zero.
#
# For some games it is simpler to compute the prizes and from them derive
# the expected prizes. For other games the reverse is true.

    nn = np.arange(1,n+1,1,'float64')
    prizes = [];
    eprizes = [];
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
    elif game=='pasa':
        eprizes = -((-1)**nn)/nn;
    elif game=='ppasa':
        eprizes = np.sort( -((-1)**nn)/nn );
    elif game=='alta':
        eprizes = -((-1)**nn)/nn;
        prizes = 1 + eprizes * (2**nn);
        eprizes = [];
    elif game=='palta':
        eprizes = np.sort( -((-1)**nn)/nn );
        prizes = 1 + eprizes * (2**nn);
        eprizes = [];
    elif game=='aix':
        eprizes = -((-2)**nn);
    elif game=='paix':
        nn = np.arange(1,n+1,1)
        eprizes = np.sort( -((-2)**nn) );
    elif game=='sudd':
        eprizes = np.concatenate([np.zeros(n-1),np.ones(1)])
    
    if np.size(prizes)==0:
        prizes = eprizes / probs;
    elif np.size(eprizes)==0:
        eprizes = prizes * probs;
        
    prizes = np.concatenate( [prizes, np.zeros(1)] );
    eprizes = np.concatenate( [eprizes, np.zeros(1)] );
    
    return( (prizes,eprizes,probs) );



def numTurns( n, runlength, numruns, ownrand ):
    if ownrand:
        a = MT.rand_real( [numruns, runlength] );
    else:
        a = np.random.rand( numruns, runlength );
    b = -np.log2( a )
    c = np.ceil( b )
    turns = np.minimum( c, n+1 )
    turns = np.ndarray.astype( turns, 'int' );
    return( turns )



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game",
        help="The game to be simulated.", type=str)
    parser.add_argument("-trunc",
        help="The time to truncate the game.", type=int, default=16)
    parser.add_argument("-runlength",
        help="The number of games in each run.", type=int, default=1000)
    parser.add_argument("-numruns",
        help="The number of runs.", type=int, default=10000)
    parser.add_argument("-feeratio",
        help="The entry fee as a proportion of expectation.", type=float, default=0.97)
    parser.add_argument("-seed",
        help="The random number seed.", type=int)
    parser.add_argument("-filename",
        help="The file to write results to.", type=str, default="")
    parser.add_argument('-plot',
        dest='plot', action='store_true', default=False,
        help="Plot some of the games.")
    parser.add_argument('-ownrand',
        dest='ownrand', action='store_true', default=False,
        help="Use the accompanying random number generator.")
    args = parser.parse_args()
    testGames( args.game,
               trunc=args.trunc,
               runlength=args.runlength,
               numruns=args.numruns,
               feeratio=args.feeratio,
               seed=args.seed,
               filename=args.filename,
               plot=args.plot,
               ownrand=args.ownrand )

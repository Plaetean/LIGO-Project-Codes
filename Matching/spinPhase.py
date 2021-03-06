from pycbc.waveform import get_td_waveform
from pycbc.filter import match
from pycbc.psd import aLIGOZeroDetHighPower
from lalsimulation import SimInspiralTransformPrecessingNewInitialConditions
import matplotlib.pyplot as plt
import numpy as np
import pickle

## Finds the minimum spin difference for the match  between a precessing
## and a non-precessing waveform to drop below 0.95 for a range of phases
## and inclinations

## Computational parameters
match_lim=0.95 # Set limit to distinguish between spinning and non spinning
mass1=55 # Mass of dominant body - this body is whose spin we vary
mass2_low=0 # Upper mass boundary
mass2_high=2*np.pi # Lower mass boundary
spin_resolution=100 # Number of spin values to 'check' for each gridpoint
dimensions=100 # Number of mass and inclination values - grid resolution

## Static parameters
approx="IMRPhenomPv2"
approx1="IMRPhenomPv2"
approx2="IMRPhenomPv2"
f_low = 20
sample_rate = 4096
savename="2D_data/phase_inc_mixed.p"

## Polarisation angle
psi_1=np.pi/4.
psi_2=np.pi/4.

## Spin parameters
phi_JL=0 ## Polarisation angle perhaps?
theta_z1=1.57
theta_z2=0.01
spin_2=0.95
phi12=0 ## Don't know what parameter this is

## Save parameters for the plot axes and future reference
specs=np.array([mass1,match_lim,approx,"Inclination","Spin difference required"])

def match_inc(inc,spin_1,mass2):
   # Allow masses to vary as parameters
   m1_1=mass1
   m2_1=15
   m1_2=mass1
   m2_2=15
   
   # Phases
   phase1=mass2
   phase2=mass2
   # Convert to precessing coords
   inc_1,s1x,s1y,s1z,s2x,s2y,s2z=SimInspiralTransformPrecessingNewInitialConditions(
                         inc, #theta_JN
                         phi_JL, #phi_JL
                         theta_z1, #theta1
                         theta_z2, #theta2
                         phi12, #phi12
                         spin_1, #chi1 - this parameter varies
                         spin_2, #chi2
                         m1_1,
                         m2_1,
                         f_low,phiRef=0)

   #This is our 'spin1=0' waveform that we match the precessing one with
   inc_2,s1x_2,s1y_2,s1z_2,s2x_2,s2y_2,s2z_2=SimInspiralTransformPrecessingNewInitialConditions(
                         inc, #theta_JN
                         phi_JL, #phi_JL
                         theta_z1, #theta1
                         theta_z2, #theta2
                         phi12, #phi12
                         0, #chi1
                         spin_2, #chi2
                         m1_2,
                         m2_2,
                         f_low,phiRef=0)

   # Generate the two waveforms to compare
   hp, hc = get_td_waveform(approximant=approx1,
                         mass1=m1_1,
                         mass2=m2_1,
                         spin1y=s1y,spin1x=s1x,spin1z=s1z,
                         spin2y=s2y,spin2x=s2x,spin2z=s2z,
                         f_lower=f_low,inclination=inc_1,
                         coa_phase=phase1,
                         delta_t=1.0/sample_rate)
   sp, sc = get_td_waveform(approximant=approx2,
                         mass1=m1_2,
                         mass2=m2_2,
                         spin1y=s1y_2,spin1x=s1x_2,spin1z=s1z_2,
                         spin2y=s2y_2,spin2x=s2x_2,spin2z=s2z_2,
                         f_lower=f_low,inclination=inc_2,
                         coa_phase=phase2,
                         delta_t=1.0/sample_rate)
   # Add polarisation mixing
   h=hp*np.cos(2*psi_1)+hc*np.sin(2*psi_1)
   s=sp*np.cos(2*psi_2)+sc*np.sin(2*psi_2)

   # Resize the waveforms to the same length
   tlen = max(len(s), len(h))
   s.resize(tlen)
   h.resize(tlen)
   # Generate the aLIGO ZDHP PSD
   delta_f = 1.0 / s.duration
   flen = tlen/2 + 1
   psd = aLIGOZeroDetHighPower(flen, delta_f, f_low)
   # Note: This takes a while the first time as an FFT plan is generated
   # subsequent calls are much faster.
   m, i = match(h, s, psd=psd, low_frequency_cutoff=f_low)
   #print 'The match is: %1.3f' % m
   return m


# For a mass value, find the minimum spin difference required to distinguish
# between precessing and non-precessing waveforms for ALL inclinations
def findMatchLimit(mass2,inc,spin1):
  matchVals=np.zeros(dimensions)
  for aa in range(len(inc)):
    match=1
    bb=0
    while (match > match_lim) and (bb < (len(spin1)-2)):
      #print spin1[bb]
      #print inc[aa]
      match=match_inc(inc[aa],spin1[bb],mass2)
      bb=bb+1
    matchVals[aa]=spin1[bb]
  return matchVals

# This function takes a range of mass values, and for each mass value
# it runs through inclinations 0 to 2pi, and for each inclination
# finds the minimum spin necessary for the match between spinning and
# non-spinning waveforms to be lower than a critical limit defined above
def spinLimit(inc,spin1,mass2Values):
  mass2Values=np.linspace(mass2_low,mass2_high,dimensions)
  matchGrid=np.zeros((dimensions,dimensions)) #Generate 2D grid array
  for aa in range(dimensions):
    perc=(float(aa)/dimensions)*100
    match_1D_array=findMatchLimit(mass2Values[aa],inc,spin1) #For each mass value, find array of matches
    print "We are %1.2f%% complete" % perc
    for bb in range(dimensions):
      matchGrid[aa][bb]=match_1D_array[bb]    # Stack these matches up into a 2D grid, one row at a time
  return matchGrid

#Parameter arrays
inc=np.linspace(0,3.14159,dimensions)
spin1=np.linspace(0,0.999,spin_resolution)
mass2Values=np.linspace(mass2_low,mass2_high,dimensions)

#Run everything and generate data
final=spinLimit(inc,spin1,mass2Values)

#Prepare data for savings
data=list([0,0,0,0])
data[0]=inc # x axis
data[1]=mass2Values # y axis
data[2]=final
data[3]=specs
pickle.dump(data,open("%s" % savename,"wb"))
print "Data saved as %s" % savename

print "DONE"

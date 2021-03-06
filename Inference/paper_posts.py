#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pycbc.io import InferenceFile
import sys
from lalsimulation import SimInspiralTransformPrecessingNewInitialConditions
from pycbc.waveform import get_td_waveform

print "Initialising..."

## Select file
run=sys.argv[1]
folder="final/"+run+"/"

## Combine inputs to form variables
data_name="output.hdf"

## Determine what parameters to plot

## List of parameters
params=np.array(["q",
		"mchirp",
		"distance",
		"inclination",
		"polarization",
                "mass1",
                "mass2",
                "chi_p",
                "chi_eff",
                "ra",
                "dec",
                "phase"])

## Load in dictionary
dic_name="paramDict.npy"
dict_load=folder+dic_name
injected=np.load("%s" % dict_load).item()
num_walkers=int(injected["n_walkers"])
num_its=int(injected["n_its"])

## Function to extract posterior for a given parameter
def getParameter(parameter):
   ## Prepare to read in parameters
   datafile=folder+data_name
   fp = InferenceFile("%s" % datafile, "r")
   
   ## Take last iteration of each walker
   parameter_values=np.array([])
   for aa in range(num_walkers):
      samples = fp.read_samples("%s" % parameter, walkers=aa)
      temp=getattr(samples,parameter)
      parameter_values=np.append(parameter_values,temp[-1])
   return parameter_values


def chi_effect():
   ## chi_eff is given by (S1/m1+S2/m2) dot L/M where M is total mass
   ## So for this we need m1, m2, s1_a, s2_a, s1_polar, s2_polar... fak me
   chi_eff=np.zeros(num_walkers)
   print "   Extracting intrinsic parameters..."
   ## Generate arrays for each paramter
   s1_a=getParameter("spin1_a")
   s1_polar=getParameter("spin1_polar")
   s2_a=getParameter("spin2_a")
   s2_polar=getParameter("spin2_polar")
   m1=getParameter("mass1")
   m2=getParameter("mass2")
   M=m1+m2
   
   ## Find spins along z-axis
   s1_z=m1*m1*s1_a*np.cos(s1_polar)
   s2_z=m2*m2*s2_a*np.cos(s2_polar)

   print "   Calculating derived parameters..."
   chi_eff=(s1_z/m1+s2_z/m2)/M
   return chi_eff

def chi_prec():
   ## chi_p is given by (1/B1m1^2)*max(B1*S1perp,B2*S2perp)
   ## with B1=2+3/2q, B2=2+3q/2
   ## so we need m1, q, s1_a, s1_polar, s2_a, s2_polar
   ## NB chi_p should always be 0 < chi_p < 1
   chi_p=np.zeros(num_walkers)
   print "   Extracting intrinsic parameters..."
   ## Generate arrays for each parameter
   s1_a=getParameter("spin1_a")
   s1_polar=getParameter("spin1_polar")
   s2_a=getParameter("spin2_a")
   s2_polar=getParameter("spin2_polar")
   mass1=getParameter("mass1")
   mass2=getParameter("mass2")
   print "   Calculating derived parameters..."
   for aa in range(len(mass1)):  ## Standard chi_p function]
      if mass1[aa]>mass2[aa]:
         ratio=mass2[aa]/mass1[aa]
         B1=2+((3*ratio)/2)
         B2=2+(3/(ratio*2))
         spin1_plane=s1_a[aa]*np.sin(s1_polar[aa])
         spin2_plane=s2_a[aa]*np.sin(s2_polar[aa])
         arg1=B1*spin1_plane*mass1[aa]*mass1[aa]
         arg2=B2*spin2_plane*mass2[aa]*mass2[aa]
         chi_p[aa]=(max(arg1,arg2))/(mass1[aa]*mass1[aa]*B1)
      else:
         ratio=mass2[aa]/mass1[aa] # Modify function for inverted mass ratio
         B1=2+((3*ratio)/2)
         B2=2+(3/(ratio*2))
         spin1_plane=s1_a[aa]*np.sin(s1_polar[aa]) # Spin1 is smaller mass this time!
         spin2_plane=s2_a[aa]*np.sin(s2_polar[aa]) # Spin2 is larger mass this time!
         arg1=B1*spin1_plane*mass1[aa]*mass1[aa]   # Swap the B coefficients now as B1 should be on the larger mass
         arg2=B2*spin2_plane*mass2[aa]*mass2[aa]
         chi_p[aa]=(max(arg1,arg2))/(mass2[aa]*mass2[aa]*B2)
   return chi_p

## Function to plot the injected waveform in time domain
def plot_injected():
   ## Not worrying about azimuthal angles as they are irrelevant
   s1z=injected["spin1_a"]*np.cos(injected["spin1_polar"])
   s1x=injected["spin1_a"]*np.sin(injected["spin1_polar"])
   s2z=injected["spin2_a"]*np.cos(injected["spin2_polar"])
   s2x=injected["spin2_a"]*np.sin(injected["spin2_polar"])
   sample_rate = 4096 # Sampling frequency
   hp, hc = get_td_waveform(approximant="IMRPhenomPv2",
                      mass1=injected["mass1"],
                      mass2=injected["mass2"],
                      spin1y=0,spin1x=s1x,spin1z=s1z,
                      spin2y=0,spin2x=s2x,spin2z=s2z,
                      f_lower=injected["f_min"],
                      inclination=injected["inclination"],
                      distance=injected["distance"],
                      ra=injected["ra"],
                      dec=injected["dec"],
                      delta_t=1.0/sample_rate,
                      coa_phase=1.5)
   

   ## Mix polarisations according to polarisation angle
   psi=injected["polarization"]
   h_obs=hp*np.cos(2*psi)+hc*np.sin(2*psi)
   plt.figure()
   plt.plot(hp.sample_times,h_obs)
   plt.xlabel("Time (s)")
   plt.ylabel("Strain")
   plt.title("Injected waveform using IMRPhenomPv2")
   plt.xlim(-0.15,0.05)
   savename=folder+"injected_clean"
   plt.savefig("%s.png" % savename)
   print "Saved plot of injected waveform as %s" % savename

## Extract parameter and plot posterior
def plotPosterior(parameter):

   if parameter=="mchirp":
      ## Find chirp mass
      m1=getParameter("mass1")
      m2=getParameter("mass2")
      M=m1+m2
      parameter_values=((m1*m2)**(3./5.))/(M**(1./5.))

      ## Injected parameter
      m1_inj=injected["mass1"]
      m2_inj=injected["mass2"]
      M_inj=m1_inj+m2_inj
      injected_value=((m1_inj*m2_inj)**(3./5.))/(M_inj**(1./5.))

   elif parameter=="chi_eff":
      parameter_values=chi_effect()

      ## Find injected value
      m2=injected["mass2"]
      m1=injected["mass1"]
      s1a=injected["spin1_a"]
      s2a=injected["spin2_a"]
      s1_polar=injected["spin1_polar"]
      s2_polar=injected["spin2_polar"]
      s1z=m1*m1*s1a*np.cos(s1_polar)
      s2z=m2*m2*s2a*np.cos(s2_polar)
      chi_eff=(s1z/m1+s2z/m2)/(m1+m2)
      injected_value=chi_eff

   elif parameter=="chi_p":
      parameter_values=chi_prec()
      ## Derive injected value
      m1=injected["mass1"]
      m2=injected["mass1"]
      s1a=injected["spin1_a"]
      s2a=injected["spin2_a"]
      s1_polar=injected["spin1_polar"]
      s2_polar=injected["spin2_polar"]
      s1_per=m1*m1*s1a*np.sin(s1_polar)
      s2_per=m2*m2*s2a*np.sin(s2_polar)
      q=m2/m1

      ## Find Bs
      B1=2.+((q*3.)/2.)
      B2=2.+(3./(2.*q))
      
      chi_p=(1./(B1*m1*m1))*max((B1*s1_per,B2*s2_per))
      injected_value=chi_p

   elif parameter=="q":
      mass1=getParameter("mass1")
      mass2=getParameter("mass2")
      q=np.zeros(len(mass1))
 
      for aa in range(len(mass1)): ## Have to ensure 0<q<1 by making sure the larger mass is the denom
         q[aa]=min((mass1[aa]/mass2[aa]),(mass2[aa]/mass1[aa]))

      parameter_values=q
      ## Injected value
      injected_value=injected["mass2"]/injected["mass1"]

   ## Ensure m1>m2 in posteriors
   elif parameter=="mass1":
      mass1=getParameter("mass1")
      mass2=getParameter("mass2")
      parameter_values=np.zeros(len(mass1))
      for aa in range(len(mass1)):
         parameter_values[aa]=max(mass1[aa],mass2[aa])
      injected_value=max(injected["mass1"],injected["mass2"])
 
   ## Ensure m2>m1 in posteriors
   elif parameter=="mass2":
      mass1=getParameter("mass1")
      mass2=getParameter("mass2")
      parameter_values=np.zeros(len(mass1))
      for aa in range(len(mass1)):
         parameter_values[aa]=min(mass1[aa],mass2[aa])
      injected_value=min(injected["mass1"],injected["mass2"])

   elif parameter=="phase":
      parameter_values=getParameter("coa_phase")
      values=len(parameter_values)
      injected_value=injected[parameter]

   else:
      parameter_values=getParameter(parameter)
      values=len(parameter_values)
      injected_value=injected[parameter]

   savename=folder+parameter   
   values=len(parameter_values)
   ## Find confidence intervals
   parameter_values=np.sort(parameter_values)
   lower_90=parameter_values[250]
   upper_90=parameter_values[4749]
   mean_val=np.average(parameter_values)
   
   ## Plot and save
   plt.hist(parameter_values,50, normed=True, alpha=0.9)
   plt.axvline(x=injected_value,linewidth=2,color='r')
   plt.axvline(x=lower_90,linewidth=2,linestyle='dashed',color='k')
   plt.axvline(x=mean_val,linewidth=2, color='k')
   plt.axvline(x=upper_90,linewidth=2,linestyle='dashed',color='k')
   plt.xlabel("%s" % parameter)
   ## Plot priors for derived spin parameters
   if parameter=="chi_p":
      prior=np.loadtxt("priors/chi_p_prior.txt")
      plt.hist(prior,50,normed=True,alpha=0.6)
      plt.xlabel(r'$\chi_p$')
   elif parameter=="chi_eff":
      prior=np.loadtxt("priors/chi_eff_prior.txt")
      plt.hist(prior,50,normed=True,alpha=0.6)
      plt.xlabel(r'$\chi_{eff}$')
   print "  --%s added" % parameter

plt.figure(figsize=(6,7))
## Plot loop
for aa in range(1,13):
   plt.subplot(4,3,aa)
   plotPosterior(params[aa-1])
plt.tight_layout()
plt.savefig("figures/%s_fullpost.png" % run)
plt.show("hold")

print "DONE"

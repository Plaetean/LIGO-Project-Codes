import matplotlib.pyplot as plt
from pycbc.waveform import get_td_waveform
inc=1.56
apx="IMRPhenomPv2"
hp, hc = get_td_waveform(approximant=apx,inclination=inc,
                                 mass1=30,
                                 mass2=10,
                                 spin1z=0.0,
                                 spin1x=0.2,
                                 delta_t=1.0/4096,
                                 f_lower=20)


sp, sc = get_td_waveform(approximant=apx,inclination=inc,
                                 mass1=30,
                                 mass2=10,
                                 spin1x=0.55,
                                 spin1z=0.0,
                                 delta_t=1.0/4096,
                                 f_lower=20)


gp, gc = get_td_waveform(approximant=apx,inclination=inc,
                                 mass1=30,
                                 mass2=10,
                                 spin1x=0.98,
                                 spin1z=0.0,
                                 delta_t=1.0/4096,
                                 f_lower=20)


lowlim=-2.45
plt.figure()
plt.subplot(3,1,1)
plt.title("Comparison of weak and heavy precession")
plt.plot(hp.sample_times, hp, label="In-plane spin=0.1")
plt.ylabel('Strain')
plt.xlim(lowlim,hp.sample_times[-1])
plt.legend(loc="best")
plt.subplot(3,1,2)
plt.plot(sp.sample_times, sp, label="In-plane spin=0.5")
plt.ylabel('Strain')
plt.legend(loc="best")
plt.xlim(lowlim,hp.sample_times[-1])
plt.subplot(3,1,3)
plt.plot(gp.sample_times, gp, label="In-plane spin=0.98")
plt.xlabel('Time (s)')
plt.ylabel('Strain')
plt.legend(loc="best")
plt.xlim(lowlim,hp.sample_times[-1])
plt.show("hold")
plt.savefig("precessfig")

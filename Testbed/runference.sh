# Create new directory for this inference run
NAMEDIR=`date '+%Y%m%d-%H%M%S'`
mkdir ${NAMEDIR}
PAR=${NAMEDIR}/parameters.txt
TEMPPAR=${NAMEDIR}/temp_par.txt

# define coalescence time, observed masses, and waveform parameters
TRIGGER_TIME=1126259462.0
INJ_APPROX=IMRPhenomPv2threePointFivePN
MASS1=67.
MASS2=25.
RA=2.21535724066
DEC=-1.23649695537
INC=1.62
COA_PHASE=1.5
POLARIZATION=1.75
DISTANCE=100000 # in kpc
INJ_F_MIN=28.
TAPER="start"

# Spin parameters
MIN_SPIN1=0.9
MAX_SPIN1=0.9
MIN_KAPPA1=0.0
MAX_KAPPA1=0.0
MIN_SPIN2=0.0
MAX_SPIN2=0.0
MIN_KAPPA2=0.9
MAX_KAPPA2=0.9

# path of injection file that will be created in the example
INJ_PATH=${NAMEDIR}/injection.xml.gz

# lalapps_inspinj requires degrees on the command line
LONGITUDE=`python -c "import numpy; print ${RA} * 180/numpy.pi"`
LATITUDE=`python -c "import numpy; print ${DEC} * 180/numpy.pi"`
INC_inj=`python -c "import numpy; print ${INC} * 180/numpy.pi"`
POLARIZATION_inj=`python -c "import numpy; print ${POLARIZATION} * 180/numpy.pi"`
COA_PHASE_inj=`python -c "import numpy; print ${COA_PHASE} * 180/numpy.pi"`

# sampler parameters
OUTPUT=${NAMEDIR}/output.hdf
SEGLEN=8
PSD_INVERSE_LENGTH=4
IFOS="H1 L1 V1"
STRAIN="H1:aLIGOZeroDetHighPower L1:aLIGOZeroDetHighPower V1:aLIGOZeroDetHighPower"
SAMPLE_RATE=2048
F_MIN=30.
N_WALKERS=5000
N_ITERATIONS=10000
N_CHECKPOINT=1000
PROCESSING_SCHEME=cpu
NPROCS=12
CONFIG_PATH=inference.ini

# get coalescence time as an integer
TRIGGER_TIME_INT=${TRIGGER_TIME%.*}

# start and end time of data to read in
GPS_START_TIME=$((${TRIGGER_TIME_INT} - ${SEGLEN}))
GPS_END_TIME=$((${TRIGGER_TIME_INT} + ${SEGLEN}))

# create injection file
lalapps_inspinj \
    --output ${INJ_PATH} \
    --seed 1000 \
    --f-lower ${INJ_F_MIN} \
    --waveform ${INJ_APPROX} \
    --amp-order 7 \
    --gps-start-time ${TRIGGER_TIME} \
    --gps-end-time ${TRIGGER_TIME} \
    --time-step 1 \
    --t-distr fixed \
    --l-distr fixed \
    --longitude ${LONGITUDE} \
    --latitude ${LATITUDE} \
    --d-distr uniform \
    --min-distance ${DISTANCE} \
    --max-distance ${DISTANCE} \
    --i-distr fixed \
    --fixed-inc ${INC} \
    --coa-phase-distr fixed \
    --fixed-coa-phase ${COA_PHASE} \
    --polarization ${POLARIZATION} \
    --m-distr fixMasses \
    --fixed-mass1 ${MASS1} \
    --fixed-mass2 ${MASS2} \
    --taper-injection ${TAPER} \
    --enable-spin \
    --min-spin1 ${MIN_SPIN1} \
    --max-spin1 ${MAX_SPIN1} \
    --min-spin2 ${MIN_SPIN2} \
    --max-spin2 ${MAX_SPIN2} \
    --min-kappa1 ${MIN_KAPPA2} \
    --max-kappa1 ${MAX_KAPPA2} \

# Output parameters as text file
printf "Injection approximant = ${INJ_APPROX} \n" > ${PAR}
printf "Trigger time = ${TRIGGER_TIME} \n" >> ${PAR}
printf "Mass 1 = ${MASS1} \n" >> ${PAR}
printf "Mass 2 = ${MASS2} \n" >> ${PAR}
printf "RA = ${RA} \n" >> ${PAR}
printf "Declination = ${DEC} \n" >> ${PAR}
printf "Inclination (degrees now) = ${INC} \n" >> ${PAR}
printf "Phase = ${COA_PHASE} \n" >> ${PAR}
printf "Polarisation = ${POLARIZATION} \n" >> ${PAR}
printf "Distance (kpc) = ${DISTANCE} \n" >> ${PAR}
printf "Minimum frequency = ${INJ_F_MIN} \n" >> ${PAR}
printf " \nSpin parameters: \n" >> ${PAR}
printf "Spin1 min = ${MIN_SPIN1} \n" >> ${PAR}
printf "Spin1 max = ${MAX_SPIN1} \n" >> ${PAR}
printf "Spin1 min kappa = ${MIN_KAPPA1} \n" >> ${PAR}
printf "Spin1 max kappa = ${MAX_KAPPA1} \n" >> ${PAR}
printf "Spin2 min = ${MIN_SPIN2} \n" >> ${PAR}
printf "Spin2 max = ${MAX_SPIN2} \n" >> ${PAR}
printf "Spin2 min kappa = ${MIN_KAPPA2} \n" >> ${PAR}
printf "Spin2 max kappa = ${MAX_KAPPA2} \n" >> ${PAR}
printf " \nSampler parameters: \n" >> ${PAR}
printf "Number of walkers = ${N_WALKERS} \n" >> ${PAR}
printf "Number of checkpoints = ${N_CHECKPOINT} \n" >> ${PAR}
printf "Number of iterations = ${N_ITERATIONS} \n" >> ${PAR}
printf "Number of processors = ${NPROCS} \n" >> ${PAR}
printf " \nOther parameters> \n" >> ${PAR}
printf "Detectors = ${IFOS} \n" >> ${PAR}
printf "Strain = ${STRAIN} \n" >> ${PAR}

# Write to temporary file
printf "${INJ_APPROX} \n" > ${TEMPPAR}
printf "${MASS1} \n" >> ${TEMPPAR}
printf "${MASS2} \n" >> ${TEMPPAR}
printf "${RA} \n" >> ${TEMPPAR}
printf "%f \n" ${DEC} >> ${TEMPPAR}
printf "${INC} \n" >> ${TEMPPAR}
printf "${COA_PHASE} \n" >> ${TEMPPAR}
printf "${POLARIZATION} \n" >> ${TEMPPAR}
printf "${DISTANCE} \n" >> ${TEMPPAR}
printf "${MIN_SPIN1} \n" >> ${TEMPPAR}
printf "${MAX_SPIN1} \n" >> ${TEMPPAR}
printf "${MIN_KAPPA1} \n" >> ${TEMPPAR}
printf "${MAX_KAPPA1} \n" >> ${TEMPPAR}
printf "${MIN_SPIN2} \n" >> ${TEMPPAR}
printf "${MAX_SPIN2} \n" >> ${TEMPPAR}
printf "${MIN_KAPPA2} \n" >> ${TEMPPAR}
printf "${MAX_KAPPA2} \n" >> ${TEMPPAR}
printf "${N_WALKERS} \n" >> ${TEMPPAR}
printf "${N_ITERATIONS} \n" >> ${TEMPPAR}
#printf "${IFOS} \n" >> ${TEMPPAR}  ----- this is not working, cannot be parsed

# Convert temporary file into dictionary and write
python conv2Dict.py ${NAMEDIR}

#Delete temporary file
rm ${TEMPPAR}

# run sampler
# specifies the number of threads for OpenMP
# Running with OMP_NUM_THREADS=1 stops lalsimulation
# to spawn multiple jobs that would otherwise be used
# run sampler
# specifies the number of threads for OpenMP
# Running with OMP_NUM_THREADS=1 stops lalsimulation
# to spawn multiple jobs that would otherwise be used
# by pycbc_inference and cause a reduced runtime.
OMP_NUM_THREADS=1 \
pycbc_inference --verbose \
    --skip-burn-in \
    --update-interval 500 \
    --instruments ${IFOS} \
    --gps-start-time ${GPS_START_TIME} \
    --gps-end-time ${GPS_END_TIME} \
    --psd-model ${STRAIN} \
    --psd-inverse-length ${PSD_INVERSE_LENGTH} \
    --fake-strain ${STRAIN} \
    --sample-rate ${SAMPLE_RATE} \
    --low-frequency-cutoff ${F_MIN} \
    --channel-name H1:FOOBAR V1:FOOBAR L1:FOOBAR \
    --injection-file ${INJ_PATH} \
    --processing-scheme ${PROCESSING_SCHEME} \
    --sampler kombine \
    --likelihood-evaluator gaussian \
    --nwalkers ${N_WALKERS} \
    --niterations ${N_ITERATIONS} \
    --config-file ${CONFIG_PATH} \
    --output-file ${OUTPUT} \
    --checkpoint-interval ${N_CHECKPOINT} \
    --checkpoint-fast \
    --nprocesses ${NPROCS}


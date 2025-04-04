#!/bin/bash
#
#  usage: $0 [ --PU ] [ --events N ] job  /store/path/output_file.root 
#
TMPDIR=$PWD
#### ENV
SRC=$1; shift
CMSSWMINI=$1; shift
CMSSWNANO=$1; shift
#STEP4=Run24_140X_step4Mini_cfg.py
STEP4=Run24_140X_step4Mini_1502_cfg.py
STEP5=Run24_140X_step5Nano_1502_JMENano_cfg.py

FIRSTLUMI=1000

FILESPY=$1
shift;

ISLHE=true

echo $LHESRC

if [[ "$1" == "--events" ]]; then
    EVNUM=$2; shift; shift;
fi;

JOB=$1
shift;

OUTFILE=$1

OUTBASE=$(basename $OUTFILE .root)
echo "Will write to $OUTFILE";
shift;

## Create output directories
OUTDIR=/eos/cms$(dirname $OUTFILE)
eos ls $OUTDIR || eos mkdir -p $OUTDIR

### ENVIRONMENT STEP
cd $SRC/$CMSSWMINI; 
export SCRAM_ARCH=el8_amd64_gcc12
if [[ "$LD_LIBRARY_PATH" == "" ]] ; then
    CMSSW_BASE_VERSION=${CMSSW_VERSION%_patch*}
    if [[ "$CMSSW_BASE_VERSION" != "$CMSSW_VERSION" ]]; then # patch release
        export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/cmssw-patch/${CMSSW_VERSION}/external/${SCRAM_ARCH}/lib ;
    else
        export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/cmssw/${CMSSW_VERSION}/external/${SCRAM_ARCH}/lib ;
    fi;
fi
eval $(scramv1 runtime -sh)
cd $TMPDIR;

echo "All the parameters"
echo $FILESPY
echo $SRC
echo $CMSSWMINI
echo $OUTBASE
echo $OUTDIR
echo $JOB
echo $OUTFILE
echo $EVNUM
echo $FIRSTLUMI


echo "Step MINIAOD"

cat $SRC/$STEP4 > $OUTBASE.step4_cfg.py
echo -n "process.source.fileNames = " >> $OUTBASE.step4_cfg.py
sed -n '/^files = \[/,/\]/p' "$SRC/$FILESPY" | sed 's/^files = //' >> $OUTBASE.step4_cfg.py
#grep -v "^files =" "$FILESPY" >> "$OUTBASE.step4_cfg.py"

cat >> $OUTBASE.step4_cfg.py <<_EOF_
## Input and output
process.maxEvents.input = cms.untracked.int32($EVNUM)
process.source.skipEvents = cms.untracked.uint32($JOB*$EVNUM)
## Scramble
import random
rnd = random.SystemRandom()
for X in process.RandomNumberGeneratorService.parameterNames_(): 
    if X != 'saveFileName': getattr(process.RandomNumberGeneratorService,X).initialSeed = rnd.randint(1,99999999)
_EOF_
cp $OUTBASE.step4_cfg.py $SRC/ciaociaomini.py
cmsRun $OUTBASE.step4_cfg.py 
STEP4OUT=step4.root
test -f $TMPDIR/${STEP4OUT}  || exit 41
edmFileUtil --ls file:$TMPDIR/${STEP4OUT} | grep events        || exit 42
edmFileUtil --ls file:$TMPDIR/${STEP4OUT} | grep ', 0 events'  && exit 43

echo "Step 4 MINIAOD finished"


cd $SRC/$CMSSWNANO; 
export SCRAM_ARCH=el8_amd64_gcc12
if [[ "$LD_LIBRARY_PATH" == "" ]] ; then
    CMSSW_BASE_VERSION=${CMSSW_VERSION%_patch*}
    if [[ "$CMSSW_BASE_VERSION" != "$CMSSW_VERSION" ]]; then # patch release
        export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/cmssw-patch/${CMSSW_VERSION}/external/${SCRAM_ARCH}/lib ;
    else
        export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/cmssw/${CMSSW_VERSION}/external/${SCRAM_ARCH}/lib ;
    fi;
fi
eval $(scramv1 runtime -sh)
cd $TMPDIR;

echo "Moving to step 5"
cat $SRC/$STEP5 > $TMPDIR/$OUTBASE.step5_cfg.py
cat >> $OUTBASE.step5_cfg.py <<_EOF_
## Input and output
process.source.fileNames = [ 'file:${STEP4OUT}' ]
import random
rnd = random.SystemRandom()
for X in process.RandomNumberGeneratorService.parameterNames_(): 
    if X != 'saveFileName': getattr(process.RandomNumberGeneratorService,X).initialSeed = rnd.randint(1,99999999)
_EOF_

cmsRun $OUTBASE.step5_cfg.py 
STEP5OUT=step5.root
echo "NanoAODs"
ls $TMPDIR/${STEP5OUT}
test -f $TMPDIR/${STEP5OUT}  || exit 51
edmFileUtil --ls file:$TMPDIR/${STEP5OUT} | grep events        || exit 52
edmFileUtil --ls file:$TMPDIR/${STEP5OUT} | grep ', 0 events'  && exit 53

echo "making directory /eos/cms/${OUTFILE}/Nano"

mkdir -p /eos/cms/${OUTFILE}/Nano
ls /eos/cms/${OUTFILE}/

cp ${STEP5OUT} /eos/cms/${OUTFILE}/Nano/job_${JOB}_${STEP5OUT}
echo "copied ${STEP5OUT} into /eos/cms/${OUTFILE}/Nano/job_${JOB}_${STEP5OUT}"



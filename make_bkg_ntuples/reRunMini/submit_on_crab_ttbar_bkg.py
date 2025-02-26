from CRABClient.UserUtilities import config, ClientException
import yaml
import datetime
from fnmatch import fnmatch
from argparse import ArgumentParser

production_tag = datetime.date.today().strftime('%Y%b%d')

config = config()
config.section_('General')
config.General.transferOutputs = True
config.General.transferLogs = True
config.General.workArea = 'crab_jobs/TTtoLNu2Q_RunIII2024Summer24DRPremix-140X_%s' % production_tag

config.section_('Data')
config.Data.publication = False
config.Data.outLFNDirBase = '/store/group/cmst3/group/softJets/friti/bkg_ntuples_2024/ttbar_bkg/miniaod_%s' % ('TTtoLNu2Q_RunIII2024Summer24DRPremix-140X_' + production_tag)
config.Data.inputDBS = 'global'

config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'tt_bkg_miniaodstep_cfg.py'
config.Data.partialDataset = True
#config.JobType.scriptExe = 'crab_script.sh'
#config.JobType.maxJobRuntimeMin = 3000
#config.JobType.allowUndistributedCMSSW = True
#config.Data.allowNonValidInputDataset = True
#config.JobType.numCores = 4
config.JobType.maxMemoryMB = 5000
#config.JobType.maxMemoryMB = 3000
config.section_('User')
config.section_('Site')
config.Site.storageSite = 'T2_CH_CERN'
config.Data.partialDataset = True

if __name__ == '__main__':

  from CRABAPI.RawCommand import crabCommand
  from CRABClient.ClientExceptions import ClientException
  from multiprocessing import Process

  def submit(config):
          crabCommand('submit', config = config)



config.Data.inputDataset = '/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24DRPremix-140X_mcRun3_2024_realistic_v26-v2/AODSIM'
config.General.requestName = 'ttbar'
config.Data.splitting = 'FileBased' 
config.Data.unitsPerJob = 4
globaltag = '140X_mcRun3_2024_realistic_v26'
                
config.JobType.outputFiles = ['tt_miniaod.root']
        
print(config)
submit(config)

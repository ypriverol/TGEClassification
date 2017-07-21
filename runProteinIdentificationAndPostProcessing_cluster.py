## This python code run MSGF+ and mzidenML-lib i.e. protein identification and post-process the result

import argparse
from subprocess import Popen, PIPE
#import subprocess as sp
import os

parser = argparse.ArgumentParser(description='This python code run MSGF+ and mzidenML-lib i.e. protein identification and post-process the result')
parser.add_argument("-i", "--input", nargs=1, required=True, help="full path of mgf file", metavar="PATH")
parser.add_argument("-o", "--output", nargs=1, required=True, help="full path of of output file", metavar="PATH")
parser.add_argument("-d", "--database", nargs=1, required=True, help="full path to the database file", metavar="PATH")
parser.add_argument("-m","--modification", nargs=1, required=True, help="full path to the modification file", metavar="PATH")
parser.add_argument("-t", "--tolerance", default=["10ppm"], help="mass tolerance")
#parser.add_option("--tda", help="whether to create decoy database", metavar="Integer")
parser.add_argument("--m_msgf", default=['1'], help="", metavar="Integer")
parser.add_argument("--inst", default=['1'],help="Instrument")
parser.add_argument("--minLength", default=['8'], help="minimum peptide length", metavar="LENGTH")
parser.add_argument("--tda", default=['1'],help="Decoy database search tda 0/1(default)")

parser.add_argument("--msgf_path", default=[""],help="msgf+ jar file location", metavar="PATH")
parser.add_argument("--mzident_path", default=[""],help="mzidentml-lib jarfile location", metavar="PATH")
parser.add_argument("--contaminants", default=["crap.fasta"],help="Decoy database search tda 0/1(default)")

#parser.add_option("--min3", help="the minimum length of 3' uORFs, only works when -uorf3output is set", metavar="Integer")

args = parser.parse_args()
#print(args)

contaminants=args.contaminants[0]

#p=Popen(["python3.4","merge_fasta_file.py", args.database[0], contaminants,  args.database[0]+".cont.fasta"],stdout=PIPE)
#p=sp.call(["python3.4","merge_fasta_file.py", args.database[0], contaminants,  args.database[0]+".cont.fasta"])
#p.wait()
#outMsg = p.communicate()[0]
#print(p.returncode)

##Temporariliy commented out
os.system("python3.4 merge_fasta_file.py "+args.database[0]+" "+contaminants+" "+args.database[0]+".cont.fasta")


#directoryMSG=sp.check_output(["cd",args.msgf_path], shell=True, stderr=sp.STDOUT)
os.chdir(args.msgf_path[0])
#print("current dir:")
#print(os.getcwd())

###Printing this to the out file allows to run the out file as a shell script.
print("#!/bin/sh")
print("#$ -cwd              # Set the working directory for the job to the current directory")
print("#$ -V")
print("#$ -l h_rt=120:0:0    # Request 240 hour runtime")
print("#$ -l h_vmem=32G      # Request 4GB RAM")

print("cd "+args.msgf_path[0])
command=" ".join(["java", "-Xmx12000M", "-jar", "MSGFPlus.jar","-s",args.input[0],"-d",args.database[0]+".cont.fasta","-o",args.output[0],"-mod",args.modification[0],"-t",args.tolerance[0],"-m",args.m_msgf[0],"-tda",args.tda[0],"-inst",args.inst[0],"-minLength",args.minLength[0],"-thread","8"])
#print("#"+command)
print(command)
outBase=os.path.splitext(args.output[0])[0]
#os.system(command)
#print(os.chdir(args.mzident_path[0]))
#print(os.getcwd())
print("cd "+args.mzident_path[0])
mzFDR=" ".join(["java","-Xmx12000M","-jar","mzidentml-lib.jar","FalseDiscoveryRate",args.output[0],outBase+"+fdr.mzid","-decoyRegex","XXX_","-decoyValue","1","-cvTerm","\"MS:1002053\"","-betterScoresAreLower","true"])
print(mzFDR)

#os.system(mzFDR)

mzTh=" ".join(["java","-Xmx8024m","-jar","mzidentml-lib.jar","Threshold",outBase+"+fdr.mzid",outBase+"+fdr+th.mzid","-isPSMThreshold","true","-cvAccessionForScoreThreshold","MS:1002355","-threshValue","0.01","-betterScoresAreLower","true","-deleteUnderThreshold","true"])
print(mzTh)
#os.system(mzTh)

mzGrp=" ".join(["java","-Xmx4024m","-jar","mzidentml-lib.jar","ProteoGrouper",outBase+"+fdr+th.mzid",outBase+"+fdr+th+grouping.mzid","-cvAccForSIIScore","MS:1002355","-logTransScore","true","-requireSIIsToPassThreshold","true","-verboseOutput","false"])
print(mzGrp)
#os.system(mzGrp)

mzPep=" ".join(["java","-Xmx4024m","-jar","mzidentml-lib.jar","Mzid2Csv",outBase+"+fdr+th+grouping.mzid",outBase+"+fdr+th+grouping.csv","-exportType","exportPSMs","-compress","false"])
print(mzPep)
#os.system(mzPep)

mzPrt=" ".join(["java","-Xmx4024m","-jar","mzidentml-lib.jar","Mzid2Csv",outBase+"+fdr+th+grouping.mzid",outBase+"+fdr+th+grouping+prt.csv","-exportType","exportProteinsOnly","-compress","false"])
print(mzPrt)
#os.system(mzPrt)

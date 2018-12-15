#Hi! Before you start off running this please go to Analyze -> Set Measurements
#choose Area, Shape Discriptors, and Stack position
#This could have been automatic, but it is not working. (I tried...TAT)
import os
from ij import IJ, ImagePlus, Macro
from ij.measure import ResultsTable, Measurements
from ij.plugin.frame import ThresholdAdjuster
from ij.plugin.filter import ParticleAnalyzer
from ij.gui import GenericDialog
from loci.plugins import BF
from loci.plugins.in import ImporterOptions

#This function is to open the VHL-tumor sample and feed it to the function findclearcell
#All the images from the same sample will be analyzed one-by-one automatically
def findclearcell_run():
  inDir = IJ.getDirectory("Input directory")
  if not inDir:
    return
  gd = GenericDialog("Process Folder")
  gd.addStringField("File extension", ".oir")
  gd.addStringField("File name starts with (the date)", "")
  gd.showDialog()
  if gd.wasCanceled():
    return
  ext = gd.getNextString()
  containString = gd.getNextString()
  for root, directories, filenames in os.walk(inDir):
    for fileName in filenames:
      if not fileName.endswith(ext):
        continue
      if containString not in fileName:
        continue
      print findclearcell(inDir, root, fileName)

#This function finds where the clear cells in a samples
def findclearcell(inDir, currentDir, fileName):
  print "Opening", fileName
  file_path= os.path.join(currentDir, fileName)
  options = ImporterOptions()
  options.setId(file_path)
  options.setSplitChannels(True)
  imps = BF.openImagePlus(options)
  for imp in imps:
  	imp.show()
  if not imps:
  	return
  IJ.selectWindow(fileName + " - C=2")
  IJ.run("Close")
  IJ.selectWindow(fileName + " - C=1")
  IJ.run("Close")
  IJ.selectWindow(fileName + " - C=0")
  IJ.run("Close")
  IJ.selectWindow(fileName + " - C=3")
  IJ.run("8-bit")
  IJ.run("Options...", "iterations=1 count=1 black edm=8-bit")
  IJ.setThreshold(62, 255)
  IJ.run("Convert to Mask", "method=Default backgorund=Dark black")
  Macro.setOptions("Stack position")
  for n in range(4,15):
	n+=1
	IJ.setSlice(n)
	IJ.run(imp, "Analyze Particles...", "size=7.2-9 circularity=0.7-0.95 display")

#this part runs all the function above
#clear cells are differentiated by the solidity of the particles detected (Threshold:0.8)
findclearcell_run()
rt=ResultsTable.getResultsTable()
totalparticles= rt.getCounter()
solidones=[]
for n in range(totalparticles):
  row=float(rt.getStringValue("Solidity",n))
  if row > 0.8:
    solidones.append(row)
numofclearcells= len(solidones)
print numofclearcells
#numbers from the UT-18-0614_HLRCC_Normal sample. Got from the same program ran above
#in 24 slices, a total of 626 particles detected, but only 170 of them have a solidity over 0.8
normal_totp=626
normal_soli=170

#calculate the score by the ratio of the number of clear cells vs. the total number of particles
normal_threshold= (float(normal_soli)/float(normal_totp))*100   #around 27%
#the VHL tumor samples have around at least a 79%
tumor_score= (float(numofclearcells)/float(totalparticles))*100

gd = GenericDialog("Results")
gd.addMessage("Score Guide")
#just a rough estimate, but because of the large difference between the clear cell carcinorma and normal samples, this works. 
gd.addMessage("->  The threshold for no clear cells is 40.5%")
gd.addMessage("->  Clear cell carcinoma samples have a percentage higher than 79%")
if tumor_score> 79.0:
  gd.addMessage("Score is {0:.2f}.".format(tumor_score))
  gd.addMessage("Clear cell carcinoma is detected.")
elif tumor_score < 40.5:
  gd.addMessage("Score is {0:.2f}.".format(tumor_score))
  gd.addMessage("No clear cells are found.")
else:
  gd.addMessage("Score is {0:.2f}.".format(tumor_score))
  gd.addMessage("The score is higher than the threshold for tissue without clear cells.")
gd.showDialog()

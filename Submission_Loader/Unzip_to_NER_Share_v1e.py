version = '1e'
###########################################################################
#
#							Submission Loader
#
# Purpose:
# This tool is intended forNER RIAU internal use only.
#
# Requirement:
# Must have ArcPy modules (ArcMap version 10.0+ installed)
#
# Notes:
# This script works only if the submission has one type of spatial layer. if the submission has multiple type, it will pick one (priority list = gdb, shp, e00)
#
# Workflow:
# 1. Unzips all zip files (including the ones in the subfolders)
# 2. Identifies the Submission number, Submission Type, Data format and Forest Management Unit based on the file/folder names.
# 3. If the submission has been identified as HEARST AWS 2018, then the tool will create this destination folder structure:
# '\\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS\HEARST\AWS\2018\SubID_99999' where 99999 is the submission ID.
# If such folder already exists, the tool will terminate.
# 4. Copies the unzipped files and folders to a temporary folder. 
# 5. Creates a metadata txt file.
# 6. Creates ...\_data\FMP_Schema.gdb geodatabase in the temporary folder and transfers the spatial data to the geodatabase.(The tool will convert e00 or shp to feature classes)
# 7. If same type of layer exists (such as mu415_16aoc01 and mu415_16aoc02), the tool will merge them.The merged fc will be named 'mu415_16aoc_merged'in this example.
# 8. Exports all files to the destination folder and deletes the temporary folder.
#
# Note that this tool only works best on AR and AWS, final/draft FMPandFMP contingency plan. It's not intended for intermediate products such as checkpoint 1 submission.
#
# Do not use this tool for Information Posts.
#
#
# Assumptions:
# The input folder (or zipfile) contains at least one folder with the following naming convention: "Product Submission - 99999" where 99999 is the 5 digit submission Id
#
# Limitations:
# As of Nov 2018, the tool can generate symbologies only for AR submissions. We need layer files with correct symbology for AWS and FMP submissions.
# The layer order should be fixed.
# The tool was intended to work on new AWS, AR, and FMP submissions that follows the 2017 tech spec. 
# It will still run on old tech spec, but may not recognize older layers when applying the symbology.
#
#
###########################################################################
debug = False

import os, datetime, shutil, traceback, time
import Loader.UnzipAll as UnzipAll
import Loader.IdentifySubmission as idSub
import Loader.WriteMetadata as meta
import Loader.copy_if_not_there as copy_if_not_there
import Loader.Convert2GDB as Convert2GDB
import Loader.merge_if_same_type as merge_if_same_type
import Loader.Apply_layerfile as Apply_layerfile
from Loader.functions import print2, rand_alphanum_gen

def main(fiDownloadzipfile,outputFMPfolder,openfolder):
	"""
	fiDownloadzipfile is the file location of the zipfile downloaded off the FI Portal (can be a zipfile or a non-zipfile)
	outputFMPfolder is the dir to the root of the local fmp folder. 
	if your outpuFMPfolder is 'C:\\user\\_FMP_LOCAL', and if your submission is HEARST AWS 2018,
	this tool will import submission into 'C:\\user\\_FMP_LOCAL\\Hearst\\AWS\\2018'
	"""

	print2('fiDownloadzipfile = %s'%fiDownloadzipfile)
	print2('outputFMPfolder = %s'%outputFMPfolder)
	print2('openfolder = %s'%openfolder)


	# Unzip the downloaded file. There usually are more zipfiles within a zipfile.
	print2('Unzipping...')
	submFolderDirList = UnzipAll.unzipAllSubmission(fiDownloadzipfile)
	# For example, submFolderDirList = ['C:\\FIPDownload\\download_cart_2018-01-02aws\\Product Submission - 23026', 'C:\\FIPDownload\\download_cart_2018-01-02aws\\Product Submission - 23028']
	print2('\nSubmissions Found:')
	subFList = [os.path.split(i)[1] for i in submFolderDirList]
	for subF in subFList:
		print2('\t%s'%subF)

	# If no submission found, the script will end here:
	if len(submFolderDirList) == 0:
		raise Exception("\nFinished unzipping but no submission file was found!!!\nThis tool is not designed to run on info posts.")


	return_dict = {}

	for submFolderDir in submFolderDirList:
		print2("\n\n\n**********    Working on %s  *********\n"%os.path.split(submFolderDir)[1])
		# Examine each submissions and figure out the subID, submission year, fmu name, submission type and list of layers.

		# subID
		try:
			SubID = int(submFolderDir[-5:])
		except:
			raise Exception("Unable to locate 'Product Submission - 00000' folder.\nMake sure you are running this tool on a FI portal submission.")
		
		# --------------------------  running identify submission module  -------------------------------------

		# Note that idSub.identifySubmission() module will return this list: [fmuName,fmuCode,submType,submYear,filetype,filelist,pdflist]
		fmuName, fmuCode, submType, submYear, filetype, filelist, pdflist = idSub.identifySubmission(submFolderDir)
		if len(filelist) == 0:
			print2("No spatial data found!",'warning')
		print2('fmuName: %s\nfmuCode: %s\nsubmType: %s\nsubmYear: %s\nfiletype: %s'%(fmuName, fmuCode, submType, submYear, filetype))
		print2('spatial data found:')
		for file in filelist:
			print2('  %s'%os.path.split(file)[1])
		if debug:
			print2('filelist: %s\npdflist: %s'%(filelist, pdflist))

		# -----------------------------------------------------------------------------------------------------

		# Prep'ing the new location where the files will be moved to
		outputFolder = os.path.join(outputFMPfolder,fmuName,submType,submYear,'SubID_%s'%SubID) # for example, ...\FMPDS\Abitibi_River\AWS\2018\SubID_22788

		# However, all the work will be done in a temporary location in C drive
		tempFolder = os.path.join('C:\\','Temp\\temp_' + rand_alphanum_gen(8)) # for example, C:\Temp\temp_VV000VDW

		# if the outputFolder directory already exist, do nothing.
		if os.path.isdir(outputFolder):
			print2('\nThe same submission already exists in this folder:\n%s\nTerminating the tool...'%outputFolder,'warning')
			print2('If you need to re-run the sub %s, then you must first delete the folder and try again'%(SubID),'warning')
		elif os.path.isdir(tempFolder):
			# this temp folder should never already exist...
			raise Exception('\n%s already exists!'%tempFolder)
		else:
			# try and except to delete all files if something went wrong.
			try:
				# Moving geospatial files
				print2('\nCopying %s to a temporary location: %s ...'%(filetype,tempFolder))
				if filetype == 'gdb':
					for filegdb in filelist:
						filegdbname = os.path.split(filegdb)[1]
						if debug: print2('Copying %s to %s'%(filegdb, os.path.join(tempFolder,'gdb',filegdbname)))
						shutil.copytree(filegdb,os.path.join(tempFolder,'gdb',filegdbname)) # copytree also creates a new directory
				elif filetype == 'shp':
					originalLocation = os.path.split(filelist[0])[0]  #eg. C:\\FIPDownload\\download_cart_2018-01-08\\Product Submission - 23035\\MU898_2018_AWS\\MU898_2018_AWS_LAYERS\\MU898_2018_AWS
					shutil.copytree(originalLocation,os.path.join(tempFolder,'shp'))
				elif filetype == 'e00':
					originalLocation = os.path.split(filelist[0])[0]
					shutil.copytree(originalLocation,os.path.join(tempFolder,'e00'))

				# Moving pdf files
				if len(pdflist) > 0:
					# create the pdf folder
					pdffolder = os.path.join(tempFolder,'pdf')
					if not os.path.exists(pdffolder): os.makedirs(pdffolder)
					print('Moving %s pdf files to... %s'%(len(pdflist),pdffolder))
					# copy the pdfs over
					for pdf in pdflist:
						shutil.copy2(pdf,pdffolder) # copies pdf file to the pdf folder just created while retaining the same filename. (pdf folder must first exist)

				# Moving all other files
				print2('Copying rest of the files to the destination folder...')
				copy_if_not_there.main(submFolderDir,tempFolder)

				# writing metadata (fi_submission_00000.txt) file
				try:
					print2('Writing metadata text file...')
					meta.writeMetadata(outputFolder,SubID,fmuName,fmuCode,submType,submYear,filetype,tempFolder)
				except:
					print2('Failed to write metadata text file.','warning')
					if debug: print2(str(traceback.format_exc()), 'warning')

				print2("\nCompleted copying all files to %s"%tempFolder)


				if len(filelist) > 0:
					# converting to gdb
					print2("\nCreating '_data' folder and 'FMP_Schema.gdb' ...")
					newgdbpath = Convert2GDB.main(tempFolder,filetype,filelist)
					print2("\nAll data now in a temporary location: %s"%newgdbpath)


					# merge same type of layers. (eg. AOC01, AOC02...)
					print2("\nChecking if any of the fcs needs merging...")
					try:
						merge_if_same_type.main(newgdbpath)
					except:
						print2('WARNING: Merging same type of fcs (such as AOCs or SACs) was unsuccessful.\nThis can happen when trying to merge two or more layers with same field name but different field length or type.', 'warning')

				else: # if len(filelist) == 0
					print2('WARNING: No spatial data found!!!', 'warning')


				# moving the temporary files to the final output location

				print2("\nMoving files from %s\nto\n%s"%(tempFolder,outputFolder))
				shutil.copytree(tempFolder,outputFolder)

				print2('\nCleaning up temporary files...')
				shutil.rmtree(tempFolder)

				# Creating layer files...
				# using try and accept, because it's not mandatory to have layer files.
				print2('\nAttempting to create layer files and apply symbology to all layers...')
				try:
					Apply_layerfile.main(submType, '2017', outputFolder, SubID, fmuName, fmuCode, submYear)
					print2('\nLayer files (with symbology) successfully created!')
				except:
					print2("\nCould not create layer files due to the following error:", 'warning')
					print2(str(traceback.format_exc()), 'warning')


				print2("\n**********   %s - Import Complete!!  *********\n"%os.path.split(submFolderDir)[1])


			# Error handling
			except:
				print2('Something went wrong while transferring and converting data...\nRemoving transitory files before terminating...','warning')
				if os.path.exists(outputFolder): shutil.rmtree(outputFolder)
				print2(str(traceback.format_exc()), 'warning')
				print2('\nERROR: The tool could not transfer and convert %s.\n'%os.path.split(submFolderDir)[1], 'error')

			finally:
				# making sure the temp folder is cleaned up whether ran into an error or not.
				if os.path.exists(tempFolder): 
					try:
						shutil.rmtree(tempFolder)
					except:
						print2('Failed to delete the temp folder: %s'%tempFolder, 'warning')



			return_dict[SubID] = [filetype,outputFolder] # this dictionary opens up the possibility of automating submission checker later on.

		# open the output folder when everything is complete.
		if openfolder:
			if os.path.exists(outputFolder): os.startfile(outputFolder)


	if debug: print2(str(return_dict)) # e.g. {24649: ['gdb', u'C:\\FIPDownload\\test1\\Gordon_Cosens\\AR\\2017\\SubID_24649']}

	print2('Script version = %s'%version)
	return return_dict







if __name__ == '__main__':
	# # Input1 is the file location of the zipfile downloaded off the FI Portal
	# # can be a zipfile or a non-zipfile.
	# fiDownloadzipfile = r'C:\FIPDownload\download_cart_2018-10-30ar.zip'
	# # Input2 is the dir to the local/shared fmp folder where the output will be populated
	# # outputFMPfolder = r'N:\WORK-DATA\FMPDS'
	# outputFMPfolder = r'C:\DanielK_Workspace\_FMP_LOCAL'
	# main(fiDownloadzipfile,outputFMPfolder)



	fiDownloadzipfile = arcpy.GetParameterAsText(0) # must be an existing zipfile
	outputFMPfolder = arcpy.GetParameterAsText(1) # optional field.
	openfolder = arcpy.GetParameterAsText(2) # True or False

	if outputFMPfolder == '':
		# outputFMPfolder = r'\\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS'
		outputFMPfolder = r'\\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS'
	if openfolder == 'true':
		openfolder = True
	else:
		openfolder = False

	main(fiDownloadzipfile,outputFMPfolder,openfolder)
import os, zipfile


def zipfileCounter(parentfolder):
	"""This tool counts the number of zipfiles in a parentfolder.
	This tool is needed for the unzipAll and unzipAllSubmission function to work"""
	zipcount = 0
	walker = os.walk(parentfolder)
	for foldername, subfolders, filenames in walker:
		for filename in filenames:
			if filename[-3:].upper() == 'ZIP':
				zipcount += 1
	return zipcount

def unzipAll(parentfolder):
	""" Use this function to search all the zipfiles in a parentfolder
		and extract them all"""
	while zipfileCounter(parentfolder) > 0:
		walker = os.walk(parentfolder)
		for foldername, subfolders, filenames in walker:
			for filename in filenames:
				if filename[-3:].upper() == 'ZIP':
					zipfilename = os.path.join(foldername,filename)
					# print('Unzipping %s...'%zipfilename)
					zip_ref = zipfile.ZipFile(os.path.join(foldername,filename),'r')
					newFolderName = os.path.join(foldername,filename[:-4])
					zip_ref.extractall(newFolderName)
					zip_ref.close()
					os.remove(zipfilename)


def unzipAllSubmission(fiDownloadzipfile):
	""" This function will take fiDownloadzipfile such as 'C:\FIPDownload\download_cart_2018-01-04aws.zip'
		and will unzip it all. It will also return the new parent folder and a list of submission folders inside it"""

        # print "here"
	# Unzip the downloaded product
	if fiDownloadzipfile[-3:].upper() == 'ZIP':
		# print('unzipping %s ...'%fiDownloadzipfile)

		zip_ref = zipfile.ZipFile(fiDownloadzipfile,'r') # path to the zip file
		fiDownloadFolder = fiDownloadzipfile[:-4]
		zip_ref.extractall(fiDownloadFolder) # directory to extract
		zip_ref.close()
	else:
		fiDownloadFolder = fiDownloadzipfile

	# walk through the unzipped folder and search for submission product folders - and save it as a list of paths.
	walker = os.walk(fiDownloadFolder)
	submissionFolderList = []
	for foldername, subfolders, filenames in walker:
		for subfolder in subfolders:
	 		if 'Product Submission - ' in subfolder:
	 			submissionFolderList.append(os.path.join(foldername,subfolder))

	# print('Submissions found: ' + str(submissionFolderList))

	for submission in submissionFolderList:

		# print('Working on %s...'%submission)

		# identify the submission ID.
		submissionID = int(submission[-5:] or None)

		# unzipAll function will continue to find and unzip .zip files until there's no more zip file left in that folder
		unzipAll(submission)

	# print('This fiDownloadzipfile function returns: \n%s\n%s'%(fiDownloadFolder,submissionFolderList))
	return submissionFolderList

	# For example, This function returns the following:
	# ['C:\\FIPDownload\\download_cart_2018-01-02aws\\Product Submission - 23026', 'C:\\FIPDownload\\download_cart_2018-01-02aws\\Product Submission - 23028']



if __name__ == '__main__':
    zipFileLocation = 'C:\FIPDownload\download_cart_2019-02-20.zip'
    print unzipAllSubmission(zipFileLocation)




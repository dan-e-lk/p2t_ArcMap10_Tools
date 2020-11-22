from functions import print2

def main(src,dst,newfoldername = 'otherfiles'):
	"""
	This function copies all the files in the src directory (including the files in all the sub-directories)
	to the dst's newfolername folder ONLY IF the same filename does not exist in the dst directory.
	src and dst must be full path. newfoldername must be the name of the new folder being created.
	Note that this function would not work well if src directory has files with same filename in different sub-directories.
	"""

	import os, shutil
	dst_folder = os.path.join(dst,newfoldername)
	try: 
		os.makedirs(dst_folder)
	except: 
		raise Exception("Unable to copy all the files - Could not create the destination folder %s"%dst_folder)

	# get list of all files in the dst
	dst_filename_list = []
	dst_walker = os.walk(dst)
	for foldername, subfolders, filenames in dst_walker:
		for filename in filenames:
			dst_filename_list.append(filename)

	# copy files from src and paste to dst if the file does not exist in dst
	src_walker = os.walk(src)
	for foldername, subfolders, filenames in src_walker:
		for filename in filenames:
			if filename not in dst_filename_list:
				filename_fullpath = os.path.join(foldername,filename)
				try:
					shutil.copy2(filename_fullpath, dst_folder)
				except:
					print2("unable to copy \n%s \nto destination folder."%filename_fullpath)

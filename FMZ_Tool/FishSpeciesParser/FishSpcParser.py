version = 'beta1'
# Use this tool on the ARA_WATER_POLY_SEGMENT or ARA_WATER_LINE_SEGMENT
# Those two layers should have FISH_SPECIES_SUMMARY text field that contains a list of fish species.
# The tool will create new fields with each field named after the fish species found.
# The new fish species fields will be filled out with 1 or 0 based on the presence/absence of the fish in that water feature.

import arcpy
import os


def compact_words(word, max_length = 10):
	"""
	Turn any word(s) into 10 characters or less by removing vowels, special characters and more.
	"""
	import re
	# First, remove any special characters and extra spaces
	word = re.sub(r'[^A-Za-z]+', r'_', word) #'Nocomis Sp.' -> 'Nocomis_Sp_'
	if word[-1] == '_': # remove trailing underscore   'Nocomis_Sp_' -> 'Nocomis_Sp'
		word = word[:-1] 
	# if the word is already less than max_length, return the word.
	if len(word) <= max_length:
		return word
	# if the word is only 1 character over, just remove the last character		
	elif len(word) == max_length + 1:
		return word[:-1]
	else:
		# Split words because we don't want to remove the first letter of each words
		new_word = ''
		word_list = word.split('_')
		for w in word_list:
			w = w[0] + re.sub(r'[aeiouAEIOU_]', '', w[1:])  # removing vowels with the exception of the first letter for each word
			if len(new_word) > 0:
				new_word += '_'
			new_word += w
		if len(new_word) <= max_length:
			return new_word
		else:
			return new_word[:max_length]


class FishSpcParser:

	def __init__(self, inputfc, fishSpcField):
		self.inputfc = inputfc
		self.fishSpcField = fishSpcField
		self.rec_count = 0
		self.water_with_fish_count = 0
		self.spc_dict = {}	


	def summarize_fish(self):
		"""
		Summarizes Fish Speices Summary field by creating a list of tuples containing species names and number of occurrences.
		"""
		fish_spc_summary_all = []
		with arcpy.da.SearchCursor(self.inputfc, self.fishSpcField) as cursor:
			for row in cursor:
				self.rec_count += 1
				if cursor[0] not in (None,'',' '):
					self.water_with_fish_count += 1
					fish_spc_summary_all.append(str(cursor[0]).upper().split(','))

		for fish_list in fish_spc_summary_all:
			for fish in fish_list:
				if fish in self.spc_dict.keys():
					self.spc_dict[fish] += 1
				else:
					self.spc_dict[fish] = 1


	def print_summary(self, order = 'desc'):
		"""
		Works with dictionaries with string keys and numeric values such as {'BROOK TROUT':30, 'WALLEYE':22}
		The output is a comma separated values of the dictionary reordered based on the numeric values.
		order should be 'desc' or 'asc'.
		"""
		TorF = True if order == 'desc' else False
		rank = 0

		arcpy.AddMessage('\nTotal Number of Records = %s\nNumber of Records with Fish Info = %s\nNumber of Species Found: %s\n'
					%(self.rec_count, self.water_with_fish_count, len(self.spc_dict)))

		SppOccrCsv = 'Rank,Species,Occurences'
		for spc, occ in sorted(self.spc_dict.items(), key=lambda (k,v): (v,k), reverse=TorF): # sort by the order of most commonly occurred to least.
			rank += 1
			SppOccrCsv += '\n%s,%s,%s'%(rank,spc,occ)

		arcpy.AddMessage(SppOccrCsv)

	def export(self, outputfc):
		arcpy.AddMessage('\nCreating a copy of the input...\n')
		arcpy.FeatureClassToFeatureClass_conversion(in_features= self.inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1])

	def create_new_fields(self, outputfc, max_num_spc, limit_fieldname_to_10char):
		"""
		Creates new attributes (or fields) based on the species found. The number of new attributes cannot exceed the max_num_spc.
		"""
		import re

		# we must first pick top x most occurring species and remove any special characters.
		self.spc_to_fieldname = []
		count = 0
		unique_fieldnames = [] # temporary list - only to check if the values in this list are unique
		for spc, occ in sorted(self.spc_dict.items(), key=lambda (k,v): (v,k), reverse=True):
			s1 = spc
			s2 = re.sub(r'[^A-Z]+', r'_', s1) # strip all text except A-Z
											  # for example, 'NORTHERN REDBELLY DACE X FINESCALE DACE' becomes 'NORTHERN_REDBELLY_DACE_X_FINESCALE_DACE'
			if s2[-1] == '_': # remove trailing underscore   'Nocomis_Sp_' -> 'Nocomis_Sp'
				s2 = s2[:-1] 

			if limit_fieldname_to_10char:
				s3 = compact_words(s1) # this will compact words to 10 char or less - shapefile's fieldname cannot be more than 10 characters.
				
				# values in s3 has to be unique because this will be used to create fieldnames.
				# if for example, 'FRSPN_STCK' already exists, the following will populate 'FRSPN_STC1' as s3 value.
				while s3 in unique_fieldnames:
					# arcpy.AddMessage('%s already exists!'%s3)				
					if len(re.findall('[1-9]',s3[-1])) == 0: # if the last character does not contain a number value...
						s3 = s3[:-1] + '1'
					else:
						s3 = s3[:-1] + str(int(s3[-1]) + 1) # if 'NRTHRN_RD1' already exists, this will create a new fieldname - 'NRTHRN_RD2'
				unique_fieldnames.append(s3)
			else:
				s3 = s2

			self.spc_to_fieldname.append((s1,s2,s3)) # list of tuples [('FOURSPINE STICKLEBACK','FOURSPINE_STICKLEBACK', 'FRSPN_STCK'),...]
			count += 1
			if count == max_num_spc:
				break


		# creating new fields in alphabetical order
		self.spc_to_fieldname.sort() # we want this to alphabetically sorted this time
		arcpy.AddMessage('\nCreating new fields (max=%s):'%max_num_spc)
		for spc in self.spc_to_fieldname:
			arcpy.AddMessage('  %s (%s)'%(spc[1],spc[2])) if limit_fieldname_to_10char else arcpy.AddMessage('  %s'%spc[1])
			arcpy.AddField_management(outputfc, spc[2], "SHORT", field_alias = spc[1])


	def populate_fields(self,outputfc):
		"""
		Populates individual species fields with 0 or 1 based on the presence.
		"""
		arcpy.AddMessage('\nPopulating new fields with 0 or 1...')
		fields = [i[2] for i in self.spc_to_fieldname] # list of newly created fields
		fields.append(self.fishSpcField) # add the FISH_SPECIES_SUMMARY field to the list

		with arcpy.da.UpdateCursor(outputfc,fields) as cursor:
			for row in cursor:
				fish_list = str(row[-1]).upper() # row[-1] is the FISH_SPECIES_SUMMARY value such as "Brook Trout,Chrosomus sp.,Northern Redbelly Dace"
				for index, spc in enumerate(self.spc_to_fieldname):
					row[index] = 1 if spc[0] in fish_list else 0
				cursor.updateRow(row)

	def generalize(self,outputfc, maximum_offset):
		arcpy.AddMessage("Generalizing (%sm tolerance)..."%maximum_offset)
		arcpy.Generalize_edit(in_features=outputfc, tolerance="%s Meters"%maximum_offset)



if __name__ == '__main__':

	######################         Example Input        #############################

	# fc = r'C:\DanielK_Workspace\_FMZ\FMZ10\FMZ10.gdb\ARA_WATER_POLY_SEG_FishNotNull'
	# field = 'FISH_SPECIES_SUMMARY'
	# summarize_only = False
	# outputfc = r'C:\DanielK_Workspace\_FMZ\FMZ10\FMZ10.gdb\ARA_WATER_POLY_SEG_parsed'
	# max_num_spc = 50 	# max number of species - the number of new attributes created is equal to number of species found. 
	# 					# But you should limit this number to for example "top 100 most occurring species"
	# 					# This number won't affect the summary. It will only restrict the number of new attributes created.
	# limit_fieldname_to_10char = True
	# generalize = True
	# maximum_offset = 5 # generalization tolerance in meters

	##################################################################################


	#############################          INPUT           ###########################

	fc = arcpy.GetParameterAsText(0) # ARA Water Segment layer (or a subset of it)
	field = arcpy.GetParameterAsText(1)
	summarize_only = arcpy.GetParameterAsText(2) # boolean
	outputfc = arcpy.GetParameterAsText(3)
	max_num_spc = arcpy.GetParameterAsText(4) # must a a positive integer (zero not accepted)
	limit_fieldname_to_10char = arcpy.GetParameterAsText(5) # boolean
	generalize = arcpy.GetParameterAsText(6) # boolean
	maximum_offset = arcpy.GetParameterAsText(7) # generalization tolerance in meters - float values between 0.01 and 50.0

	##################################################################################

	summarize_only = True if summarize_only == 'true' else False
	limit_fieldname_to_10char = True if limit_fieldname_to_10char == 'true' else False
	generalize = True if generalize == 'true' else False

	arcpy.AddMessage('Tool version = %s'%version)
	myFish = FishSpcParser(fc,field)
	myFish.summarize_fish()
	myFish.print_summary()

	if not summarize_only:
		myFish.export(outputfc)
		myFish.create_new_fields(outputfc, max_num_spc, limit_fieldname_to_10char)
		myFish.populate_fields(outputfc)
		if generalize:
			myFish.generalize(outputfc,maximum_offset)

	arcpy.AddMessage('\nCompleted!!\n')


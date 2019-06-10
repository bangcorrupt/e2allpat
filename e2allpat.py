import zipfile
import zlib
from io import BytesIO
from flask import send_file

class E2AllPat():
	def __init__(self, ap, ap_type):
		
		self.ap_type = ap_type

		if self.ap_type == 'e2allpat' or self.ap_type == 'e2sallpat':
			self.ap_data = ap.read()
		
		elif self.ap_type == 'zip':
			self.ap_data = self.zip_to_ap(ap)

		self.pat_count = 250	
			
		self.header = self.ap_data[:0x100]	# Korg file header
		self.settings = self.ap_data[0x100:0x10100] # global settings + padding
		self.pattern = self.get_patterns()

	
	def get_patterns(self):
		pat_off = 0x10100
		pat_len = 0x4000
		pat_list = []
		for i in range(self.pat_count):		
			start = pat_off+(i*pat_len)
			end = start + pat_len
			pat_data = self.ap_data [start:end]			
			pat_data = self.header + pat_data
			pat_list.append(pat_data)			# update this to be list of pattern objects
		return pat_list


	def write_ap(self):		
		ap_file = BytesIO(self.ap_data)
		ap_file.seek(0)
		return ap_file


	
	def write_zip(self):
		if self.ap_type == 'e2allpat':
			filename = 'global_settings.e2global'
			zip_name = 'e2allpat.zip'
			extension = '.e2pat'
		elif self.ap_type == 'e2sallpat':
			filename = 'global_settings.e2sglobal'
			zip_name = 'e2sallpat.zip'
			extension = '.e2spat'
		zip_file = BytesIO()
		data = self.header + self.settings
		with zipfile.ZipFile(zip_file, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
				zf.writestr(filename , data)

		for i in range(self.pat_count):
			data = self.pattern[i]
			filename = str(i+1).zfill(3) + '_' + data[256:][16:32].decode().rstrip('\0') + extension
			with zipfile.ZipFile(zip_file, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
				zf.writestr(filename , data)
		zip_file.seek(0)
		
		return zip_file


	
	def zip_to_ap(self, ap_zip):
		zf = zipfile.ZipFile(ap_zip,mode='r')
		file_list = sorted(zf.namelist())
		if file_list[0][-5:] == 'e2pat':
			self.ap_type = 'e2allpat'
		elif file_list[l][-6:] == 'e2spat':
			self.ap_type = 'e2sallpat'

		# find *.e2global
		l = 0
		settings = False
		if self.ap_type == 'e2allpat':
			while settings == False:
				if len(zf.read(file_list[l])) == 65792 and (file_list[l][-8:] == 'e2global' or file_list[l][-9:] == 'e2sglobal'):
					settings = zf.read(file_list[l])
					del file_list[l]
				else: 
					l+=1
					
		elif self.ap_type == 'e2sallpat':
			while settings == False:
				if len(zf.read(file_list[l])) == 65792 and (file_list[l][-8:] == 'e2global' or file_list[l][-9:] == 'e2sglobal'):
					settings = zf.read(file_list[l])
					del file_list[l]
				else: 
					l+=1
		ap_list = [settings]	# add korg file header + global settings

		for k in range(250):	
			pat_data = bytearray(zf.read(file_list[k])[256:])
			if self.ap_type == 'e2allpat':	
				pat_name = file_list[k][4:-6].ljust(16, '\0')
			elif self.ap_type == 'e2sallpat':
				pat_name = file_list[k][4:-7].ljust(16, '\0')
			pat_data[16:32] = [ord(x) for x in pat_name]
			ap_list.append(pat_data)

		# flatten list
		ap_data=[]
		for i in ap_list:
			for j in i:
				ap_data.append(j)
		
		return bytearray(ap_data)



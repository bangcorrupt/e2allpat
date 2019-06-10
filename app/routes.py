import os
from flask import request, render_template,flash, redirect, url_for, send_file
from app import app
from werkzeug.utils import secure_filename
from  e2allpat import *

ALLOWED_EXTENSIONS = set(['e2allpat','e2sallpat', 'zip'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file selected')
			return redirect(request.url)
		file = request.files['file']
		
		if file.filename == '':
			flash('No file selected')
			return redirect(request.url)
		
		if file and allowed_file(file.filename):                     
			if file.filename[-8:] == 'e2allpat':
				ap = E2AllPat(file, 'e2allpat')
				response = ap.write_zip()
				file_name = file.filename[:-9] + '.zip'				
			
			elif file.filename[-9:] == 'e2sallpat':
				ap = E2AllPat(file, 'e2sallpat')
				response = ap.write_zip()
				file_name = file.filename[:-10] + '.zip'	
			
			elif file.filename[-3:] == 'zip':
				ap = E2AllPat(file, 'zip')
				response = ap.write_ap()
				if ap.ap_type == 'e2allpat':
					file_name = file.filename[:-4] + '.e2allpat'		
				elif ap.ap_type == 'e2sallpat':
					file_name = file.filename[:-4] + '.e2sallpat'		

			return send_file(response, attachment_filename=file_name, as_attachment=True) #and redirect(url_for('index'))
	
	return render_template('index.html')           

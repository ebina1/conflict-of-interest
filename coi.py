#!/usr/bin/python3

import sys, csv, urllib.request, json, mimetypes, xlrd, re
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
 
window = Tk()
window.title("DBLP conflict search")
window.config(bd=20)

Current_author = 0
Author_cnt = 0
Paper_cnt = 0
submission_file = ''
reviewer_file = ''
Header_row = -1
ID_col = -1
Conflicts_col = -1


def submission_browse():
	global submission_file
	# clear all previously displayed file info in preparation for a new file.
	display_frame_clear()
	clear_feedback()
	export_cflict_btn.grid_forget()
	file = filedialog.askopenfilename(filetypes = (("Comma separated values","*.csv"),("spreadsheet","*.xlsx")))
	if (file != ''):
		status = check_for_conflict_column(file)
		# status 0 = bad file data
		# status 1 = No header row, but at least two columns (assume paper id, authors)
		# status 2 = Has header row, find Paper ID and Author Names columns, no Conflicts column
		# status 3 = Has header row, find Paper ID and Author Names columns, has Conflicts column
		if (status == 0):
			submission_file = ''
			filename_lbl.configure(text='No file selected.')
			return
		if ((status == 1) or (status == 2)):
			export_cflict_btn.grid_forget()
		if (status == 3):
			export_cflict_btn.grid(column=3, row=0)
		submission_file = file
		fp = submission_file.split('/')
		filename_lbl.configure(text=fp[-1])
		# Despite its name, review_data reads and processes the file, setting important globals
		review_data(status)

def reviewer_browse():
	global reviewer_file
	# clear all previously displayed file info in preparation for a new file.
	display_frame_clear()
	clear_feedback()
	file = filedialog.askopenfilename(filetypes = (("Comma separated values","*.csv"),("spreadsheet","*.xlsx")))
	if (file != ''):
		status = check_for_any_names(file)
		# status 0 = bad file data
		# status 1 = No header row, but something in first column (assume reviewers)
		# status 2 = Has header row, found Reviewer column with at least one name
		if (status == 0):
			reviewer_file = ''
			filename_lbl0.configure(text='No file selected.')
			return
		reviewer_file = file
		fp = reviewer_file.split('/')
		filename_lbl0.configure(text=fp[-1])
		# Despite its name, reads and processes the file, setting important globals
		review_reviewerdata(status)

def export_conflicts():
	global submission_data
	global Author_cnt
	if ((submission_file == '') or (len(submission_data) == 0)):
		message_lbl["text"] = "No submission data"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return
	clear_feedback()
	clist = read_conflict_list()
	if (len(clist) == 0):
		return
	cyear = get_year()
	Author_cnt = len(submission_data) - Paper_cnt
	progress.grid(column=0, row=0, sticky="w")
	prog_name_lbl.grid(column=2, row=0, sticky="w")
	cinfo = all_conflicts(submission_data, clist, cyear)
	# output data in 'raw' data format PaperID,Author,ConflictReviewer,Year one item per row.
	odata = cinfo['data']
	clear_feedback()
	if (cinfo['conflict_cnt'] == 0):
		message_lbl["text"] = "No conflicts found"
		message_lbl.grid(column=0, row=0, sticky="ew")
		display_data(submission_data)
	else:
		message_lbl["text"] = "Conflicts exported to output.csv"
		message_lbl.grid(column=0, row=0, sticky="ew")
		# export the raw output data as comma separated values in output.csv
		export_data(odata)
		display_data(odata)

# The same conflict detection as export_conflicts
# But since the input file had a Conflicts column
# output the input file with that column filled in
# as comma separated values to output.csv
def export_plus_conflicts():
	global submission_data
	global Author_cnt
	global Header_row
	global ID_col
	global Conflicts_col
	# we need to re-read the submission file since we have to output all of it.
	indata = verify_read_file(submission_file)
	if ((submission_file == '') or (len(submission_data) == 0) or (len(indata) == 0)):
		return
	clear_feedback()
	clist = read_conflict_list()
	if (len(clist) == 0):
		return
	cyear = get_year()
	Author_cnt = len(submission_data) - Paper_cnt
	progress.grid(column=0, row=0, sticky="w")
	prog_name_lbl.grid(column=2, row=0, sticky="w")
	cinfo = all_conflicts(submission_data, clist, cyear)
	# output data in 'raw' data format PaperID,Author,ConflictReviewer,Year one item per row.
	odata = cinfo['data']
	clear_feedback()
	if (cinfo['conflict_cnt'] == 0):
		message_lbl["text"] = "No conflicts found"
		message_lbl.grid(column=0, row=0, sticky="ew")
		display_data(submission_data)
		return
	message_lbl["text"] = "Submission with conflicts exported to output.csv"
	message_lbl.grid(column=0, row=0, sticky="ew")
	# generate list of papers with a list of reviewer names that have conflicts for each paper
	plist = []
	nlist = []
	for row in odata:
		if (row[0] != ''):
			plist.append(nlist)
			nlist = []
		elif (row[2] != ''):
			nlist.append(row[2])
	plist.append(nlist)
	# above algorithm leaves empty element at beginning of list.  Remove it.
	plist.pop(0)
	pcnt = 0
	# Go through the data, matching each paper ID row to put the
	# conflicting review names in the corrent row of the Conflicts column
	for rindx, rdata in enumerate(indata):
		if (rindx > Header_row):
			if (rdata[ID_col] != ''):
				if (pcnt < len(plist)):
					rdata[Conflicts_col] = ";".join(plist[pcnt])
					pcnt = pcnt + 1
	export_data(indata)
	display_data(odata)

#Build the GUI
input_frame = Frame(window)
input_frame.grid(column=0, row=0, sticky=W)
lbl0 = Label(input_frame, text="Select reviewer data file:", font=("DejaVu Serif", 16))
lbl0.grid(column=0, row=0)
in_btn = Button(input_frame, text="Browse...", font=('', 16), command=reviewer_browse)
in_btn.grid(column=1, row=0)
filename_lbl0 = Label(input_frame, text="No file selected.", font=("fixed", 16))
filename_lbl0.grid(column=2, row=0)

file_frame = Frame(window)
file_frame.grid(column=0, row=1, sticky=W)
lbl = Label(file_frame, text="Select paper submission data file:", font=("DejaVu Serif", 16))
lbl.grid(column=0, row=0)
btn = Button(file_frame, text="Browse...", font=('', 16), command=submission_browse)
btn.grid(column=1, row=0)
filename_lbl = Label(file_frame, text="No file selected.", font=("fixed", 16))
filename_lbl.grid(column=2, row=0)

year_frame = Frame(window)
year_frame.grid(column=0, row=2, sticky=W)
lbl2 = Label(year_frame, text="Cut-off year for conflicts:", font=("DejaVu Serif", 16))
lbl2.grid(column=0, row=0)
year_entry = Entry(year_frame, width=5, font=('', 16))
year_entry.grid(column=1, row=0)

btn_frame = Frame(window)
btn_frame.grid(column=0, row=3, sticky=W)
export_btn = Button(btn_frame, text="Export conflicts(.csv)", font=('', 13), command=export_conflicts)
export_btn.grid(column=0, row=0)
export_cflict_btn = Button(btn_frame, text="Export submission with conflicts(.csv)", font=('', 13), command=export_plus_conflicts)

feedback = Frame(window, bd=10)
feedback.grid(column=0, row=4)
progress = Progressbar(feedback, orient = HORIZONTAL, length = 300, mode = 'determinate') 
prog_name_lbl = Label(feedback, width=25, text="", font=('', 12))
message_lbl = Label(feedback, text="", font=('', 12))

container = Frame(window)
container_ROW = 5
container.grid_columnconfigure(0, weight=1)
canvas = Canvas(container, height=400)
scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas, bd=1, background="black")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.grid(column=0, row=0)


# get the year value from the GUI text field
def get_year():
	entered_yr = year_entry.get()
	try:
		yr = int(entered_yr)
	except ValueError:
		yr = 0
	if (yr < 0):
		yr = 0
	return yr

# strips all whitespace and then joins with the passed character
def format_name(name, sp):
        new1 = sp.join(name.split())
        return(new1)

def add_row(data, row):
        data.append([])
        for entry in row:
                data[-1].append(entry)

# Reads the input file looking for a header row with a column names Conflicts.
# If found it sets globals identifying the header row number, and the column 
# numbers for both the Conflicts column and the Paper ID column
def check_for_conflict_column(fname):
	global Header_row
	global ID_col
	global Conflicts_col
	mtype = mimetypes.MimeTypes().guess_type(fname)[0]
	if (mtype == None):
		clear_feedback()
		message_lbl["text"] = "Invalid file selected"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return 0
	mlist = mtype.split('/')
	if ((mtype == "text/plain") or (mtype == "text/csv")) :
		try:
			with open(fname) as csv_file:
				status = 0
				csv_reader = csv.reader(csv_file, delimiter=',')
				w = 0
				has_conflicts = False # looking for column with Conflicts header
				rindx = 0
				hrow = -1 # looking for the row containing column headers
				for row in csv_reader:
					if (len(row) > w):
						w = len(row)
					cindx = 0
					for entry in row:
						if (hrow < 0):
							if "paper id" in entry.lower():
								# the first row where Paper ID appears
								# is assumed to be the column headers
								hrow = rindx
								ID_col = cindx
						if (hrow == rindx):
							# Already found header row.
							# looking for Conflicts header
							if ("conflicts" == entry.strip().lower()):
								has_conflicts = True
								Conflicts_col = cindx
						cindx = cindx + 1
					rindx = rindx + 1
				if (has_conflicts == True):
					# To have conflicts column must have header row
					status = 3
					Header_row = hrow
				else:
					if (hrow != -1):
						# Have header row, no conflicts column
						status = 2
					else:
						if (w >= 2):
							# No headers but enough columns for raw input
							status = 1
				return status
		except Exception as e:
			clear_feedback()
			message_lbl["text"] = "Invalid file data"
			message_lbl.grid(column=0, row=0, sticky="ew")
			return 0
	elif ((mlist[0] == "application") and ("sheet" in mlist[1])):
		try:
			wbook = xlrd.open_workbook(fname)
			sheet = wbook.sheet_by_index(0)
		except Exception as e:
			clear_feedback()
			message_lbl["text"] = "Invalid file data"
			message_lbl.grid(column=0, row=0, sticky="ew")
			return 0
		has_conflicts = False # looking for column with Conflicts header
		hrow = -1 # looking for the row containing column headers
		status = 0
		for row in range(sheet.nrows):
			for col in range(sheet.ncols):
				val = str(sheet.cell_value(row, col))
				if (hrow < 0):
					if "paper id" in val.lower():
						# the first row where Paper ID appears
						# is assumed to be the column headers
						hrow = row
						ID_col = col
				if (hrow == row):
					# Already found header row.
					# looking for Conflicts header
					if ("conflicts" == val.strip().lower()):
						has_conflicts = True
						Conflicts_col = col
		if (has_conflicts == True):
			# To have conflicts column must have header row
			Header_row = hrow
			status = 3
		else:
			if (hrow != -1):
				# Have header row, no conflicts column
				status = 2
			else:
				if (sheet.ncols >= 2):
					# No headers but enough columns for raw input
					status = 1
		return status
	else:
		clear_feedback()
		message_lbl["text"] = "Incorrect input filetype!"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return 0

# Read the file looking for any reviewer names.
# Along the way determine if the file has a header row so we can look
# for Reviewer column headers, or else just assume a single first column
# of reviewer names.
def check_for_any_names(fname):
	mtype = mimetypes.MimeTypes().guess_type(fname)[0]
	if (mtype == None):
		clear_feedback()
		message_lbl["text"] = "Invalid file selected"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return 0
	mlist = mtype.split('/')
	if ((mtype == "text/plain") or (mtype == "text/csv")) :
		try:
			with open(fname) as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=',')
				w = 0
				h = 0
				c1 = ''
				rcols = []
				hrow = -1 # looking for the row containing column headers
				rindx = 0
				for row in csv_reader:
					if (len(row) > w):
						w = len(row)
					if (c1 == ''):
						# c1 ends up the first non-empty
						# entry in column 0
						c1 = row[0]
					cindx = 0
					for entry in row:
						if (hrow < 0):
							if "reviewer" in entry.lower():
								# the first row where Reviewer appears
								# is assumed to be the column headers
								hrow = rindx
								if "email" not in entry.lower():
									# rcols is the list of all columns
									# with reviewer in there name, but
									# not email.  Catch reviewer,
									# MetaReviewer, etc.
									rcols.append(cindx)
						else:
							if cindx in rcols:
								# if we found at least one reviewer name
								# we can return here.
								if (entry.strip() != ''):
									# print("Name", entry)
									return 2
						cindx = cindx + 1
					rindx = rindx + 1
				h = rindx
				if (hrow == -1) and (c1 != ''):
					# Column 0 is not empty, but there is no header row.
					return 1
				elif (hrow >= 0):
					# We have a header row, but no review names!
					clear_feedback()
					message_lbl["text"] = "No reviewer names in file"
					message_lbl.grid(column=0, row=0, sticky="ew")
					return 0

				return 0
		except Exception as e:
			clear_feedback()
			message_lbl["text"] = "Invalid file data"
			message_lbl.grid(column=0, row=0, sticky="ew")
			return 0
	elif ((mlist[0] == "application") and ("sheet" in mlist[1])):
		try:
			wbook = xlrd.open_workbook(fname)
			sheet = wbook.sheet_by_index(0)
		except Exception as e:
			clear_feedback()
			message_lbl["text"] = "Invalid file data"
			message_lbl.grid(column=0, row=0, sticky="ew")
			return 0

		rcols = []
		c1 = ''
		hrow = -1 # looking for the row containing column headers
		for row in range(sheet.nrows):
			for col in range(sheet.ncols):
				val = str(sheet.cell_value(row, col))
				if (col == 0) and (c1 == ''):
					# c1 ends up the first non-empty
					# entry in column 0
					c1 = val
				if (hrow < 0):
					if "reviewer" in val.lower():
						# the first row where Reviewer appears
						# is assumed to be the column headers
						hrow = row
						if "email" not in val.lower():
							# rcols is the list of all columns
							# with reviewer in there name, but
							# not email.  Catch reviewer,
							# MetaReviewer, etc.
							rcols.append(col)
				else:
					if col in rcols:
						# if we found at least one reviewer name
						# we can return here.
						if (val.strip() != ''):
							# print("Name", val)
							return 2
		if (hrow == -1) and (c1 != ''):
			# Column 0 is not empty, but there is no header row.
			return 1
		elif (hrow >= 0):
			# We have a header row, but no review names!
			clear_feedback()
			message_lbl["text"] = "No reviewer names in file"
			message_lbl.grid(column=0, row=0, sticky="ew")
			return 0
		return 0
	else:
		clear_feedback()
		message_lbl["text"] = "Incorrect input filetype!"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return 0

# Based on mime type, read in all the data from a file as a list of rows each containing a list of columns
def verify_read_file(fname):
	indata = []
	mtype = mimetypes.MimeTypes().guess_type(fname)[0]
	if (mtype == None):
		print("Invalid file selected")
		sys.exit()
#	print('[', mtype, ']', sep='')
	mlist = mtype.split('/')
	if ((mtype == "text/plain") or (mtype == "text/csv")) :
		with open(fname) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				add_row(indata, row)
	elif ((mlist[0] == "application") and ("sheet" in mlist[1])):
		wbook = xlrd.open_workbook(fname)
		sheet = wbook.sheet_by_index(0)
		for row in range(sheet.nrows):
			indata.append([])
			for col in range(sheet.ncols):
				# Trying to prevent paper ID numbers that are ints
				# appearing with .0 because xlsx is all float
				# type 2 is float
				if (sheet.cell_type(row, col) == 2):
					val = int(sheet.cell_value(row, col))
				else:
					val = sheet.cell_value(row, col)
				indata[-1].append(str(val))
	else:
		print("Incorrect input filetype!")
		sys.exit()
	return indata

def display_frame_clear():
	container.grid_forget()
	scrollbar.grid_forget()
	list = scrollable_frame.grid_slaves()
	for l in list:
		l.destroy()

def export_data(data):
	display_frame_clear()
	with open('output.csv', mode='w') as out_file:
		owriter = csv.writer(out_file, delimiter=',')
		for row in data:
			owriter.writerow(row)

def display_data(data):
	display_frame_clear()
	rcnt = 0
	for row in data:
		ccnt = 0
		for entry in row:
			l = Label(scrollable_frame, text=entry, font=('', 12))
			l.grid(row=rcnt, column=ccnt, sticky="nsew", padx=1, pady=1)
			ccnt = ccnt + 1
		rcnt = rcnt + 1
	scrollable_frame.update_idletasks()
	bbox = canvas.bbox("all")
	w = bbox[2] - bbox[0]
	h = bbox[3] - bbox[1]
	canvas.configure(scrollregion=bbox, width=w)
	container.grid(column=0, row=container_ROW)
	if (h > 400):
		scrollbar.grid(column=1, row=0, sticky="ns")

submission_data = []
def simplify_data(data, status):
	global submission_data
	global Paper_cnt
	submission_data = []
	Paper_cnt = 0
	if (status == 1):
		# raw data. Just count the paper ids
		for row in data:
			if (row[0] != ''):
				Paper_cnt = Paper_cnt + 1
		submission_data = data
		return data
	elif ((status == 2) or (status == 3)):
		# we have a header row
		hrow = -1 # looking for the row containing column headers
		name_cols = [] # possibly multiple columns of author names?
		id_col = -1
		for rindx, row in enumerate(data):
			for cindx, entry in enumerate(row):
				if (hrow < 0):
					if "paper id" in entry.lower():
						# the first row where Paper ID appears
						# is assumed to be the column headers
						hrow = rindx
						id_col = cindx
				if (rindx == hrow):
					# Already found header row.
					# looking for Author Names header
					if (("author" in entry.lower()) and ("name" in entry.lower())):
						# Column header looks like author names
						name_cols.append(cindx)
				elif (rindx > hrow):
					if ((cindx == id_col) and (entry != '')):
						# count the papers, and put them in raw data
						add_row(submission_data, [entry, ''])
						Paper_cnt = Paper_cnt + 1
					if cindx in name_cols:
						# may be multiple author names in this entry
						narr = entry.split(';')
						for n in narr:
							na1 = re.split("[,*(]", n)
							# don't add empty names
							if (na1[0].strip() != ''):
								add_row(submission_data, ['', format_name(na1[0], " ")])
		return submission_data
	else:
		return []

reviewer_data = []
def extract_names(ndata):
	global reviewer_data
	# Names are ; separated, but may have institution names attached by commas or parenthesis etc.
	narr = ndata.split(';')
	for n in narr:
		na1 = re.split("[,*(]", n)
		name = format_name(na1[0], " ")
#		name = format_name(n, " ")
		if (name != '') and "@" not in name: #excludes any emails that snuck in
			has_name = False
			for row in reviewer_data:
				if name in row:
					has_name = True
					break
			if (has_name == False):
				# Only add names that are not duplicates
				add_row(reviewer_data, [name])

# Basically like check_for_any_names, but collect them all instead of stopping at the first one
def namify_data(data, status):
	global reviewer_data
	reviewer_data = []
	if (status == 1):
		for row in data:
			entry = row[0]
			extract_names(entry)
	elif (status == 2):
		hrow = -1 # looking for the row containing column headers
		rcols = []
		for rindx, row in enumerate(data):
			found_header = False
			for cindx, entry in enumerate(row):
				if (hrow < 0):
					if "reviewer" in entry.lower():
						# the first row where Reviewer appears
						# is assumed to be the column headers
						found_header = True
						if "email" not in entry.lower():
							# rcols is the list of all columns
							# with reviewer in there name, but
							# not email.  Catch reviewer,
							# MetaReviewer, etc.
							rcols.append(cindx)
				else:
					if cindx in rcols:
						# If this is a reviewer column, collect
						# all names from this entry.
						extract_names(entry)
			if (found_header == True):
				hrow = rindx
	else:
		return []
	return reviewer_data

def clear_feedback():
	message_lbl.grid_forget()
	progress.grid_forget()
	prog_name_lbl.grid_forget()

def review_data(status):
	global submission_data
	clear_feedback()
	if (submission_file == ''):
		return
	message_lbl["text"] = "Data from submissions file"
	message_lbl.grid(column=0, row=0, sticky="ew")
	# read in all data
	indata = verify_read_file(submission_file)
	# convert to 'raw' input data format PaperID,Author one item per row.
	submission_data = simplify_data(indata, status)
	display_data(submission_data)

def review_reviewerdata(status):
	global reviewer_data
	clear_feedback()
	if (reviewer_file == ''):
		return
	message_lbl["text"] = "Data from reviewers file"
	message_lbl.grid(column=0, row=0, sticky="ew")
	# read in all data
	indata = verify_read_file(reviewer_file)
	# convert to 'raw' non-duplicate reviewer names
	reviewer_data = namify_data(indata, status)
	display_data(reviewer_data)

# turn reviewer name spreadsheet data into a simple list of names
def read_conflict_list():
	if (reviewer_file == ''):
		message_lbl["text"] = "No reviewer data"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return []
	conflict_list = []
	for row in reviewer_data:
		for entry in row:
			conflict_list.append(entry)
	return conflict_list

def find_conflicts(name, clist, cyear):
	global Current_author
	# Look up the publication record of the passed name in the DBLP database
	url = "https://dblp.org/search/publ/api?q=author%3A" + name + "%3A&h=1000&format=json"
	# print(url)
	response = urllib.request.urlopen(url)
	if (response.getcode() != 200):
		return({})
	url_resp = response.read()
	data = json.loads(url_resp.decode('utf-8'))
	# Drill down in the data structure returned to find the list of papers
	hit_cnt = data['result']['hits']['@total']
	if (int(hit_cnt) < 1):
		return({})
	hit_list = data['result']['hits']['hit']
	cons = {}
	hit_indx = 0
	for hit_data in hit_list:
		auth_list = hit_data['info']['authors']['author']
		year = hit_data['info']['year']
		# Drill down in the paper data structure for year and author names
		if (int(year) >= cyear):
			# This field can be an array of entries, or a single entry
			if isinstance(auth_list, list):
				for auth_entry in auth_list:
					auth_name = auth_entry['text']
					if (auth_name in clist):
						if (auth_name in cons):
							cons[auth_name].append(year)
						else:
							cons[auth_name] = []
							cons[auth_name].append(year)
			else:
				auth_name = auth_list['text']
				if (auth_name in clist):
					if (auth_name in cons):
						cons[auth_name].append(year)
					else:
						cons[auth_name] = []
						cons[auth_name].append(year)
		# Update progress bar
		pp = 100 * hit_indx / int(hit_cnt)
		if (pp < 2):
			pp = 2
		show_progress(Current_author, pp, '*')
		hit_indx = hit_indx + 1
	return(cons)

def show_progress(cauthor, type, name):
	global Author_cnt
	max = progress["maximum"]
	if (type == 0):
		p = 100 * (cauthor - 1) / Author_cnt
	elif (type == 1):
		p = 100 * cauthor / Author_cnt
	else:
		step = 100 * 1 / Author_cnt
		p = 100 * (cauthor - 1) / Author_cnt
		p = p + (type * step / 100)
	progress["value"] = p
	if (name != '*'):
		prog_name_lbl["text"] = name
	window.update_idletasks()
#	window.after(10)

# Raw data:
# Column 0: Paper ID or ''
# Column 1: Author Name or ''
# Column 2: Reviewer Conflict  or ''
# Column 3: Year of Conflict  or ''
def all_conflicts(data, clist, cyear):
	global Current_author
	outdata = []
	ccnt = 0
	Current_author = 1
	for row in data:
		add_row(outdata, [row[0], row[1], '', ''])
		if row[1] != '':
			show_progress(Current_author, 0, format_name(row[1], "_"))
			cdict = find_conflicts(format_name(row[1], "_"), clist, cyear)
			for cname in clist:
				if (cname in cdict):
					ccnt = ccnt + 1
					add_row(outdata, ['', '', cname, ''])
					for date in cdict[cname]:
						add_row(outdata, ['', '', '', date])
			show_progress(Current_author, 1, '*')
			Current_author = Current_author + 1
	return {'data':outdata, 'conflict_cnt':ccnt}


window.mainloop()

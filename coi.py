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


def submission_browse():
	global submission_file
	display_frame_clear()
	clear_feedback()
	export_cflict_btn.grid_forget()
	file = filedialog.askopenfilename(filetypes = (("Comma separated values","*.csv"),("spreadsheet","*.xlsx")))
	if (file != ''):
		status = check_for_conflict_column(file)
		if (status == 0):
			submission_file = ''
			filename_lbl.configure(text='No file selected.')
			return
		if (status == 1):
			export_cflict_btn.grid_forget()
		if (status == 2):
			export_cflict_btn.grid(column=3, row=0)
		submission_file = file
		fp = submission_file.split('/')
		filename_lbl.configure(text=fp[-1])
		review_data()

def reviewer_browse():
	global reviewer_file
	display_frame_clear()
	clear_feedback()
	file = filedialog.askopenfilename(filetypes = (("Comma separated values","*.csv"),("spreadsheet","*.xlsx")))
	if (file != ''):
		status = check_for_any_names(file)
		if (status == 0):
			reviewer_file = ''
			filename_lbl0.configure(text='No file selected.')
			return
		reviewer_file = file
		fp = reviewer_file.split('/')
		filename_lbl0.configure(text=fp[-1])
		review_reviewerdata(status)

def export_conflicts():
	global simple_data
	global Author_cnt
	if (submission_file == ''):
		message_lbl["text"] = "No submission data"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return
	clear_feedback()
	indata = verify_read_file(submission_file)
	simple_data = simplify_data(indata)
	clist = read_conflict_list()
	if (len(clist) == 0):
		return
	cyear = get_year()
	Author_cnt = len(simple_data) - Paper_cnt
	progress.grid(column=0, row=0, sticky="ew")
	cinfo = all_conflicts(simple_data, clist, cyear)
	odata = cinfo['data']
	clear_feedback()
	if (cinfo['conflict_cnt'] == 0):
		message_lbl["text"] = "No conflicts found"
		message_lbl.grid(column=0, row=0, sticky="ew")
		display_data(simple_data)
	else:
		message_lbl["text"] = "Conflicts exported to output.csv"
		message_lbl.grid(column=0, row=0, sticky="ew")
		export_data(odata)
		display_data(odata)

def export_plus_conflicts():
	global simple_data
	global Author_cnt
	if (submission_file == ''):
		return
	clear_feedback()
	indata = verify_read_file(submission_file)
	simple_data = simplify_data(indata)
	clist = read_conflict_list()
	cyear = get_year()
	Author_cnt = len(simple_data) - Paper_cnt
	progress.grid(column=0, row=0, sticky="ew")
	cinfo = all_conflicts(simple_data, clist, cyear)
	odata = cinfo['data']
	clear_feedback()
	if (cinfo['conflict_cnt'] == 0):
		message_lbl["text"] = "No conflicts found"
		message_lbl.grid(column=0, row=0, sticky="ew")
		display_data(simple_data)
		return
	message_lbl["text"] = "Submission with conflicts exported to output.csv"
	message_lbl.grid(column=0, row=0, sticky="ew")
#	export_data(odata)
	plist = []
	nlist = []
	for row in odata:
		if (row[0] != ''):
			plist.append(nlist)
			nlist = []
		elif (row[2] != ''):
			nlist.append(row[2])
	plist.append(nlist)
	plist.pop(0)
	for rindx, rdata in enumerate(indata):
		if (rindx >= 3):
			rdata[10] = ";".join(plist[rindx - 3])
	export_data(indata)
	display_data(odata)

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
progress = Progressbar(feedback, orient = HORIZONTAL, length = 500, mode = 'determinate') 
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





def get_year():
	entered_yr = year_entry.get()
	try:
		yr = int(entered_yr)
	except ValueError:
		yr = 0
	if (yr < 0):
		yr = 0
	return yr


# progress.grid(column=0, row=0, sticky="ew")



def format_name(name, sp):
        new1 = sp.join(name.split())
        return(new1)

def add_row(data, row):
        data.append([])
        for entry in row:
                data[-1].append(entry)

def check_for_conflict_column(fname):
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
				rindx = 0
				for row in csv_reader:
					if (len(row) < 2):
						has_column = 0
						break
					if (len(row) < 11):
						has_column = 1
						break
					if (rindx == 2):
						if (row[10] == "Conflicts"):
							has_column = 2
							break
						else:
							has_column = 1
							break
					rindx = rindx + 1
				return has_column
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
		if (sheet.nrows < 3) or (sheet.ncols < 11):
			has_column = 1
		elif (sheet.cell_value(2, 10) == "Conflicts"):
			has_column = 2
		else:
			has_column = 1
		return has_column
	else:
		clear_feedback()
		message_lbl["text"] = "Incorrect input filetype!"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return 0

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
				hrow = -1
				rindx = 0
				for row in csv_reader:
					if (len(row) > w):
						w = len(row)
					if (c1 == ''):
						c1 = row[0]
					cindx = 0
					for entry in row:
						if (hrow < 0):
							if "reviewer" in entry.lower():
								hrow = rindx
								if "email" not in entry.lower():
									rcols.append(cindx)
						else:
							if cindx in rcols:
								if (entry != ''):
									return 2
						cindx = cindx + 1
					rindx = rindx + 1
				h = rindx
				if (hrow == -1) and (c1 != ''):
					return 1
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
		hrow = -1
		for row in range(sheet.nrows):
			for col in range(sheet.ncols):
				val = str(sheet.cell_value(row, col))
				if (col == 0) and (c1 == ''):
					c1 = val
				if (hrow < 0):
					if "reviewer" in val.lower():
						hrow = row
						if "email" not in val.lower():
							rcols.append(col)
				else:
					if col in rcols:
						if (val != ''):
							return 2
		if (hrow == -1) and (c1 != ''):
			return 1
		return 0
	else:
		clear_feedback()
		message_lbl["text"] = "Incorrect input filetype!"
		message_lbl.grid(column=0, row=0, sticky="ew")
		return 0

def verify_read_file(fname):
	global Paper_cnt
	Paper_cnt = 0
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
				if (row[0] != ''):
					Paper_cnt = Paper_cnt + 1
				add_row(indata, row)
	elif ((mlist[0] == "application") and ("sheet" in mlist[1])):
		wbook = xlrd.open_workbook(fname)
		sheet = wbook.sheet_by_index(0)
		for row in range(sheet.nrows):
			indata.append([])
			if (sheet.cell_value(row, 0) != ''):
				Paper_cnt = Paper_cnt + 1
			for col in range(sheet.ncols):
				# type 2 is float
				if (sheet.cell_type(row, col) == 2):
					val = int(sheet.cell_value(row, col))
				else:
					val = sheet.cell_value(row, col)
				indata[-1].append(val)
	else:
		print("Incorrect input filetype!")
		sys.exit()
	return indata

def verify_read_reviewerfile(fname):
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

simple_data = []
def simplify_data(data):
	global Paper_cnt
	if (data[2][0] == "Paper ID"):
		Paper_cnt = 0
		sdata = []
		for rindx, rdata in enumerate(data):
			if (rindx >= 3):
				add_row(sdata, [rdata[0], ''])
				Paper_cnt = Paper_cnt + 1
				narr = rdata[5].split(';')
				for n in narr:
					na1 = re.split("[,*(]", n)
					add_row(sdata, ['', format_name(na1[0], " ")])
		return sdata
	else:
		return data

reviewer_data = []
def extract_names(ndata):
	global reviewer_data
	narr = ndata.split(';')
	for n in narr:
		na1 = re.split("[,*(]", n)
		name = format_name(na1[0], " ")
#		name = format_name(n, " ")
		if (name != '') and "@" not in name:
			has_name = False
			for row in reviewer_data:
				if name in row:
					has_name = True
					break
			if (has_name == False):
				add_row(reviewer_data, [name])

def namify_data(data, status):
	global reviewer_data
	reviewer_data = []
	if (status == 1):
		for row in data:
			entry = row[0]
			extract_names(entry)
	elif (status == 2):
		hrow = -1
		rcols = []
		for rindx, row in enumerate(data):
			found_header = False
			for cindx, entry in enumerate(row):
				if (hrow < 0):
					if "reviewer" in entry.lower():
						found_header = True
						if "email" not in entry.lower():
							rcols.append(cindx)
				else:
					if cindx in rcols:
						extract_names(entry)
			if (found_header == True):
				hrow = rindx
	else:
		return []
	return reviewer_data

def clear_feedback():
	message_lbl.grid_forget()
	progress.grid_forget()

def review_data():
	global simple_data
	clear_feedback()
	if (submission_file == ''):
		return
	message_lbl["text"] = "Data from submissions file"
	message_lbl.grid(column=0, row=0, sticky="ew")
	indata = verify_read_file(submission_file)
	simple_data = simplify_data(indata)
	display_data(simple_data)

def review_reviewerdata(status):
	global reviewer_data
	clear_feedback()
	if (reviewer_file == ''):
		return
	message_lbl["text"] = "Data from reviewers file"
	message_lbl.grid(column=0, row=0, sticky="ew")
	indata = verify_read_reviewerfile(reviewer_file)
	reviewer_data = namify_data(indata, status)
	display_data(reviewer_data)

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
	url = "https://dblp.org/search/publ/api?q=author%3A" + name + "%3A&h=1000&format=json"
#	print(url)
	response = urllib.request.urlopen(url)
	if (response.getcode() != 200):
		return({})
	url_resp = response.read()
	data = json.loads(url_resp.decode('utf-8'))
	hit_cnt = data['result']['hits']['@total']
	if (int(hit_cnt) < 1):
		return({})
	hit_list = data['result']['hits']['hit']
	cons = {}
	hit_indx = 0
	for hit_data in hit_list:
		auth_list = hit_data['info']['authors']['author']
		year = hit_data['info']['year']
		if (int(year) >= cyear):
			if isinstance(auth_list, list):
				for auth_name in auth_list:
					if (auth_name in clist):
						if (auth_name in cons):
							cons[auth_name].append(year)
						else:
							cons[auth_name] = []
							cons[auth_name].append(year)
			else:
				if (auth_list in clist):
					if (auth_list in cons):
						cons[auth_list].append(year)
					else:
						cons[auth_list] = []
						cons[auth_list].append(year)
		pp = 100 * hit_indx / int(hit_cnt)
		if (pp < 2):
			pp = 2
		show_progress(Current_author, pp)
		hit_indx = hit_indx + 1
	return(cons)

def show_progress(cauthor, type):
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
	window.update_idletasks()
#	window.after(10)

def all_conflicts(data, clist, cyear):
	global Current_author
	outdata = []
	ccnt = 0
	Current_author = 1
	for row in data:
		add_row(outdata, [row[0], row[1], '', ''])
		if row[1] != '':
			show_progress(Current_author, 0)
			cdict = find_conflicts(format_name(row[1], "_"), clist, cyear)
			for cname in clist:
				if (cname in cdict):
					ccnt = ccnt + 1
					add_row(outdata, ['', '', cname, ''])
					for date in cdict[cname]:
						add_row(outdata, ['', '', '', date])
			show_progress(Current_author, 1)
			Current_author = Current_author + 1
	return {'data':outdata, 'conflict_cnt':ccnt}

def view_conflicts():
	global simple_data
	global Author_cnt
	if (submission_file == ''):
		return
	clear_feedback()
	indata = verify_read_file(submission_file)
	simple_data = simplify_data(indata)
	clist = read_conflict_list()
	cyear = get_year()
	Author_cnt = len(simple_data) - Paper_cnt
	progress.grid(column=0, row=0, sticky="ew")
	cinfo = all_conflicts(simple_data, clist, cyear)
	odata = cinfo['data']
	clear_feedback()
	message_lbl["text"] = "Data and conflicts shown"
	message_lbl.grid(column=0, row=0, sticky="ew")
	display_data(odata)


window.mainloop()

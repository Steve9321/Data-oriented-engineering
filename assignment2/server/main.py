import xlrd
from collections import defaultdict
from mongoengine import connect
from flask_restful import reqparse
import requests
from postcode import Offence, Data
from flask import Flask, jsonify, render_template, request
from werkzeug.contrib.atom import AtomFeed, FeedEntry
from datetime import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
from auth import SECRET_KEY, admin_required, login_required
import urllib.request
from flask_cors import CORS

connect(host = 'mongodb://aa:0987654321a@ds127531.mlab.com:27531/ass2database')
addr = "http://www.bocsar.nsw.gov.au/Documents/RCS-Annual/"
app = Flask(__name__)

collections = defaultdict(list)
L = []

CORS(app)

def read_collection():
    r = requests.get(
        'https://docs.google.com/spreadsheets/d/1tHCxouhyM4edDvF60VG7nzs5QxID3ADwr3DGJh71qFg/export?format=xlsx&id=1tHCxouhyM4edDvF60VG7nzs5QxID3ADwr3DGJh71qFg')
    file = '/Users/user/Desktop/Australian LGA postcode mappings (2011 data).xlsx'
    with open(file, 'wb') as f:
        f.write(r.content)#download the postcode file and write it on desktop
    workbook = xlrd.open_workbook('/Users/user/Desktop/Australian LGA postcode mappings (2011 data).xlsx')
    worksheet = workbook.sheet_by_name('lga_postcode_mappings')
    num_rows = worksheet.nrows - 1
    curr_row = 1
    while curr_row < num_rows and worksheet.cell_value(curr_row, 0)=="New South Wales":
        postcode = worksheet.cell_value(curr_row, 2)
        region = worksheet.cell_value(curr_row, 1)
        curr_row += 1
        L.append((postcode,region))
    for k, v in L:
        collections[k].append(v)#store all the data of NSW into dictionary

def url_is_alive(url): #check this url is valid
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'
    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

@app.route("/createlga", methods=['POST'])
# @admin_required
def import_LGA():
    parser = reqparse.RequestParser() #create the document by the region name
    parser.add_argument('region', type=str)
    args = parser.parse_args()
    region = request.form.get("region")# get the attribute of region
    region1 = region.replace(" ", "").lower()
    url = addr + region1 + 'lga.xlsx'
    file = '/Users/user/Desktop/' + region + 'lga.xlsx'
    r = requests.get(url) # get the request of getting the url
    if not url_is_alive(url): #check whether the url exists
        return 'Not found'
    with open(file, 'wb') as f: #write the file on the desktop
        f.write(r.content)
    id = region
    scan_file(file,region,id)
    string = rss_feed(region)
    return jsonify(string), 200
   # return render_template("ATOM.html")
 #   return 201, jsonify("Created")

@app.route("/createpostcode", methods=['POST'])
#@admin_required
def import_code():  #create the document by the postcode
    parser = reqparse.RequestParser()
    parser.add_argument('postcode', type=int)
    args = parser.parse_args()
    postcode = args.get("postcode") # get the attribute of postcode
    line = collections[int(postcode)]
    string, n = '', 0
    for e in line:
        if check_exist(e):
            n += 1
            #         The file has already been existed!
            continue
        e1 = e.replace(" ", "").lower()
        file = '/Users/user/Desktop/' + e + 'lga.xlsx'
        url = addr + e1 + 'lga.xlsx'
        r = requests.get(url)
        if not url_is_alive(url):
            continue
        with open(file, 'wb') as f:
            f.write(r.content)
        id = e
        scan_file(file, e, id)
        string += rss_feed(e)
    return jsonify(string), 200

def scan_file(file,e,id):
    excel = xlrd.open_workbook(file)
    worksheet = excel.sheet_by_name('Summary of offences')#open the excel file and select the sheet named Summary of offences
    rows = worksheet.nrows - 1
    columns = worksheet.ncols - 1#get the column number of the sheet
    curr_row = 5#start from the sixth row
    s = []
    while curr_row < 69:
        L = []
        curr_col = 0
        while curr_col<= columns:
            cell_value = worksheet.cell_value(curr_row, curr_col)
            L.append(str(cell_value))
            curr_col+=1
        s.append(L)
        curr_row += 1
    d = []
    for i in range(len(s)):
        a = Data(s[i][0],s[i][1],s[i][2],s[i][3],s[i][4],s[i][5],s[i][6],s[i][7],s[i][8],s[i][9],s[i][10],s[i][11],s[i][12],s[i][13],s[i][14])
        Offence(id,e,d.append(a))
    t = Offence(id,e,d)
    connect('statistics')
    t.save()

@app.route("/getall", methods=['GET'])
# @login_required
def get_collection():
    connect('statistics')
    output, id = {}, []
    for t in Offence.objects:
        id.append(t.id)
    entry = FeedEntry(id = id ,title='all collections', updated=datetime.now(), author='Steve')
    return entry.to_string()

@app.route("/getall_json", methods=['GET'])
# @login_required
def get_collection_json():
    connect('statistics')
    output, id = dict(), []
    for t in Offence.objects:
        id.append(t.id)
    for i in range(len(id)):
        output[i+1] = id[i]
    return jsonify(output), 200
    # return jsonify(' '.join(id)), 200


@app.route("/getinfo", methods=['GET'])
# @login_required
def getinfo():#get the whole content of one region
    parser = reqparse.RequestParser()
    parser.add_argument('region', type=str)
    args = parser.parse_args()
    region = request.args.get("region")
    connect('statistics')#connect with mlab
    result = content_feed(region)#get the freeentry of the result
    return result

    return jsonify('OK'), 200

@app.route("/getinfo_json", methods=['GET'])
# @login_required
def get_info():#get the json of a region's whole information
    parser = reqparse.RequestParser()
    parser.add_argument('region', type=str)
    args = parser.parse_args()
    region = request.args.get("region")
    connect('statistics')
    L = []
    for t in Offence.objects(id=region):
        for e in t.data:
            L.append(' '.join([e.offence, e.type, e.data1, e.data2, e.data3, e.data4, e.data5, e.data6, e.data7, e.data8,
                      e.data9, e.data10, e.data11, e.data11, e.data13]))
    return ' '.join(L)

    return jsonify('OK'), 200

@app.route("/filter", methods=['GET'])
# @login_required
def getcoloumn():# get the column of one region in one year
    parser = reqparse.RequestParser()
    parser.add_argument('area', type=str)
    parser.add_argument('year', type =str)
    args = parser.parse_args()
   # region = request.form.get("area")
    region = args.get("area")
 #   year = request.form.get("year")
    year = args.get('year')
    connect('statistics')
    result = content_col(region,year)
    return result

@app.route("/filter_json", methods=['GET'])
# @login_required
def get_coloumn():#get the json of one place in one year
    parser = reqparse.RequestParser()
    parser.add_argument('area', type=str)
    parser.add_argument('year', type =str)
    args = parser.parse_args()
   # region = request.form.get("area")
    region = args.get("area")
 #   year = request.form.get("year")
    year = args.get('year')
    connect('statistics')
    L, index = [], 0
    output = []
    for t in Offence.objects(id=region):
        for e in t.data:
            L.append([e.offence, e.type, e.data1, e.data2, e.data3, e.data4, e.data5, e.data6, e.data7, e.data8,
                      e.data9, e.data10, e.data11, e.data11, e.data13])
    for e in L[0]:
        if year in e:
            index = L[0].index(e)
    for line in L:
        output.append(' '.join([line[0], line[1], line[index], line[index + 1]]))
    return ' '.join(output)

@app.route("/delete", methods=['POST'])
# @admin_required
def delete():#delete the document on mlab
    parser = reqparse.RequestParser()
    parser.add_argument('nameDelete', type=str)
    args = parser.parse_args()
    id = request.form.get("nameDelete")
    connect('statistics')#connect with malb
    item = Offence.objects(id=id).first()#find the object of which id is the same as input
    item.delete()#delete the items
    return jsonify(Region = id), 200

def rss_feed(district):# the feedback of creating one document
	entry = FeedEntry(id = addr+district,
                      title = district+'_detail',
                      updated = datetime.now(),
                      author = 'Zhuowen Deng',)
	return entry.to_string()

def content_feed(region):#the detail of the region
    L =[]
    for t in Offence.objects(id=region):
        for e in t.data:
            L.append([e.offence,e.type,e.data1,e.data2,e.data3,e.data4,e.data5,e.data6,e.data7,e.data8,
                  e.data9,e.data10,e.data11,e.data11,e.data13])
    entry = FeedEntry(id = addr+region,title = region+'detail',updated = datetime.now(),author = 'Zhuowen Deng',content = L)
    return entry.to_string()

def content_col(region, year):#the column info of one region in one year
    L,index = [], 0
    output = []
    for t in Offence.objects(id=region):
        for e in t.data:
            L.append([e.offence,e.type,e.data1,e.data2,e.data3,e.data4,e.data5,e.data6,e.data7,e.data8,
                  e.data9,e.data10,e.data11,e.data11,e.data13])
    for e in L[0]:
        if year in e :
            index = L[0].index(e)
    for line in L:
        output.append([line[0],line[1],line[index],line[index+1]])
    entry = FeedEntry(id=addr + region, title=region+'_detail', updated=datetime.now(), author='Zhuowen Deng', content=output)
    return entry.to_string()

def check_exist(id):
    return bool(Offence.objects(id=id))


@app.route("/auth", methods=['GET'])#authenticcation
def generate_token():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str)
    parser.add_argument('password', type=str)
    args = parser.parse_args()
    username = args.get("username")
    # username = request.form.get("username")
    password = args.get("password")
    # password = request.form.get("password")

    s = Serializer(SECRET_KEY, expires_in=600)
    token = s.dumps(username)
    if username == 'admin' and password == 'admin':
        return jsonify({'token':token.decode()}),200
    if username == 'guest' and password == 'guest':
        return jsonify({'token': token.decode()}),200
    return '',500

if __name__ =='__main__':
    read_collection()
    app.run()

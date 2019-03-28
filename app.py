from flask import Flask, request
from cassandra.cluster import Cluster
import requests

cluster = Cluster(['cassandra'])
session = cluster.connect()
app = Flask(__name__)

#this function aims to create the database in cassandra by grab the data from UK POLICE API in a sepecific month
@app.route('/<mydata>', methods=['GET'])
def hello(mydata):
    crime_url_template ='https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={lng}&date={data}'
    my_latitude = '51.52369'               
    my_longitude = '-0.0395857'
    crime_url = crime_url_template.format(lat = my_latitude,lng = my_longitude,data = mydata) #pass the parameter to the request
    resp = requests.get(crime_url)
    if resp.ok:
        crimes = resp.json()
    else:
        print(resp.reason)
    categories_url_template = 'https://data.police.uk/api/crime-categories?date={date}'
    resp = requests.get(categories_url_template.format(date = mydata))
    if resp.ok:
        categories_json = resp.json()
    else:
        print(resp.reason)

    categories = {categ["url"]:categ["name"] for categ in categories_json}
    crime_category_stats = dict.fromkeys(categories.keys(), 0)
    crime_category_stats.pop("all-crime")
    for crime in crimes:
        crime_category_stats[crime["category"]] += 1
    for key in crime_category_stats:
        rows = session.execute( """insert into crime.category(month,name,count) values('{}','{}',{})""".format(mydata,key,crime_category_stats[key]))
    return('<h1>crime data for {} is created</h1>'.format(mydata))

@app.route('/<data>/<name>', methods=['GET'])
def profile(data,name):
    rows = session.execute( """select * from crime.category where month = '{}' and name= '{}' allow filtering""".format(data,name))
    for crime in rows:
        return('<h1>{} in {} happened {} times!</h1>'.format(name, data, crime.count))
    return('<h1>That kind of crime does not exist!</h1>')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

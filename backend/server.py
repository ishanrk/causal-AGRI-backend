
from flask import Flask, request, jsonify

from dowhy import gcm
import json

import networkx as nx, numpy as np, pandas as pd

import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
from flask_cors import CORS

import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

#enter username and apssword for your mongodb database

username = userNmae
password = passWord

mongoString = 'mongodb+srv://' + username + ':' + password + '@causalai.p6ds6oh.mongodb.net/'

app = Flask(__name__)
CORS(app)

def upload_data(data_row):
    client = MongoClient(mongoString)
# Send a ping to confirm a successful connection

    db = client['agriculture_data']
    collection = db['Agriculture']

    collection.insert_one(data_row)

    client.close()



def get_data():
    client = MongoClient(mongoString)
# Send a ping to confirm a successful connection

    db = client['agriculture_data']
    collection = db['Agriculture']

# Retrieve all data from MongoDB and convert to DataFrame
    query = {}  # Empty query to retrieve all documents
    cursor = collection.find(query)
    df = pd.DataFrame(list(cursor))

    df=df.drop('_id',axis=1)

    client.close()

    return df

@app.route('/get_row', methods=['POST'])
def get_row():
    data = request.json
    print(data)
    values = int(data['index'])
    df = get_data()
    df_row= df.iloc[values]
    print(df_row)

    return jsonify(df_row.to_dict())



@app.route('/submit_data', methods=['POST'])
def inp():
    data = request.json
    data['index'] = max(get_data()['index'])+1
    print(data)
    client = MongoClient(mongoString)
# Send a ping to confirm a successful connection

    db = client['agriculture_data']
    collection = db['Agriculture']
    for key, value in data.items():
        # Check if the value is a string containing only numbers
      if not(isinstance(value,int)):
        if not ((isinstance(value, str)) and value.isdigit()):
            return jsonify({'Ans':False,'ind':-1})
        data[key]=float(value)
        
    collection.insert_one(data)
    print("yes happened", data['index'])
    return jsonify({'Ans':True,'ind':data['index']})


@app.route('/predict', methods=['POST'])
def cf_predict():
    try:
        data = request.json
        values = data['currentList']
        print(values)
       
        training_data = get_data()
        
        # Perform multiplication logic here
        

        causal_model = gcm.InvertibleStructuralCausalModel(get_causal_graph()) 
        gcm.auto.assign_causal_mechanisms(causal_model, training_data)
        gcm.fit(causal_model, training_data)

        predict_dict={}
        sample_dict={'Fertilizer(kg/acre)':False, 'PlantationMonth':False, 'Humidity(%)':False, 'Temperature(C)':False}

        for key in values:
            if(key in sample_example() and values[key]!="-"):
                sample_dict[key]=int(values[key])
       
        
                
        
        pred=gcm.counterfactual_samples(
        causal_model,
        { 'Expected' : lambda x : x,
            'Irrigation' : lambda x :x, 'CropType' : lambda x :x, 
            'Pest' : lambda x :x, 'Temperature(C)' : lambda x:x if sample_dict['Temperature(C)']==False else sample_dict['Temperature(C)'],'PlantationMonth' : lambda x:x if sample_dict['PlantationMonth']==False else sample_dict['PlantationMonth'],
            'Rainfall(cm)' : lambda x:x,
            'SoilSalinity' : lambda x:x,'Fertilizer(kg/acre)' :lambda x:x if sample_dict['Fertilizer(kg/acre)']==False else sample_dict['Fertilizer(kg/acre)'],
            'Disease' :lambda x:x,'Humidity(%)' : lambda x:x if sample_dict['Humidity(%)']==False else sample_dict['Humidity(%)'], 'Light(Lumens)': lambda x:x
             },observed_data=training_data)
      
        print("pred data")
        print(pred)
        print("training_data")
        print(training_data)
       
        return jsonify({"ActualYield":round(pred['Actual'][float(values['index'])],3)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400



def sample_example():
    sample  = {
    'Expected': 25,
    'Irrigation': 1,
    'CropType': 0,
    'Pest': 0,
    'Temperature(C)': 25.5,
    'PlantationMonth': 1,
    'Rainfall(cm)': 30.0,
    'SoilSalinity': 1,
    'Fertilizer(kg/acre)': 200,
    'Disease': 1,
    'Humidity(%)': 60,
    'Light(lumens)': 35000,
    'FarmNum':40
    }
    return sample

def get_causal_graph():
    causal_graph = nx.DiGraph([

    ('CropType','Irrigation'),
    ('CropType','Disease'),
    ('Disease','Actual'),
    ('CropType','PlantationMonth'),
    ('Expected','Actual'),
    ('Temperature(C)','Humidity(%)'),
    ('Rainfall(cm)','Humidity(%)'),
    ('SoilSalinity','pH'),
    ('Irrigation','Expected'),
    ('Humidity(%)','Actual'),
    ('pH','Actual'),
    ('Light(Lumens)','Disease'),
    ('Light(Lumens)','Pest'),

    ('Pest','Actual'),
    ('Fertilizer(kg/acre)','Actual'),
    ('Fertilizer(kg/acre)','pH')
    ,
    ('SoilTemp','Humidity(%)')
    ,
    ('Expected','Actual'),
    ('PlantationMonth','Actual'),
    ('PlantationMonth','Expected'),

    ('Disease','Actual')])


    fig = plt.figure(figsize=(15, 8))  # set figsize
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor("#001521")  # set backgrount

    pos = nx.drawing.layout.circular_layout(causal_graph)

    nx.draw_networkx_nodes(
    causal_graph,
    pos,
    node_shape="H",
    node_size=1000,
    linewidths=3,
    edgecolors="#4a90e2d9",
    node_color=["black"],
    )
    # add labels
    nx.draw_networkx_labels(
    causal_graph,
    pos,
    font_color="#FFFFFFD9",
    font_weight="bold",
    
    font_size=10,
    )
    # add edges
    nx.draw_networkx_edges(
    causal_graph,
    pos,
    edge_color="white",
    node_shape="H",
    node_size=2000,
    
    width=[1],
    )
    return causal_graph

"""
@app.route('/optimize_fertilizer', methods=['POST'])
def optimize_fertilizer():
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid input. Please provide a dictionary.")

        causal_model = gcm.InvertibleStructuralCausalModel(get_causal_graph) 
        gcm.auto.assign_causal_mechanisms(causal_model, training_data)
        gcm.fit(causal_model, training_data)
        j = 1
        max1 = 0

        fertmax = 0
        y = data["FarmNum"]
        fert=training_data['Fertilizer(kg/acre)'][y]-50
        while(j<=10):
            pred=gcm.counterfactual_samples(
            causal_model,
            { 'Expected' : lambda x : x,
            'Irrigation' : lambda x :x, 'CropType' : lambda x :x, 
            'Pest' : lambda x :x, 'Temperature(C)' : lambda x:x,'PlantationMonth' : lambda x:x,
            'Rainfall(cm)' : lambda x:x,
            'SoilSalinity' : lambda x:'1','Fertilizer(kg/acre)' :lambda x:fert+j*10,
            'Disease' :lambda x:x,'Humidity(%)' : lambda x:x-50, 'Light(Lumens)': lambda x:x
             }   ,observed_data=training_data)
            
            if(pred['Actual'][x]>=max1):
                max1 = pred['Actual'][y]
                fertmax = fert+j*10
            j+=1
        return jsonify({"OptimalFertilizer":fertmax,"MaxYield":max1})

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/optimize_month', methods=['POST'])
def optimize_month():
    try:
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid input. Please provide a dictionary.")

        causal_model = gcm.InvertibleStructuralCausalModel(get_causal_graph()) 
        gcm.auto.assign_causal_mechanisms(causal_model, training_data)
        gcm.fit(causal_model, training_data)
        
        j = 1
        max1 = 0
        mon =0
        x = int(input("Enter farm number"))
        while(j<13):
            pred=gcm.counterfactual_samples(
            causal_model,
            { 'Expected' : lambda x : x,
            'Irrigation' : lambda x :x, 'CropType' : lambda x :x, 
            'Pest' : lambda x :x, 'Temperature(C)' : lambda x:x,'PlantationMonth' : lambda x:j,
            'Rainfall(cm)' : lambda x:x,
             'SoilSalinity' : lambda x:x,'Fertilizer(kg/acre)' :lambda x:x,
             'Disease' :lambda x:x,'Humidity(%)' : lambda x:x, 'Light(Lumens)': lambda x:x
            },observed_data=training_data)
    
            if(pred['Actual'][x]>=max1):
                max1 = pred['Actual'][x]
                mon =j
        
            j+=1
        return jsonify({"OptimalMonth":mon,"MaxYield":max1})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/counterfactual_predict', methods=['POST'])
def predict_endpoint():
    try:
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid input. Please provide a dictionary.")

        causal_model = gcm.InvertibleStructuralCausalModel(get_causal_graph()) 
        gcm.auto.assign_causal_mechanisms(causal_model, training_data)
        gcm.fit(causal_model, training_data)
        
        pred=gcm.counterfactual_samples(
        causal_model,
        { 
            'Expected' : lambda x : data['Expected'],
          'Irrigation' : lambda x :data['Irrigation'], 'CropType' : lambda x :data['CropType'], 
          'Pest' : lambda x :data['Pest'], 'Temperature(C)' : lambda x:data['Temperature(C)'],'PlantationMonth' : lambda x:data['PlantationMonth'],
          'Rainfall(cm)' : lambda x:data['Rainfall(cm)'],
         'SoilSalinity' : lambda x:data['SoilSalinity'],'Fertilizer(kg/acre)' :lambda x:data['Fertilizer'],
           'Disease' :lambda x:data['Disease'],'Humidity(%)' : lambda x:data['Humidity'], 'Light(Lumens)': lambda x:data['Light(lumens)']
        },observed_data=training_data)
        return jsonify({"ActualYield":pred['Actual'][data['FarmNum']]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


"""
if __name__ == '__main__':
    app.run(debug=True)

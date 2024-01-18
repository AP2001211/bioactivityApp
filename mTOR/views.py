import subprocess
import os
import base64
import pickle
import pandas as pd
# from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse



def upload_file_view(request):
    return render(request, 'mTOR.html')

# Molecular descriptor calculator
def desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar /Users/apoorvav/bioactivityApp/mTOR/data/PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes /Users/apoorvav/bioactivityApp/mTOR/data/PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Model building
def build_model(input_data, load_data):
    # Reads in saved regression model
    load_model = pickle.load(open('/Users/apoorvav/bioactivityApp/mTOR/data/mTOR_model.pkl', 'rb'))
    # Apply model to make predictions
    print(input_data)
    prediction = load_model.predict(input_data)
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    download_link = filedownload(df)
    return df, download_link

# Create your views here.
def index(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES.get('myfile')
        if uploaded_file is None:  # No file uploaded
            error_message = 'Please select a file to upload.'
            return render(request, 'mTOR.html', {'error': error_message})
        load_data = pd.read_table(uploaded_file, sep=' ', header=None)
        load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)
        desc_calc()
        # Read in calculated descriptors and display the dataframe
        desc = pd.read_csv('/Users/apoorvav/bioactivityApp/descriptors_output.csv')
        # Read descriptor list used in previously built model
        Xlist = list(pd.read_csv('/Users/apoorvav/bioactivityApp/mTOR/data/descriptor_list.csv').columns)
        desc_subset = desc[Xlist]
        df, download_link = build_model(desc_subset, load_data)
        context['original_data'] = load_data.to_html()
        context['desc_data'] = desc_subset.to_html()
        context['pred_data'] = df.to_html()
        context['download_link'] = download_link
        return render(request, 'Result.html', context)
    # else:
    #     return render(request, 'index.html')


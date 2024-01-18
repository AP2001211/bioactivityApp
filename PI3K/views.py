import subprocess
import os
import base64
import pickle
import pandas as pd
# from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse
import kora.install.rdkit
from rdkit import Chem
from rdkit.Chem import AllChem
import py3Dmol



def upload_file_view(request):
    return render(request, 'PI3K.html')

# Molecular descriptor calculator
def desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar /Users/apoorvav/bioactivityApp/PI3K/data/PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes /Users/apoorvav/bioactivityApp/PI3K/data/PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
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
    load_model = pickle.load(open('/Users/apoorvav/bioactivityApp/PI3K/data/PI3K_model.pkl', 'rb'))
    # Apply model to make predictions
    print(input_data)
    prediction = load_model.predict(input_data)
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    download_link = filedownload(df)
    return df, download_link

def mol_view(request):
    smiles = 'CC(=O)OC1=CC=CC=C1C(=O)O'
    mol = Chem.MolFromSmiles(smiles)
    AllChem.EmbedMolecule(mol)
    mb = Chem.MolToMolBlock(mol)
    p = py3Dmol.view(width=400,height=400)
    p.addModel(mb,'sdf')
    p.setStyle({'stick':{}})
    p.setBackgroundColor('0xeeeeee')
    p.zoomTo()
    html = p._repr_html_()
    return HttpResponse(html)

# Create your views here.
def index(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES.get('myfile')
        if uploaded_file is None:  # No file uploaded
            error_message = 'Please select a file to upload.'
            return render(request, 'PI3K.html', {'error': error_message})
        load_data = pd.read_table(uploaded_file, sep=' ', header=None)
        load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)
        desc_calc()
        # Read in calculated descriptors and display the dataframe
        desc = pd.read_csv('/Users/apoorvav/bioactivityApp/descriptors_output.csv')
        # Read descriptor list used in previously built model
        Xlist = list(pd.read_csv('/Users/apoorvav/bioactivityApp/PI3K/data/descriptor_list.csv').columns)
        desc_subset = desc[Xlist]
        df, download_link = build_model(desc_subset, load_data)
        context['original_data'] = load_data.to_html()
        context['desc_data'] = desc_subset.to_html()
        context['pred_data'] = df.to_html()
        context['download_link'] = download_link
        return render(request, 'Result.html', context)
    # else:
    #     return render(request, 'index.html')


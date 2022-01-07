from flask import Flask, render_template, request
import xmlschema
from lxml import etree
from io import StringIO

app = Flask(__name__)

#des chaines de caractères qui s'afficheront lors de validation d'un document XML
dtdv = " the XML document is valid by DTD"
dtdnv = "the XML document is not valid by DTD !"

xsdv = " the XML document is valid by XSD"
xsdnv = "the XML document is not valid by XSD !"

#On affecte les résultas à ces deux variables.
res1 =""
res2 =""

@app.route('/')
def index():
    return render_template('index.html')

# Using file (l'utilisateur importe le docuement xml)
@app.route('/validationByFile', methods=['POST'])
def validationByFile():
     xmlfile = request.files['xmlfile']
     validatorFile = request.files['validatorfile']

     #Si le document de validation (xsd ou dtd) n'est pas importé donc le fichier xml contient un dtd interne
     if validatorFile.filename == '':
         res1 = byInternalDTD(xmlfile)
     #Sinon la validation se fait selon le format de fichier de validation importé (DTD ou XSD)
     elif validatorFile.filename.endswith('.dtd'):
         res1 = byDTD(xmlfile, validatorFile)
     else:
         res1 = byXSD(xmlfile, validatorFile)

     return render_template('index.html', messageFile = res1)

# dtd validator using file
def externalDTDUsingFile(xmlfile, dtdFile):
    try:
        dtd = etree.DTD(dtdFile)      #extraire le DTD
        tree = etree.parse(xmlfile)      #analyser le fichier XML # analyser le contenu de la source
        root = tree.getroot()            #obtenir l'element racine de l'arbre
        stat = dtd.validate(root)
        return stat;
    except Exception as e:
        print(e);

#fonction qui affiche le résultat selon la validité du document xml par dtd externe
def byDTD(xmlfile, validatorFile):
    if externalDTDUsingFile(xmlfile, validatorFile): return dtdv
    else: return dtdnv

# xsd validator using file
def XSDUsingFile(xmlfile, xsdfile):
    try:
        XS = xmlschema.XMLSchema(xsdfile) #création d'une instance de schéma en utilisant le chemin du fichier contenant le schéma en argument:
        o = XS.is_valid(xmlfile)
        return o
    except Exception as e:
        print(e);

#fonction qui affiche le résultat selon la validité du document xml par xsd
def byXSD(xmlfile, validatorFile):
    if XSDUsingFile(xmlfile, validatorFile): return xsdv
    else: return xsdnv

#internal dtd using file
def internalDTDUsingFile(xmlFile):
    try:
        #recupere l xml
        tree = etree.parse(xmlFile)
        #internalDTD
        dtd = tree.docinfo.internalDTD
        root = tree.getroot()
        status = dtd.validate(root)
        return status;
    except Exception as e:
        print(e);

#fonction qui affiche le résultat selon la validité du document xml par dtd interne
def byInternalDTD(xmlfile):
    if internalDTDUsingFile(xmlfile): return dtdv
    else: return dtdnv

#--------------------------------------------------------------------------------------------------------------------------------

# Using text area (l'utilisateur saisi le docuement xml dans le champs donné)
@app.route('/validationByText', methods=['POST'])
def validationByText():
    xmltextarea = format(request.form['xmltextarea'])
    validatortextarea = format(request.form['validatortextarea'])

    # Si le code (xsd ou dtd) de validation n'est pas saisi dans le champs (text area) donc le code xml contient un dtd interne
    if validatortextarea == "":
        res2 = byInternalDTDTxt(xmltextarea);
    # tester si le fichier est un fichier XSD ou DTD externe
    elif "<xsd:schema>" or "<xs:schema>" in validatortextarea:
    #elif ":schema" in validatortextarea:
        res2 = byXSDbyTxt(xmltextarea, validatortextarea)
    else: res2 = byDTDbyTxt(xmltextarea, validatortextarea);
    return render_template('index.html', messageTxt=res2);

# dtd validator using text area
def externalDTDUsingTxt(xmltextarea, dtdtextarea):
    try:
        dtd_tags = StringIO(dtdtextarea)
        dtd = etree.DTD(dtd_tags)
        root = etree.XML(xmltextarea)
        stat = dtd.validate(root)
        return stat
    except Exception as e:
         print(e);

#fonction qui affiche le résultat selon la validité du document xml par dtd externe
def byDTDbyTxt(xmltextarea, dtdtextarea):
    if externalDTDUsingTxt(xmltextarea, dtdtextarea): return dtdv
    else: return dtdnv

# xsd validator using text area
def XSDUsingTxt(xmltextarea, xsdtextarea):
    try:
        f = StringIO(xsdtextarea)
        xmlschema_doc = etree.parse(f)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        valid = StringIO(xmltextarea)
        doc = etree.parse(valid)
        stat = xmlschema.validate(doc)
        return stat
    except Exception as e:
        print(e);

#fonction qui affiche le résultat selon la validité du document xml par xsd
def byXSDbyTxt(xmltextarea, xsdtextarea):
    if XSDUsingTxt(xmltextarea, xsdtextarea): return xsdv
    else: return xsdnv

#internal dtd using text area
def internalDTDUsingTxt(xmlTxtArea):
    try:
        dtd_tags = StringIO(xmlTxtArea)
        tree = etree.parse(dtd_tags)
        dtd = tree.docinfo.internalDTD
        root = tree.getroot()
        status = dtd.validate(root)
        return status;
    except Exception as e:
        print(e);

#fonction qui affiche le résultat selon la validité du document xml par dtd interne
def byInternalDTDTxt(xmlTxtArea):
    if internalDTDUsingTxt(xmlTxtArea): return dtdv
    else: return dtdnv


if __name__ == '__main__':
    app.run(debug=True)
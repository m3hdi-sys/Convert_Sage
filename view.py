import csv
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse

def format_excel_date(val):
    try:
        num = float(val)
        if num > 10000:
            dt = datetime(1899, 12, 30) + timedelta(days=num)
            return dt.strftime("%d/%m/%Y")
    except:
        pass
    return str(val).strip()

def format_montant(val):
    try:
        num = float(val)
        if num == 0:
            return ""
        return str(num).replace(',', '.') # Assure le point pour Sage
    except:
        return ""

def accueil(request):
    if request.method == 'POST' and request.FILES.get('fichier_csv'):
        csv_file = request.FILES['fichier_csv']
        
        # Lecture du fichier envoyé
        decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
        reader = csv.reader(decoded_file, delimiter=',')
        
        output_data = []
        paysEU = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]

        # Ignorer la ligne d'en-tête
        next(reader, None)

        for row in reader:
            if len(row) < 12: 
                continue
            
            piece = row[0].strip()
            date_str = format_excel_date(row[1])
            nom = row[2][:35].strip()
            ht = row[3] or 0
            tva = row[4] or 0
            ttc = row[5] or 0
            pays = row[10].strip()
            reglement = row[11].strip().upper()

            # =========================================================
            # LES RÈGLES STRICTES DE KAKAROTTO (Sans les noms d'entreprises)
            # =========================================================
            suffix = ""
            if "FAIRE" in reglement or "FAI" in reglement: 
                suffix = "FAI"
            elif "VAD" in reglement or reglement == "VIRVAD": 
                suffix = "VAD" # Fonctionne même si c'est capricieux
            elif "VIR" in reglement: 
                suffix = "VIR"
            elif "CB" in reglement: 
                suffix = "CB"
            elif "AVO" in reglement or "AVOIR" in reglement: 
                suffix = "AVO"

            # Si on a trouvé un suffixe, c'est 411 + suffixe. Sinon, compte d'attente 471000
            compteClient = ("411" + suffix) if suffix else "471000"

            # =========================================================
            # COMPTES VENTES (FR / UE / EXPORT)
            # =========================================================
            if pays == "FR": compteVente = "707000"
            elif pays in paysEU: compteVente = "707910"
            else: compteVente = "707930"

            # Construction des 3 lignes Sage (Client, TVA, Vente)
            output_data.append([date_str, "ve", compteClient, piece, nom, format_montant(ttc), "", "E"])
            output_data.append([date_str, "ve", "445710", piece, nom, "", format_montant(tva), "E"])
            output_data.append([date_str, "ve", compteVente, piece, nom, "", format_montant(ht), "E"])

        # Préparation du fichier CSV à télécharger
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Import_Sage100_Strict.csv"'
        
        writer = csv.writer(response, delimiter=',')
        for data_row in output_data:
            writer.writerow(data_row)

        return response 

    # Affichage de la page web
    return render(request, 'convertisseur/index.html')
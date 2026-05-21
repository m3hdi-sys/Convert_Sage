from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import io
import csv
import zipfile
from datetime import datetime

# --- LE DICTIONNAIRE SECRET DE SARL MOMENT ---
# Mots-clés en majuscules pour éviter les bugs (ex: si c'est écrit "D'auria" ou "d'Auria", il trouvera "AURIA")
MAPPING_SARL_MOMENT = {
    "OZ": "411OZ",
    "TURQUOISE": "411TUR",
    "TOMORROW": "411TOM",
    "MCT": "411MCT",
    "BLACK LAB": "411BLA",
    "FILS": "411FIL", # Raccourci pour être sûr de capter "SARL FILS"
    "JOT": "411JOT",
    "UNI FASHION": "411UNF",
    "RICOCHET": "411RIC",
    "KCB": "411KCB",
    "TOPANGA": "411TOP",
    "MADE BY COCO": "411MCO",
    "CHENGCH": "411CHE",
    "IZI": "411IZI",
    "JUMELLES": "411LJB",
    "AURIA": "411DAU", # Marche pour "D'AURIA" ou "AURIA"
    "DOUBLE D": "411DOU",
    "JLM": "411JLM",
    "APW": "411APW",
    "ROSE METAL": "411ROS"
}

def accueil(request):
    if request.method == 'POST' and request.FILES.getlist('fichiers_csv'):
        fichiers = request.FILES.getlist('fichiers_csv')
        format_sortie = request.POST.get('format_sortie', 'xlsx')
        
        try:
            fichiers_traites = []
            paysEU = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]

            for fichier in fichiers:
                # On regarde quelle règle tu as choisie pour ce fichier (Standard ou SARL_MOMENT)
                regle_choisie = request.POST.get(f'regle_{fichier.name}', 'DEFAUT')
                
                nom_origine = fichier.name.rsplit('.', 1)[0]
                nom_final_base = f"Sage_{nom_origine}"
                
                nom_f = fichier.name.lower()
                if nom_f.endswith('.csv'):
                    df = pd.read_csv(fichier, sep=None, engine='python')
                else:
                    df = pd.read_excel(fichier)
                    
                df = df.fillna('')
                lignes_sage = []

                for _, row in df.iterrows():
                    if len(df.columns) < 12: continue
                    piece = str(row.iloc[0]).strip()
                    if not piece: continue
                    
                    date_val = row.iloc[1]
                    dateStr = date_val.strftime("%d/%m/%Y") if isinstance(date_val, (datetime, pd.Timestamp)) else str(date_val)[:10]
                    
                    nom = str(row.iloc[2])[:35]
                    nom_analyse = nom.upper() # On met tout en majuscule pour l'analyse
                    
                    ht = float(row.iloc[3]) if row.iloc[3] != '' else 0.0
                    tva = float(row.iloc[4]) if row.iloc[4] != '' else 0.0
                    ttc = float(row.iloc[5]) if row.iloc[5] != '' else 0.0
                    pays = str(row.iloc[10]).strip().upper()
                    reglement = str(row.iloc[11]).strip().upper()
                    
                    compteClient = "471000" # Base par défaut

                    # --- L'INTELLIGENCE ARTIFICIELLE : ANALYSE DU NOM DU CLIENT ---
                    if regle_choisie == "SARL_MOMENT":
                        # Le moteur cherche dans le nom si un de tes clients VIP existe
                        for mot_cle, code_vip in MAPPING_SARL_MOMENT.items():
                            if mot_cle in nom_analyse:
                                compteClient = code_vip
                                break # On a trouvé, on arrête de chercher pour cette ligne
                    
                    # --- RÈGLE CLASSIQUE (Si ce n'est pas SARL MOMENT, ou si le client VIP n'a pas été trouvé) ---
                    if compteClient == "471000":
                        if any(x in reglement for x in ["FAI", "VIR", "CB", "VAD", "AVO"]):
                            trouve = next((x for x in ["FAI", "VIR", "CB", "VAD", "AVO"] if x in reglement), "471000")
                            compteClient = "411" + trouve if trouve != "471000" else "471000"
                        
                    # Règle Vente (TVA)
                    if pays == "FR": compteVente = "707000"
                    elif pays in paysEU: compteVente = "707910"
                    else: compteVente = "707930"

                    def fmt(val): return "{:g}".format(val).replace(',', '.') if val != 0 else ""

                    lignes_sage.append([dateStr, "ve", compteClient, piece, nom, fmt(ttc), "", "E"])
                    lignes_sage.append([dateStr, "ve", "445710", piece, nom, "", fmt(tva), "E"])
                    lignes_sage.append([dateStr, "ve", compteVente, piece, nom, "", fmt(ht), "E"])

                fichiers_traites.append((nom_final_base, lignes_sage))

            # --- FONCTIONS DE GÉNÉRATION ---
            def generer_csv(lignes):
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer, delimiter=';')
                for row in lignes: writer.writerow(row)
                return '\ufeff' + csv_buffer.getvalue()

            def generer_xlsx(lignes):
                xlsx_buffer = io.BytesIO()
                df_sortie = pd.DataFrame(lignes)
                with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                    df_sortie.to_excel(writer, index=False, header=False, sheet_name='Import Sage')
                return xlsx_buffer.getvalue()

            # --- DISTRIBUTION ---
            if len(fichiers_traites) == 1 and format_sortie != 'zip':
                nom_base, lignes = fichiers_traites[0]
                if format_sortie == 'csv':
                    response = HttpResponse(generer_csv(lignes).encode('utf8'), content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="{nom_base}.csv"'
                    return response
                elif format_sortie == 'xlsx':
                    response = HttpResponse(generer_xlsx(lignes), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename="{nom_base}.xlsx"'
                    return response

            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for nom_base, lignes in fichiers_traites:
                        if format_sortie == 'csv' or format_sortie == 'zip':
                            zf.writestr(f'{nom_base}.csv', generer_csv(lignes).encode('utf8'))
                        if format_sortie == 'xlsx' or format_sortie == 'zip':
                            zf.writestr(f'{nom_base}.xlsx', generer_xlsx(lignes))
                
                zip_buffer.seek(0)
                response = HttpResponse(zip_buffer, content_type='application/zip')
                nom_zip = "Import_Sage_Multiple.zip" if len(fichiers_traites) > 1 else f"{fichiers_traites[0][0]}_Complet.zip"
                response['Content-Disposition'] = f'attachment; filename="{nom_zip}"'
                return response

        except Exception as e:
            return HttpResponse(f"Erreur lors de la conversion : {e}", status=400)

    return render(request, 'convertisseur/index.html')
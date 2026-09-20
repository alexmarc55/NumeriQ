CLASSIFICATION_PROMPT = """
Analizează documentul atașat și clasifică-l în categoria corectă din domeniul contabil.

Categorii posibile:
- factura: factură fiscală de vânzare/cumpărare, cu produse/servicii, TVA, furnizor și client
- factura_storno: factură de stornare/corecție a unei facturi anterioare
- aviz_expeditie: aviz de însoțire a mărfii, fără valoare fiscală de plată
- bon_fiscal: bon de casă emis de o casă de marcat
- chitanta: chitanță pentru încasare sau plată în numerar
- extras_cont_bancar: listă de tranzacții bancare dintr-un cont, emisă de bancă
- ordin_plata: ordin de plată către un beneficiar
- stat_plata: stat de plată sau fluturaș salarial
- contract_munca: contract individual de muncă
- raport_financiar: raport de sinteză, balanță de verificare, situație financiară pe o perioadă (active, venituri, cheltuieli, profit)
- bilant_contabil: bilanț contabil anual
- jurnal_contabil: registru jurnal sau notă contabilă
- declaratie_fiscala: declarație fiscală depusă la ANAF (ex: D112, D300, D390, D394)
- decizie_impunere: decizie de impunere emisă de ANAF
- contract_comercial: contract comercial cu furnizori sau clienți
- nir: notă de intrare-recepție pentru marfă sau stoc
- bon_consum: bon de consum de materiale
- proces_verbal: proces verbal (recepție, predare-primire, constatare etc.)
- altul: orice document care nu se încadrează clar în categoriile de mai sus

Alege categoria care descrie cel mai exact scopul principal al documentului, nu doar termenii care apar în text
(ex: un document care menționează "conturi" și "sold" poate fi raport_financiar, nu neapărat extras_cont_bancar —
uită-te la structura și scopul întregului document).

Extrage apoi informațiile cerute, relevante pentru tipul de document identificat.
"""

CLASSIFICATION_SCHEMA = {
    "name": "document_classification",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "doc_type": {
                "type": "string",
                "enum": [
    "factura",
    "factura_storno",
    "aviz_expeditie",
    "bon_fiscal",
    "chitanta",

    # Documente bancare
    "extras_cont_bancar",
    "ordin_plata",

    # Documente de personal/salarizare
    "stat_plata",
    "contract_munca",

    # Rapoarte si situatii financiare
    "raport_financiar",
    "bilant_contabil",
    "jurnal_contabil",

    # Declaratii fiscale
    "declaratie_fiscala",
    "decizie_impunere",

    # Documente contractuale
    "contract_comercial",

    # Alte documente justificative
    "nir",
    "bon_consum",
    "proces_verbal",

    "altul",
],
            },
            "furnizor": {"type": ["string", "null"]},
            "cui_furnizor": {"type": ["string", "null"]},
            "data_document": {"type": ["string", "null"]},
            "suma_totala": {"type": ["number", "null"]},
            "tva": {"type": ["number", "null"]},
            "moneda": {"type": ["string", "null"]},
        },
        "required": ["doc_type", "furnizor", "cui_furnizor", "data_document", "suma_totala", "tva", "moneda"],
        "additionalProperties": False,
    },
}

ACCOUNTING_PROMPT_TEMPLATE = """
Ești contabil expert în legislația română (plan de conturi conform OMFP 1802/2014).

Tip document: {doc_type}
Date extrase: {extracted_data}
CUI-ul firmei pentru care se face contarea: {company_cui}

IMPORTANT — direcția operațiunii:
- Dacă CUI-ul firmei apare ca FURNIZOR pe document → este o factură de ieșire (VENIT).
- Dacă CUI-ul firmei apare ca CUMPĂRĂTOR/CLIENT pe document → este o factură de intrare (CHELTUIALĂ).

Propune toate liniile contabile necesare (pot fi mai mult de o pereche debit/credit — ex: TVA se contează separat).
Fiecare linie are: cont (doar codul numeric, ex: "4111"), tip ("debit" sau "credit"), suma.
Suma totală a liniilor debit trebuie să fie egală cu suma totală a liniilor credit.

Dacă informațiile nu sunt suficiente pentru o propunere sigură, marchează necesita_verificare: true.
{feedback_section}
"""

FEEDBACK_SECTION_TEMPLATE = """
ATENȚIE — o propunere anterioară pentru acest document a avut următoarele probleme, corectează-le explicit:
{issues}
"""

ACCOUNTING_SCHEMA = {
    "name": "accounting_entry_proposal",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "linii": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "cont": {"type": "string"},
                        "tip": {"type": "string", "enum": ["debit", "credit"]},
                        "suma": {"type": "number"},
                    },
                    "required": ["cont", "tip", "suma"],
                    "additionalProperties": False,
                },
            },
            "necesita_verificare": {"type": "boolean"},
            "observatii": {"type": ["string", "null"]},
        },
        "required": ["linii", "necesita_verificare", "observatii"],
        "additionalProperties": False,
    },
}
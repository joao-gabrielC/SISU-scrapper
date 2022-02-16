#!/usr/bin/env python3
import requests
import re
import sys
from constants import estados
import datetime


def get_info(dados, numero):
    sigla = f'{dados[numero]["sg_uf_ies"]}-{dados[numero]["sg_ies"]}-{dados[numero]["no_municipio_campus"]}'
    codigo = dados[numero]['co_oferta']
    return (sigla, codigo)


def get_cortes(codigo):
    r=requests.get(f'https://sisu-api-pcr.apps.mec.gov.br/api/v1/oferta/{codigo}/modalidades')
    data = r.json()

    out = []
    for i in data['modalidades']:
        out.append({'modalidade': i['no_concorrencia'].replace(',', '', 999),
                       'cod_concorr': i['co_concorrencia'],
                       'corte': i['nu_nota_corte']
                       })
    return out


def formata(sigla, dicionario):
    output = sigla + ',{0},{5},{6},{1},{2},{14},{10},{13},{9},{3},{4},{7},{8},{15},{11}'
    for i in dicionario:
        if i['corte'] and int(i['cod_concorr'])<16 and int(i['cod_concorr'])!=12:
            output = output.replace("{" + i['cod_concorr'] + "}", i['corte'])
        elif int(i['cod_concorr']) >= 16 or int(i['cod_concorr'] == 12):
            output += ',' + i['modalidade'] + ': ' + str(i['corte'])
    output = re.sub('\{.{1,2}\}', '-', output)
    return(output)

try:
    curso_id = sys.argv[1]
except IndexError:
    curso_id = 37 # Default é medicina

r = requests.get(f'https://sisu-api-pcr.apps.mec.gov.br/api/v1/oferta/curso/{curso_id}')
dados = r.json()
output = []
for i in dados.keys():
    if len(i) < 3:
        sigla, codigo = get_info(dados, i)
        dicionario = get_cortes(codigo)
        # print(sigla, dicionario)  # DEBUG
        linha = formata(sigla, dicionario)
        print(linha)  # DEBUG
        output.append(f'{linha}\n')

output.sort(key = lambda sigla: sigla.split('-', maxsplit=2)[1])
output.sort(key = lambda sigla: estados[sigla.split('-', maxsplit=2)[0]])

output.insert(0, "Faculdade,\
AC,\
Escola Pública (L5),\
Escola Pública + PPI (L6),\
Escola Pública + Renda (L1),\
Escola Pública + PPI + Renda (L2),\
Escola Pública + PCD + PPI (L14),\
Escola Pública + PCD + RENDA + PPI  (L10),\
Escola Pública + PCD (L13),\
Escola Pública + PCD + RENDA (L9),\
Escola Pública + PP + Renda  (L3),\
Escola Pública + Renda + Indígenas (L4),\
Escola Pública + PP (L7),\
Escola Pública + Indígenas (L8),\
Escola Pública + PCD + PP (L15),\
Escola Pública + PCD + PP  + Renda (L11),\
Outros\n")

now=datetime.datetime.now

with open(f'notas{now.day}-{now.month}-{now.year}.csv', 'a') as f:
    for line in output: f.write(line)

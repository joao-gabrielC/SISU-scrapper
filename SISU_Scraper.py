#!/usr/bin/env python3
import requests
import re
import sys


def get_info(dados, numero):
    sigla = dados[numero].get('sg_uf_ies') + '-' + dados[numero].get('sg_ies') + '-' + dados[numero].get('no_municipio_campus')
    codigo = dados.get(numero).get('co_oferta')
    return (sigla, codigo)


def get_cortes(codigo):
    r=requests.get('https://sisu-api-pcr.apps.mec.gov.br/api/v1/oferta/%s/modalidades' % (codigo))
    __data = r.json()

    output = []
    for i in __data['modalidades']:
        output.append({'modalidade': i['no_concorrencia'].replace(',', '', 999),
                       'cod_concorr': i['co_concorrencia'],
                       'corte': i['nu_nota_corte']
                       })
    return output


def formata(sigla, dicionario):
    output = sigla + ',{0},{5},{6},{1},{2},{14},{10},{13},{9},{3},{4},{7},{8},{15},{11}'
    for i in dicionario:
        if i['corte'] and int(i['cod_concorr'])<16 and int(i['cod_concorr'])!=12:
            output = output.replace("{" + i['cod_concorr'] + "}", i['corte'])
        elif int(i['cod_concorr']) >= 16 or int(i['cod_concorr'] == 12): output += ',' + i['modalidade'] + ': ' + i['corte']
    output = re.sub('\{.{1,2}\}', '-', output)
    return(output)

try:
    curso_id = sys.argv[1]
except IndexError:
    curso_id = 37 # Default é medicina

r = requests.get(f'https://sisu-api-pcr.apps.mec.gov.br/api/v1/oferta/curso/{curso_id}')
dados = r.json()
output = ["Faculdade,\
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
Outros\n"]
print(output)
for i in dados.keys():
    if len(i) < 3:
        sigla, codigo = get_info(dados, i)
        dicionario = get_cortes(codigo)
        # print(sigla, dicionario)  # DEBUG
        linha = formata(sigla, dicionario)
        print(linha)  # DEBUG
        output.append(f'{linha}\n')

with open('notasFinal.csv', 'a') as f:
    for line in output: f.write(line)

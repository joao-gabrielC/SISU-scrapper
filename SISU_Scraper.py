#!/usr/bin/env python3
import requests
import re
import sys
from constants import estados, api_url
import datetime

user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}


def get_info(dados, numero):
    sigla = f'{dados[numero]["sg_ies"]} {dados[numero]["no_municipio_campus"]}'
    codigo = dados[numero]['co_oferta']
    return (sigla, codigo)


def get_cortes(codigo):
    r=requests.get(f'{api_url}/oferta/{codigo}/modalidades', headers = user_agent)
    data = r.json()

    out = []
    for i in data['modalidades']:
        out.append({'modalidade': i['no_concorrencia'].replace(',', '', 999),
                       'cod_concorr': i['co_concorrencia'],
                       'corte': i['nu_nota_corte'] or '',
                       'cota': i['tp_cota'] or '',
                       'salario_minimo': i['tp_salario_minimo'] or ''
                       })
    return out


def formata(sigla, dicionario):
    # Placeholders, in the format of (cota, salario_minimo)
    output = sigla + ",{(0, 0)},{(4, 0)},{(1, 0)},{(4, 1)},{(1, 1)},{(2, 0)},{(2, 1)},{(3, 0)},{(3, 1)}"
    titulo_cota_dict = {
            'PPI': 1,
            'Q': 2,
            'PCD': 3,
            'EP': 4
        }
    salario_minimo_dict = {
        'S': 0,
        'I': 1
    }
       
    for i in dicionario:  
         # Replace ampla from the start so we don't have problems with null values
        if i["cod_concorr"] == "0":            
            output.replace('{(0, 0)}', i['corte'])
        else:
            try: 
                co_modalidade = (titulo_cota_dict[i['cota']], salario_minimo_dict[i['salario_minimo']])
                if str(co_modalidade) in output:

                    output = output.replace("{" + str(co_modalidade) + "}", i['corte'])
                else: 
                    output += ',' + i['modalidade'] + ': ' + i['corte']
    
            except KeyError:
                # Catch cases where the values aren't default and manually apend the value
                output += ',' + i['modalidade'] + ': ' + i['corte']

# Clean the output for any remaining placeholders
    output = re.sub('\{.{6}\}', '-', output)
    return(output)

try:
    curso_id = sys.argv[1]
except IndexError:
    curso_id = 37 # Default é medicina

r = requests.get(f'{api_url}/oferta/curso/{curso_id}', headers = user_agent)
dados = r.json()
output = []
for i in dados.keys():
    if len(i) < 3:
        sigla, codigo = get_info(dados, i)
        dicionario = get_cortes(codigo)
        linha = formata(sigla, dicionario)
        output.append(f'{linha}\n')

output.sort()

output.insert(0, "Faculdade,\
                AC,\
                Escola Pública (LI_EP),\
                Escola Pública + PPI (LI_PPI),\
                Escola Pública + Renda (LB_EP),\
                Escola Pública + PPI + Renda (LB_PPI),\
                Escola Pública + Quilombola (LI_Q),\
                Escola Pública + Quilombola + Renda (LB_Q),\
                Escola Pública + PCD (LI_PCD),\
                Escola Pública + PCD + RENDA (LB_PCD),\
                Outros\n")

now=datetime.datetime.now()

with open(f'notas{now.day}-{now.month}-{now.year}.csv', 'a') as f:
    for line in output: f.write(line)

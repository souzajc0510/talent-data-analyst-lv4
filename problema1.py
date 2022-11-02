import pandas as pd
import re
from utils import utils
import os
from fastparquet import write 

import pyarrow as pa
import pyarrow.parquet as pq

#definindo as variáveis

#loglevel int
#0 = Não gera os prints dos logs
#1 = Gera os prints dos logs
loglevel = 1
project_dir = os.getcwd()
source_file_name = project_dir+'/dados_cadastrais_fake.csv'
de_para_file_name = project_dir+'/de_para_estados.csv'

def read_file(file_name, vdelimiter):
    try:
        df = pd.read_csv(file_name,delimiter=vdelimiter)
        utils.logger(loglevel,'Arquivo '+ file_name+' lido - quantidade de linhas: '+str(len(df)))
        utils.logger(loglevel,'Colunas: ')
        utils.logger(loglevel,df.columns)
        return df
    except Exception as e:
        print("Error when trying to open the file: ",e)
        df = 'Error'
        return df

if __name__ == '__main__':
    x = utils.logger(loglevel, "Iniciando o processo")
    utils.logger(loglevel, utils.is_cpf_valido('529.982.247-25'))

    #lendo o arquivo dados_cadastrais_fake.csv
    df = read_file(source_file_name,';')
    df_de_para = read_file(de_para_file_name,';')

    # criando coluna cpf_limpo sem "." e "-" 
    df['cpf_limpo'] = df['cpf'].map(lambda x: re.sub(r'\W+', '', x))
    # criando coluna cnpj_limpo sem "." e "-"    
    df['cnpj_limpo'] = df['cnpj'].map(lambda x: re.sub(r'\W+', '', x))

    # validando se o CPF é válido através do método "is_cpf_valido"
    df['cpf_valido'] = df['cpf_limpo'].apply(lambda x: 'Valido' if utils.is_cpf_valido(x) else 'Invalido')
    # validando se o CNPJ é válido através do método "is_cnpj_valido"
    df['cnpj_valido'] = df['cnpj_limpo'].apply(lambda x: 'Valido' if utils.is_cnpj_valido(x) else 'Invalido')

    # fazendo o merge dos data frames
    df = pd.merge(df, df_de_para, on="estado", how="left")

    # Apagando a coluna estado
    df = df.drop('estado', axis=1)
    
    # Renomeando a coluna estado_harmonizado para estado
    df=df.rename(columns = {'estado_harmonizado':'estado'})

    print('Existem ',df['nomes'].nunique(),' clientes únicos na base de dados')

    #Calculando a média de idade
    print('A média de idade da base de dados é:')
    print(df['idade'].mean())
    report_list ={'Media de Idade':[df['idade'].mean()], 'Quantidade de Clientes':[df['nomes'].nunique()]}
    report1 = pd.DataFrame(report_list)
    write(project_dir+'/report1.parquet', report1)
    
    #Agrupando os dados por estado
    report2= pd.DataFrame({'quantidade cliente': df.groupby('estado')['nomes'].nunique()})
    write(project_dir+'/report_estado1.parquet', report2)
    
    #Mostrando a quantidade de cpf e cnpj válidos
    print(df.groupby(['cpf_valido'])['cpf_valido'].count())
    print(df.groupby(['cnpj_valido'])['cpf_valido'].count())
    report2.to_csv(project_dir+'/report_estado.csv')
    
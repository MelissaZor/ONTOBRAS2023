from bs4 import BeautifulSoup
import re
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from rdflib import Literal
import os
from urllib.parse import quote

pasta = r'C:\Users\ANTONIO\Desktop\Request\htmlInteriorTeor'
arquivos = os.listdir(pasta)
num_arquivos = len(arquivos)
counter = 0
print(num_arquivos)

g = Graph()

cnj = Namespace('http://ontojur.com.br/JudicialProcess/')

while counter != num_arquivos:

    with open(fr"C:\Users\ANTONIO\Desktop\Request\htmlInteriorTeor\teste{counter}.html", encoding="utf8") as fp:
        soup = BeautifulSoup(fp, 'html.parser')


    TNURapporteurName = soup.find('span', {'class' : 'nome_relator'}).text.strip()

    TNURapporteurName = TNURapporteurName.replace('Juiz Federal', '').replace('Juíza Federal', '').strip()

    stringNumeroProcesso = soup.find('span', {'data-sin_numero_processo' : 'true'}).text.strip()
    
    numeroProcesso = re.sub(r"\D", "", stringNumeroProcesso)

    number = stringNumeroProcesso

    nomeRecurso = soup.find('span', {'data-classe_processo' : True}).text.strip()

    turmaRecursalOrigem = soup.find('span', {'data-origem_processo' : True}).text.strip()

    section_acordao = soup.find('section', {'data-nome' : 'acordao'})

    decisao = section_acordao.find('p', {'class' : 'paragrafoPadrao'})
    
    paragrafo = section_acordao.find('p', {'class' : 'paragrafoPadrao'}).text.lower()

    print(decisao)

    print(turmaRecursalOrigem)

    JudicialProcess = URIRef(cnj[numeroProcesso])

    TNURapporteur = URIRef(cnj['TNURapporteur/' + quote(TNURapporteurName)])

    g.add((JudicialProcess, RDF.type, cnj.JudicialProcess))
    g.add((JudicialProcess, cnj.number, Literal(numeroProcesso)))
    g.add((TNURapporteur, RDF.type, cnj.Rapporteur))
    g.add((TNURapporteur, RDFS.label, Literal(TNURapporteurName)))
    g.add((JudicialProcess, cnj.distributedTo, Literal(TNURapporteur)))
    #g.add((JudicialProcess, cnj.temNome, Literal(nomeRecurso)))
    #g.add((JudicialProcess, cnj.temTurmaRecursalOrigem, Literal(turmaRecursalOrigem)))
    
    #if 'não conheço' in paragrafo or 'não conhecimento' in paragrafo or 'desconheço' in paragrafo or 'não conhecer' in paragrafo:

        #NotHeardRSByTNU = URIRef(cnj['NotHeardRSByTNU/' + quote(number)])
        #g.add((NotHeardRSByTNU, RDF.type, cnj.NotHeardRSByTNU))
        #g.add((TNURapporteur, cnj.voted, NotHeardRSByTNU))
    

    # elif 'inadmitir' in paragrafo:

    #     g.add((JudicialProcess, cnj.temDecisao, Literal('Inadmissivel')))

    # elif 'anular' in paragrafo:

    #     g.add((JudicialProcess, cnj.temDecisao, Literal('Anulado')))

    # elif 'nego provimento' in paragrafo or 'não provimento' in paragrafo:
        
    #     g.add((JudicialProcess, cnj.temDecisao, Literal('não provimento')))

    # elif 'concedo provimento' in paragrafo:
        
    #     g.add((JudicialProcess, cnj.temDecisao, Literal('provimento')))

    # elif 'suspendo' in paragrafo or 'suspensão' in paragrafo:
        
    #     g.add((JudicialProcess, cnj.temDecisao, Literal('suspenso')))

    # elif 'provimento' in paragrafo and 'não provimento' not in paragrafo and 'nego provimento' not in paragrafo and 'parcial' not in paragrafo:
        
    #     g.add((JudicialProcess, cnj.temDecisao, Literal('provimento')))
    
    # elif 'parcial' in paragrafo:

    #     g.add((JudicialProcess, cnj.temDecisao, Literal('parcial provimento')))

    # else:
    #     g.add((JudicialProcess, cnj.temDecisao, Literal('nao averiguado')))

    # if 'unanimidade' in paragrafo:
    #     g.add((JudicialProcess, cnj.temForma, Literal('Unanimidade')))
    
    # elif 'maioria' in paragrafo:
    #     g.add((JudicialProcess, cnj.temForma, Literal('Maioria')))

    # else:
    #     g.add((JudicialProcess, cnj.temForma, Literal('não averiguado')))

    div_parte_re = soup.find('div', {'class': 'parte_re'})

    div_parte_autor = soup.find('div', {'class': 'parte_autor'})

    section_votantes = soup.find('section', {'data-nome' : 'votantes'})

    for votante in section_votantes.find_all('span', {'class': 'nome_relator'}):
            nomeVotante = votante.text.strip()
            nomeVotante = nomeVotante.replace('Juiz Federal', '').replace('Juíza Federal', '').strip()
            FederalJudge= URIRef(cnj['FederalJudge/' + quote(nomeVotante)])
            g.add((FederalJudge, RDF.type, cnj.FederalJudge))
            g.add((FederalJudge, RDFS.label, Literal(nomeVotante)))
            g.add((FederalJudge, cnj.federalJudgeMediatesJudicialProcess, JudicialProcess))

    if div_parte_re:                                                                                 
        for reu in div_parte_re.find_all('span', {'class': 'nome_parte'}):
            
            nomeReu = reu.text.strip()

            Appellee = URIRef(cnj['Appellee/' + quote(nomeReu)])

            g.add((Appellee, RDF.type, cnj.Appellee))
            g.add((Appellee, RDFS.label, Literal(nomeReu)))
            g.add((JudicialProcess, cnj.judicialProcessMediatesAppellee, Appellee))

                # adicionando informação que o reu é uma pessoa e também está vinculado ao processo
                #g.add((representante_uri, RDFS.label, Literal(nomeRepresentanteReu)))


        for representanteReu in div_parte_re.find_all('span', {'class': 'nome_parte_representante'}):
        
            nomeRepresentanteReu = representanteReu.text.strip()

            AttorneyName = nomeRepresentanteReu

            match = re.search(r"\bOAB [A-Z0-9]+\b", nomeRepresentanteReu)

            print(match)

            if match:
                oab_string = match.group(0)
                #oab_uri = URIRef(cnj['oab/' + quote(oab_string.split()[-1])])  # criar nova URI para a OAB

                #g.add((oab_uri, RDF.type, cnj.OAB))
                #g.add((oab_uri, cnj.temNumero, Literal(oab_string)))

                # usar número da OAB como ID do representante
                AttorneyCounsel = cnj['AttorneyCounsel/' + oab_string.split()[-1]]

                g.add((AttorneyCounsel, RDF.type, cnj.AttorneyCounsel))
                g.add((AttorneyCounsel, RDFS.label, Literal(AttorneyName)))
                g.add((AttorneyCounsel, cnj.OAB_1, Literal(oab_string.split()[-1])))



                OABRegistrationState = oab_string.split()[-1][:2]

                g.add((AttorneyCounsel, cnj.OABRegistrationState, Literal(OABRegistrationState)))

                # adicionando informação que o representante é uma pessoa e também está vinculado ao processo
                #g.add((representante_uri, RDFS.label, Literal(nomeRepresentanteReu)))

                #g.add((JudicialProcess, cnj.temRepresentanteReu, Literal(nomeRepresentanteReu)))
    
    if div_parte_autor:

        for autor in div_parte_autor.find_all('span', {'class': 'nome_parte'}):
            
            nomeAutor = autor.text.strip()

            Appellant = URIRef(cnj['Appellant/' + quote(nomeAutor)])
            g.add((Appellant, RDFS.label, Literal(nomeAutor)))
            g.add((Appellant, RDF.type, cnj.Appellant))
            #g.add((Appellant, cnj.temNome, Literal(nomeAutor)))

                # adicionando informação que o reu é uma pessoa e também está vinculado ao processo
            #g.add((autor_uri, RDF.type, pessoa.Pessoa))
                #g.add((representante_uri, RDFS.label, Literal(nomeRepresentanteReu)))

            g.add((JudicialProcess, cnj.judicialProcessMediatesAppellant, Appellant))


        for representanteAutor in div_parte_autor.find_all('span', {'class': 'nome_parte_representante'}):
        
            nomeRepresentanteAutor = representanteAutor.text.strip()

            match = re.search(r"\bOAB [A-Z0-9]+\b", nomeRepresentanteAutor)

            if match:
                oab_string = match.group(0)
                AttorneyCounsel = cnj['AttorneyCounsel/' + oab_string.split()[-1]]

                OABRegistrationState = oab_string.split()[-1][:2]

                g.add((AttorneyCounsel, RDF.type, cnj.AttorneyCounsel))
                g.add((AttorneyCounsel, RDFS.label, Literal(nomeRepresentanteAutor)))
                g.add((AttorneyCounsel, cnj.OAB_1, Literal(oab_string.split()[-1])))
                g.add((AttorneyCounsel, cnj.OABRegistrationState, Literal(OABRegistrationState)))
                
                #g.add((representante_uri, RDFS.label, Literal(nomeRepresentanteAutor)))

                #g.add((JudicialProcess, cnj.temRepresentanteAutor, Literal(nomeRepresentanteAutor)))

               


    counter += 1

with open("outputFFFFFFinal.ttl", "w", encoding="utf-8") as f:
    f.write(g.serialize(format="turtle"))

print("Acabou!")



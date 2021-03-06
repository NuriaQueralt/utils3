'''
Created on Sep 30, 2019

@name: phenomenet_class.py
@description: Module for the PhenomeNET ontology
@author: Nuria Queralt Rosinach
@version: 1.0
@date: 30-09-2019
@license: CC0
'''

import re, sys

class term(object):
    '''
    Classes in the ontology
    '''


    def __init__(self, pheno_owl):
        '''
        Constructor
        '''

        self.metadata = []
        #self.doid2orpha = {}
        self.eq_pheno_entity = dict()
        self.eq_pheno_quality = dict()

        # Input
        with open(pheno_owl, 'r', encoding='latin1') as pheno_f:
            pheno_d = pheno_f.read()
        pheno_f.close()

        # RE patterns
        iri_pattern = re.compile(r'<owl:Class rdf:about="(.+)"(.*)>')
        label_pattern = re.compile(r'<rdfs:label(.+)>(.+)</rdfs:label>')
        exact_synonym_pattern = re.compile(r'<oboInOwl:hasExactSynonym(.+)>(.+)</oboInOwl:hasExactSynonym>')
        definition_pattern = re.compile(r'<obo:IAO_0000115(.+)>(.+)</obo:IAO_0000115>')
        #doid_pattern = re.compile(r' <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_(.+)">')
        #orpha_pattern = re.compile(r'<owl:equivalentClass rdf:resource="http://www.orpha.net/ORDO/Orphanet_(.+)"/>')
        eq_pattern = re.compile(r'''
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/BFO_0000051"/>
                <owl:someValuesFrom>
                    <owl:Class>
                        <owl:intersectionOf rdf:parseType="Collection">
                            <rdf:Description rdf:about="(.+)"/>
                            <owl:Restriction>
                                <owl:onProperty rdf:resource="http://aber-owl.net/#has-quality"/>
                                <owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/PATO_(.+)"/>
                            </owl:Restriction>
                        </owl:intersectionOf>
                    </owl:Class>
                </owl:someValuesFrom>
            </owl:Restriction>
        </owl:equivalentClass>
        ''')

        # Algorithm
        # Classes in chunks
        pheno_terms = pheno_d.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]

        # Get term metadata
        # Parse chunks and extract mappings, term info
        for term in pheno_terms:
            concept = {}

            # get term id, iri
            iri_match = iri_pattern.search(term)
            try:
                iri = iri_match.group(1)
            except AttributeError:
                #print('term that is not a class: ',term)
                continue

            if '_' in iri:
                id = iri.rsplit('/',1)[1].replace('_',':')
            elif '#' in iri:
                id = iri.rsplit('#',1)[1]
            elif iri.rsplit('/',1):
                id = iri.rsplit('/',1)[1]
            else:
                print('Problems parsing IRI {} to extract the id.'.format(iri))

            # get term info: label, synonyms, definition
            label_match = label_pattern.search(term)
            if not label_match:
                label = 'NA'
            else:
                label = label_match.group(2)
            synonym_matches = exact_synonym_pattern.finditer(term)
            synonyms_l = []
            for synonym_match in synonym_matches:
                synonym = synonym_match.group(2)
                synonyms_l.append(synonym)
            synonyms = "|".join(synonyms_l)
            if not synonyms:
                synonyms = 'NA'
            definition_match = definition_pattern.search(term)
            if not definition_match:
                definition = 'NA'
            else:
                definition = definition_match.group(2)

            # build the concept dictionary
            concept['id'] = id
            concept['iri'] = iri
            concept['label'] = label
            concept['synonyms'] = synonyms
            concept['definition'] = definition

            # append the concept to the list of terms
            self.metadata.append(concept)


        # # Get do2orpha mappings
        # # Parse chunks and extract mappings, term info
        # for term in pheno_terms:
        #     # DOID class
        #     doid_match = doid_pattern.search(term)
        #     if not doid_match:
        #         continue
        #     doid_code = 'DOID:' + doid_match.group(1)
        #
        #     # Orphanet equivalent classes (mappings)
        #     orpha_matches = orpha_pattern.finditer(term)
        #     if not orpha_matches:
        #         continue
        #     orpha_l = []
        #     for orpha_match in orpha_matches:
        #         orpha_code = 'Orphanet:' + orpha_match.group(1)
        #         orpha_l.append(orpha_code)
        #     self.doid2orpha[doid_code] = set(orpha_l)

        # Get EQ model links
        for term in pheno_terms:
            # phenotype id
            iri_match = iri_pattern.search(term)
            if iri_match:
                iri = iri_match.group(1)
                if '_' in iri:
                    phenotype = iri.rsplit('/', 1)[1].replace('_', ':')
                elif '#' in iri:
                    phenotype = iri.rsplit('#', 1)[1]
                elif iri.rsplit('/', 1):
                    phenotype = iri.rsplit('/', 1)[1]
                else:
                    print('Problems parsing IRI {} to extract the id.'.format(iri))

            # EQ model match
            eq_match = eq_pattern.search(term)
            if eq_match:
                # entity class
                entity_iri = eq_match.group(1)
                entity = entity_iri.rsplit('/',1)[1]
                # pato class
                quality = 'PATO:' + eq_match.group(2)
                print('{}\t{}'.format(phenotype,entity))
                #print('{}\t{}'.format(phenotype, quality))
                self.eq_pheno_entity[phenotype] = entity
                self.eq_pheno_quality[phenotype] = quality

    def get_metadata_per_id(self, id):
        '''
        This function returns all the metadata for term queried: id, iri, label, synonyms, definition.
        :param id: str, ID of the term, e.g. DOID:4
        :return: dict, one dictionary with the metadata
        '''

        if '_' in id:
            id = id.replace('_',':')

        concept = 0
        for term in self.metadata:
            if term['id'] == id:
                concept = term
        if concept:
            return concept
        else:
            return print('Please enter a correct ID format, e.g. DOID:4. Use ":" of namespace separator. Thanks!')

    def get_specific_metadata_per_id(self, id, metadata='iri'):
        '''
        This Function returns the specific requested metadata for term queried.
        :param id: str, ID of the term, e.g. DOID:4
        :param metadata: str, 'iri', 'label', 'synonyms', or 'definition'
        :return: str
        '''

        term = self.get_metadata_per_id(id)
        return term[metadata]

    def print_metadata(self,outfile):
        '''
        This function extracts basic term metadata information for all terms in the ontology to be used in graph representation applications such as neo4j or Knowledge.Bio.
        Particularly, returns the id, :LABEL, label, synonyms, and definition
        :return: output file called 'pheno_concepts.tsv' with all the metadata for all terms
        '''

        # Output
        out_f = open('{}'.format(outfile),'w')
        out_f.write('id:ID,:LABEL,preflabel,synonyms:IGNORE,definition\n')
        out_f.write('owl#Thing,MONDOCLASS,"Thing","NA","Root class."\n')

        # Algorithm
        # Parse chunks and extract mappings, term info
        for term in self.metadata:
            # get term id, iri, label, synonyms, definition metadata
            id = term.get('id')
            iri = term.get('iri')
            label = term.get('label')
            synonyms = term.get('synonyms')
            definition = term.get('definition')

            # write term metadata down
            out_f.write('{},MONDOCLASS,"{}","{}","{}"\n'.format(id, label, synonyms, definition))

        out_f.close()

        return print('Term metadata file generated at "{}"'.format(outfile))

    def get_orphanet_mappings_per_doid(self, doid):
        '''
        This function return the orphanet mappings for the DO term queried.
        :param doid: DOID
        :return: orphanet mappings
        '''
        return self.doid2orpha.get(doid, ['NA'])

    def print_entities_qualities_from_eqmodel(self,outfile):
        '''
        This function extracts entity and quality from EQ model for all classes in the ontology to be used in TILDE.
        Particularly, returns 'has-entity' and 'has-quality' relations in prolog format
        :return: output file called  by the user, sth like 'phenotype_eqmodel_relations.bg'
        '''

        # Output
        out_f = open('{}'.format(outfile),'w')

        # Algorithm
        # Parse chunks and extract mappings, term info
        # get phenotype-entity relations
        for phenotype, entity in self.eq_pheno_entity.items():
            # (hasEntity(x,y),E(y) :- P(x))
            out_f.write('hasEntity({},{}), E({}) :- P({}).\n'.format(phenotype, entity, entity, phenotype))

        # get phenotype-quality relations
        for phenotype, quality in self.eq_pheno_quality.items():
            # (hasQuality(x,y),Q(y) :- P(x))
            out_f.write('hasQuality({},{}), Q({}) :- P({}).\n'.format(phenotype,quality,quality,phenotype))

        out_f.close()

        return print('Phenotypes-Entities and Phenotypes-Qualitites relations file generated at "{}"'.format(outfile))


class hierarchy(object):
    '''
    Inferred ontology - extraction of the hierarchy
    '''

    def __init__(self, pheno_owl):
        '''
        Constructor
        :param pheno_owl:
        '''

        self.totalNumberOfTerms = 0
        self.namespaces = {}
        self.predicates = {}

        # Input
        with open(pheno_owl, 'r') as pheno_f:
            pheno_d = pheno_f.read()

        # Output
        out_f = open('/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo_statements.tsv', 'w')
        out_f.write(':START_ID,:TYPE,association_type,pid,:END_ID,reference_uri,reference_supporting_text,reference_date\n')

        # RE patterns
        subjectIri_pattern = re.compile(r'<owl:Class rdf:about="(.+)">')
        propertyObjectIris_pattern = re.compile(r'<(.+) rdf:resource="(.+)"/>')

        # Algorithm
        # Classes in chunks
        pheno_terms = pheno_d.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]
        self.totalNumberOfTerms = len(pheno_terms)

        # Parse chunks and extract relationships
        pid = 'P279'
        reference_uri = "http://purl.obolibrary.org/obo/upheno/mondo.owl"
        reference_text = "No sentence because edge extracted from the MONDO ontology"
        reference_date = "2017-05-02"
        for term in pheno_terms:
            # extract relationships in each class disclosure
            subjectIri_match = subjectIri_pattern.search(term)
            subjectIri = subjectIri_match.group(1)
            subjectId = subjectIri.rsplit('/',1)[1].replace('_',':')
            objectPropertyIris_matches = propertyObjectIris_pattern.finditer(term)
            for objectPropertyIris_match in objectPropertyIris_matches:
                propertyIri = objectPropertyIris_match.group(1)
                objectIri = objectPropertyIris_match.group(2)
                propertyId = propertyIri.split(':')[1]
                objectId = objectIri.rsplit('/',1)[1].replace('_', ':')
                out_f.write('{},{},{},{},{},{},"{}",{}\n'.format(subjectId,propertyId,propertyId,pid,objectId,reference_uri,reference_text,reference_date))

                # get information: distinct property and namespace types
                self.predicates[propertyIri] = 1
                ns = objectIri.rsplit('/',1)[1].split('_')[0]
                self.namespaces[ns] = 1
        out_f.close()

    def get_total_number_of_terms(self):
        return print('Total number of terms: {}'.format(self.totalNumberOfTerms))
    def get_predicates(self):
        return print('Distinct predicates: {}'.format(self.predicates.keys()))
    def get_object_namespaces(self):
        return print('Distinct objects namespaces: {}'.format(self.namespaces.keys()))

if __name__ == '__main__':

    try:
        # input
        #mondo_f = "/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo.owl"
        pheno_f = "/home/rosinanq/workspace/droppheno/ontologies/phenomenet-extending.owl"
        #pheno_inferred_f = "/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo-inferred.owl"

        # output
        concepts_f = '/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo_concepts.tsv'

        # parse owl file
        tm = term(pheno_f)
        #print(tm.doid2orpha)
        #print(tm.metadata)
        #tm.print_metadata(concepts_f)
        #print(tm.get_metadata_per_id(id='DOID_0001816'))
        #print(tm.get_specific_metadata_per_id(id='DOID_0001816', metadata='iri'))
        #print(tm.get_specific_metadata_per_id(id='DOID:0001816', metadata='label'))
        #print(tm.get_specific_metadata_per_id(id='DOID_0001816', metadata='definition'))
        #cl = hierarchy(mondo_inferred_f)
        #cl.get_total_number_of_terms(), cl.get_predicates(), cl.get_object_namespaces()
        ## Apr 23rd 2018 version
        #print(tm.get_metadata_per_id(id='DOID_0001816'))
        #print(tm.get_metadata_per_id(id='MONDO:0015286'))

        # phenomenet
        #print(tm.get_metadata_per_id(id='FYPO:0000023'))
        #print(tm.get_metadata_per_id(id='PHENO:1'))
        # output phenotype-quality from simple EQ model
        outfile = "/home/rosinanq/workspace/droppheno/ontologies/phenotype_eqmodel_relations.bg"
        tm.print_entities_qualities_from_eqmodel(outfile)

    except OSError:
        print("Some problem occurred....T_T")
        sys.exit()
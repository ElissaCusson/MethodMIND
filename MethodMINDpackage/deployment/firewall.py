from MethodMINDpackage.train.database import connectload

def firewall_all_keywords(text_input):
    #firewall with all the keywords

    #connecting to database + getting keywords
    client, collection_name = connectload(database_name="MethodMIND", collection_name="MethodVectors")
    key_words = retrieve_all_keywords(client, collection_name)

    split_items = [item.strip() for sublist in key_words for item in sublist.split(',')]
    return any(item.lower() in text_input.lower() for item in split_items)

#retrieve keywords for firewall, haven't tested it yet
def retrieve_all_keywords(client, collection_name="MethodVectors"):
    """
    Retrieve all unique keywords from the specified collection.

    Args:
        client (MilvusClient): Milvus client connection.
        collection_name (str): Name of the collection to query.

    Returns:
        set: A set of unique keywords.
    """
    try:
        # Query all keywords from the collection
        results = client.query(
            collection_name=collection_name,
            #expr='',  # No filtering, query all records
            output_fields=["keywords"],  # Specify the field to retrieve
            limit = 10000
        )

        # Extract keywords and ensure uniqueness using a set
        keywords = {record.get("keywords") for record in results if record.get("keywords")}
        print(f"Retrieved {len(keywords)} unique keywords.")
        return keywords
    except Exception as e:
        print(f"An error occurred during keyword retrieval: {e}")
        return set()

if __name__=='__main__':
    pass
    # firewall_all_keywords('')

#{'Parkinson’s disease, anhedonia, levodopa dosage, mortality, predictive factors', 'Acute encephalitis syndrome (AES),
# anti-NMDAR encephalitis, autoimmune encephalitis, children, immune mediated encephalitis, viral encephalitis', 'Craniotomy,
# Intracranial bleeding, Neurosurgery, Outcome, Traumatic brain injury', 'fat deposition heterogeneity, insulin resistance,
# non-alcoholic fatty liver disease, non-alcoholic fatty pancreas disease, obesity', 'Aneurysmal Subarachnoid Hemorrhage,
# Functional outcome, Glucose/Potassium Index', 'atrial fibrillation, cardiovascular diseases, echocardiography, ischemic attack,
# transient, stroke', 'Anti-Müllerian hormone, acetaminophen/paracetamol, medication overuse headache,
# non-steroidal anti-inflammatory drugs, simple analgesics', 'Surpass Evolve, flow diversion, intracranial aneurysm,
# medium, small', 'CDD, CDKL5 Deficiency Disorder, comorbidities, multidimensional, resistant epilepsy', 'clinical phenotype,
# frailty, microbiome, nursing home, poor nutrition', 'Alzheimer’s disease, Alzheimer’s pathology, Enlarged perivascular spaces,
# Longitudinal analysis, Multicentre study, Virchow–Robin spaces', 'Genetic overlap, Genome-wide association study,
# Mendelian randomization, Multiple sclerosis, Vitamin D', 'Health knowledge, attitudes, practice, rabies virus, Colombia',
# 'Elderly, Glioblastoma, Glioma, Score', 'anticoagulation, atrial fibrillation, cardioembolism, cerebral infarction,
# cryptogenic ischemic stroke, electrocardiographic monitoring', 'Alzheimer’s disease, cathepsins, mendelian randomization,
# pathological features', 'NR', 'Mediation analysis, Mendelian randomization, Observational study, Socioeconomic status, Stroke'
# 'accuracy, acute ischaemic stroke, continuous glucose monitoring, mechanical thrombectomy', 'Arterial dissection, Diagnosis,
# Headache, Neck pain, Referral and consultation, Stroke', 'Body composition, Composición corporal, Errores innatos del metabolismo,
# Estado nutricional, Fenilcetonuria, Inborn errors of metabolism, Nutritional status, Phenylketonuria',
# 'Intracranial atherosclerotic disease, acute ischaemic stroke, basilar artery infarction, basilar artery stenting',
# 'Alzheimer’s disease, amyloid-related imaging abnormalities, lecanemab, mild cognitive impairment', 'Intracranial aneurysm,
# Mortality, Risk factors, Subarachnoid hemorrhage, Survival', 'Gamma knife radiosurgery, Neurosurgery, Pituitary adenoma,
# Stereotactic radiosurgery', 'Follow-up, LAMA2, Merosin-deficient congenital muscular dystrophy type 1A (MDC1A), Natural history,
# Outcome measures, SELENON, SEPN1, Trial readiness', 'Mycobacterium tuberculosis, Streptococcus, brain abscess, infection, morbidity,
# mortality', 'Cost-effectiveness, End effector robot, Robotics-assisted therapy, Stroke, Tele-monitoring, Telerehabilitation, Upper limb',
# 'coronary artery bypass grafting, percutaneous coronary intervention, surgical aortic valve replacement,
# transcatheter aortic valve\xa0replacement', 'energy expenditure, indirect calorimetry, intracerebral hemorrhage,
# neurocritical care, nutrition, subarachnoid hemorrhage, traumatic brain injury', 'Brain imaging, Early brain injury,
# Subarachnoid hemorrhage', 'Bisphenol, Kidney, electrolyte, toxicity', 'patent foramen ovale, right-to-left shunt, stroke recurrence,
# transesophageal echocardiography, white matter lesions', 'Auditory brainstem implantation, Brain relaxation, Hypertonic saline,
# Mannitol, Osmotherapy, Pediatrics', 'dementia, feeding behaviour, longitudinal studies, malnutrition, predictive value of tests',
# 'Adult neurology, Fatigue, Gait Analysis, Neuromuscular disease', 'Anxiety, Cannabidiol oil, Depression, Drug-resistant focal epilepsy,
# Psychiatry, Quality of life', 'Clinical quality registry, Community health services, General practice, Metabolic diseases,
# Prevention and control, Risk factors, Treatment outcome', 'adenotonsillectomy, apnea-hypopnea index, functional prediction,
# gut microbiome, obstructive sleep apnea', 'Dysphagia, Modified barium swallow study, Small vessel disease, Stroke',
# 'PFO morphotype, PFO‐associated stroke, high‐stroke‐risk PFO channels, low‐stroke‐risk PFO channels, nomogram',
# 'Arteries, Brain, CADASIL, Magnetic resonance angiography, Neural networks (computer)', 'high‐intensity focused ultrasound,
# large vessel occlusion, sonothrombolysis, stroke', 'Admission blood glucose, Hemoglobin A1c, Idiopathic pulmonary arterial hypertension,
# Mediation, Outcomes, Stress hyperglycemia ratio', 'Coronary Artery Bypass, Heart Valve Prosthesis Implantation, STROKE',
# 'gait deviation index, isokinetic dynamometry, machine learning, sensors, stroke', 'Choline alfoscerate, Claims database,
# Cox regression model, Dementia, Survival analysis', 'GLIM criteria, food consumption, malnutrition, plate waste method,
# post-stroke, rehabilitation', 'Gut microbiome, Ketogenic diet, Metabolomics, Pharmaco-resistant epilepsy, Plasmalogens',
# "Alzheimer's disease and related dementias, cholinesterase inhibitors, dementia, medicare", 'Cohort study, Complications,
# Diabetes mellitus, Major adverse cardiovascular and cerebrovascular events, Noncardiac surgery, Perioperative medicine,
# Stress hyperglycemia ratio', 'BPSD, LTCFs, dementia, depression, older adults, trazodone', 'FLOW800, Hemodynamics, Moyamoya disease,
# Perioperative complication, Self-recirculation network', 'Aneurysmal subarachnoid hemorrhage, Cerebrospinal fluid,
# Enzyme-linked adsorption assay, Interleukin-4, Outcome, Serum', 'Delayed cerebral ischemia, Platelets, Subarachnoid hemorrhage',
# 'Chronic obstructive pulmonary disease, association rule mining, comorbidities, daily expenses, length of stay, one-year readmission',
# 'Acute ischemic stroke, Rural setting, Tenecteplase, rtPA', 'Diagnosis, Dyspnea, Heart failure, Lung, Ultrasound', 'Antibodies,
# Autoimmune Diseases, Magnetic Resonance Imaging, Systemic Lupus Erythematosus', 'HIV/AIDS, MRI, cerebral small vessel disease,
# cognitive impairment, non-classical monocytes', '18F-Fluorodeoxyglucose-positron emission tomography, Alzheimer’s disease,
# Brain aging, Cerebrospinal fluid, Cognitive impairment, Dementia'}


# #testing
# items = [
#     'dementia, feeding behaviour, longitudinal studies, malnutrition, predictive value of tests',
#     'clinical phenotype, frailty, microbiome, nursing home, poor nutrition',
#     'gait deviation index, isokinetic dynamometry, machine learning, sensors, stroke',
#     'clinical outcomes, inherited metabolic disorders, kidney transplantation, post-transplant care',
#     'Cost-effectiveness, End effector robot, Robotics-assisted therapy, Stroke, Tele-monitoring, Telerehabilitation, Upper limb',
#     'NR',
#     'Bisphenol, Kidney, electrolyte, toxicity',
#     'Antibodies, Autoimmune Diseases, Magnetic Resonance Imaging, Systemic Lupus Erythematosus',
#     'NR',
#     'Intracranial atherosclerotic disease, acute ischaemic stroke, basilar artery infarction, basilar artery stenting'
# ]

# #correct format
# split_items = [item.strip() for sublist in items for item in sublist.split(',')]

# # String to check
# input_string = "machine learning."

# input_string_false = 'machine.'

# # Check if any item from the list is in the input_string
# contains_item = any(item.lower() in input_string.lower() for item in split_items)

# contains_item_false = any(item.lower() in input_string_false.lower() for item in split_items)

# print(contains_item)

# print(contains_item_false)

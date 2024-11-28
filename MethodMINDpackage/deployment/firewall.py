def firewall(text_input, data):
    key_words = data['Keywords'].tolist()
    split_items = [item.strip() for sublist in key_words for item in sublist.split(',')]
    return any(item.lower() in text_input.lower() for item in split_items)




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

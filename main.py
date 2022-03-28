from text_comp.text_comp import *
from key_value_cells.key_value_cell import *
from hand_writing.breaking_and_classifying import *

#get document features dataframe
doc_dataframe=get_text_comp_features()
print(doc_dataframe)

#get page_wise key_value and cells dataframe
#key_val_cells_dataframe=get_key_cell_features()
#print(key_val_cells_dataframe)

#get page_wise hand_writing percentage
#hand_writing_percentage_dataframe=hand_written()
#print(hand_writing_percentage_dataframe)

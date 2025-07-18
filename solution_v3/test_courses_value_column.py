import pandas as pd
import os

# Paths
dataset_dir = 'dataset'
courseplan_path = os.path.join(dataset_dir, 'PRJT2_Support_Data_V3.xlsx')
test_output_path = 'test_courses_output.xlsx'

print('[TEST] Reading courseplan from:', courseplan_path)
df_courses = pd.read_excel(courseplan_path, sheet_name='CoursePlan')
df_courses.columns = [c.strip() for c in df_courses.columns]
melted = df_courses.melt(
    id_vars=['Course', 'Class', 'Year', 'Semester'],
    value_vars=['T', 'TP', 'PL'],
    var_name='Type', value_name='Duration'
)
melted = melted.dropna(subset=['Duration'])
melted = melted[['Course', 'Year', 'Semester', 'Type', 'Duration']]
melted['Class_Group'] = ''
melted['Professor'] = ''
melted['Value'] = 1
print('[TEST] melted columns before reorder:', list(melted.columns))
melted = melted[['Course', 'Year', 'Semester', 'Type', 'Duration', 'Class_Group', 'Professor', 'Value']]
print('[TEST] FINAL melted columns before to_excel:', list(melted.columns))
print('[TEST] FINAL melted sample before to_excel:\n', melted.head())
melted.to_excel(test_output_path, index=False)
print(f'[TEST] Written to {test_output_path}')
# Read back and print
df_check = pd.read_excel(test_output_path)
print('[TEST] Read back columns:', list(df_check.columns))
print('[TEST] Read back sample:\n', df_check.head()) 
import pandas as pd

# Read excel files into separate dataFrames
df1 = pd.read_excel('ModernaSCOPE/Scope_Firmware/Python/SPEGrid/SPETestingGrid1.xlsx', index_col=0) # SPE number on sensing pcb table
df2 = pd.read_excel('ModernaSCOPE/Scope_Firmware/Python/SPEGrid/SPETestingGrid2.xlsx', index_col=0) # Electrode ID number in firmware table
df3 = pd.read_excel('ModernaSCOPE/Scope_Firmware/Python/SPEGrid/SPETestingGrid3.xlsx', index_col=0) # Interface board to SPE number on sensing pcb table

# Create empty dataframe to store the results (Interface board to electrode ID in firmware)
result_df = pd.DataFrame(index=df3.index, columns=df3.columns)

# Iterate through each cell of df3
for row_label, row in df3.iterrows():
    for col_label, cell_value in row.items():
        # Find the corresponding row and column index in df1
        row_index_df1 = df1.index[df1.eq(cell_value).any(axis=1)].tolist()
        col_index_df1 = df1.columns[df1.eq(cell_value).any(axis=0)].tolist()

        if row_index_df1 and col_index_df1:
            # Use the first matching index from df1 to locate the value in df2
            result_value = df2.loc[row_index_df1[0], col_index_df1[0]]
        else:
            result_value = None
        
        # Store the result in the result dataframe at the same index as df3
        result_df.at[row_label, col_label] = result_value

# Print the result dataframe (Interface board to electrode ID in firmware)
print(result_df)

# Copy result dataframe to clipboard
result_df.to_clipboard()


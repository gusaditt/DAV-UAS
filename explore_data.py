import pandas as pd

df = pd.read_excel('coffe_shop_final.xlsx')
df['date'] = pd.to_datetime(df['date'])

with open('data_info.txt', 'w') as f:
    f.write(f"Shape: {df.shape}\n\n")
    f.write("Dtypes:\n")
    f.write(df.dtypes.to_string() + "\n\n")
    f.write("Unique branches:\n")
    for b in df['branch_name'].unique():
        f.write(f"  {b}\n")
    f.write(f"\nYears: {sorted(df['date'].dt.year.unique())}\n")
    f.write(f"\nSample row:\n")
    for col in df.columns:
        f.write(f"  {col}: {df.iloc[0][col]}\n")
    f.write(f"\nRevenue sum: {df['total_revenue'].sum():,.0f}\n")
    f.write(f"Cups sold sum: {df['total_cups_sold'].sum():,.0f}\n")
    f.write(f"Transactions sum: {df['total_transactions'].sum():,.0f}\n")
    f.write(f"Avg ticket size mean: {df['avg_ticket_size'].mean():,.0f}\n")
    f.write(f"Satisfaction mean: {df['customer_satisfaction'].mean():.2f}\n")
    f.write(f"Satisfaction range: {df['customer_satisfaction'].min()} - {df['customer_satisfaction'].max()}\n")
    f.write(f"\nUnique categories: {df['top_selling_category'].unique().tolist()}\n")
    f.write(f"Unique branch_type: {df['branch_type'].unique().tolist()}\n")
    f.write(f"Unique promo_type: {df['promo_type'].unique().tolist()}\n")

print("Data info saved to data_info.txt")

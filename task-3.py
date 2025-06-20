import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import calendar # To get month names

# --- 1. Create Dummy Data (Replace with your actual data loading) ---
# Simulating a year's worth of data with sales across regions and categories
print("Generating dummy data...")
np.random.seed(42) # for reproducibility

dates = pd.to_datetime(pd.date_range(start='2024-01-01', end='2024-12-31', freq='D'))
regions = ['West', 'East', 'Central', 'South']
categories = ['Technology', 'Furniture', 'Office Supplies']

data = []
for date in dates:
    for _ in range(np.random.randint(1, 5)): # Simulate multiple sales per day
        region = np.random.choice(regions, p=[0.3, 0.25, 0.25, 0.2])
        category = np.random.choice(categories, p=[0.4, 0.35, 0.25])
        
        # Simulate sales amount, with Technology generally higher
        if category == 'Technology':
            sales_amount = np.random.uniform(100, 5000) * (1 + date.month / 12) # Trend up towards year end
        elif category == 'Furniture':
            sales_amount = np.random.uniform(50, 3000) * (1 + date.month / 12 * 0.8)
        else:
            sales_amount = np.random.uniform(20, 1500) * (1 + date.month / 12 * 0.7)
            
        data.append([date, region, category, sales_amount])

df = pd.DataFrame(data, columns=['OrderDate', 'Region', 'Category', 'SalesAmount'])

# Aggregate to monthly level for the time series chart
df['Month'] = df['OrderDate'].dt.month
df['YearMonth'] = df['OrderDate'].dt.to_period('M')

print("Dummy data generated successfully.")
print(df.head())
print("\nDataFrame Info:")
df.info()

# --- 2. Dashboard Plotting ---

# Define colors for the dashboard (matching the purple theme)
PURPLE_PRIMARY = '#8A2BE2' # A bright purple similar to the image
PURPLE_LIGHT = '#BE90D4'
PURPLE_DARK = '#4B0082' # Darker purple for background elements
PURPLE_ACCENT = '#9932CC' # Slightly different purple for contrast

BACKGROUND_COLOR = '#1A1A1A' # Dark background
TEXT_COLOR = 'white'
GRID_COLOR = '#444444'

# Function to format sales values to M/K
def format_sales(value, pos):
    if value >= 1_000_000:
        return f'{value/1_000_000:.1f}M'
    elif value >= 1_000:
        return f'{value/1_000:.0f}K'
    return f'{value:.0f}'


# Set up the figure and axes for the dashboard layout
# We'll create a figure and then manually place axes for each plot
fig = plt.figure(figsize=(16, 9), facecolor=BACKGROUND_COLOR) # Overall dashboard size
fig.patch.set_facecolor(BACKGROUND_COLOR) # Set figure background

# GridSpec for flexible subplots (adjust as needed for precise layout)
gs = fig.add_gridspec(nrows=3, ncols=3, height_ratios=[0.1, 0.45, 0.45], width_ratios=[1, 1, 1])

# --- Title ---
ax_title = fig.add_subplot(gs[0, :]) # Top row, spanning all columns
ax_title.text(0.02, 0.5, 'SALES ANALYSIS', color=TEXT_COLOR, fontsize=24, fontweight='bold', va='center')
ax_title.set_facecolor(BACKGROUND_COLOR)
ax_title.axis('off') # Hide axes for the title

# --- Region Slicers (Simulated as text boxes for static plot) ---
# These are interactive elements in Power BI, but static text for Matplotlib
region_slicer_texts = ['Central', 'East', 'South', 'West']
for i, region in enumerate(region_slicer_texts):
    # Adjust position based on index to space them out
    ax = fig.add_subplot(gs[0, i+0.8:]) # Adjust column span/start for positioning
    ax.text(0.5, 0.5, region, color=TEXT_COLOR, fontsize=14, fontweight='bold', ha='center', va='center')
    ax.set_facecolor(PURPLE_ACCENT) # Slicer background
    ax.patch.set_edgecolor(BACKGROUND_COLOR) # Border color
    ax.patch.set_linewidth(2) # Border width
    ax.axis('off')


# --- Plot 1: Sum of Sales by Region (Bar Chart) ---
ax1 = fig.add_subplot(gs[1, 0]) # Row 1, Col 0 (using 0-indexed rows of gs[1, ...])
region_sales = df.groupby('Region')['SalesAmount'].sum().sort_values(ascending=False)
bars = ax1.barh(region_sales.index, region_sales.values, color=PURPLE_PRIMARY)
ax1.set_title('Sum of Sales by Region', color=TEXT_COLOR, fontsize=16)
ax1.set_xlabel('Sum of Sales', color=TEXT_COLOR)
ax1.tick_params(axis='x', colors=TEXT_COLOR)
ax1.tick_params(axis='y', colors=TEXT_COLOR)
ax1.set_facecolor(BACKGROUND_COLOR) # Plot area background
ax1.grid(axis='x', linestyle='--', alpha=0.7, color=GRID_COLOR) # Horizontal grid lines

# Set custom x-axis ticks and labels
max_sales = region_sales.max()
xticks = np.linspace(0, max_sales, 5) # 5 ticks
ax1.set_xticks(xticks)
ax1.xaxis.set_major_formatter(plt.FuncFormatter(format_sales))

# Add data labels to bars
for bar in bars:
    width = bar.get_width()
    ax1.text(width + (max_sales * 0.02), bar.get_y() + bar.get_height()/2,
             format_sales(width, None), ha='left', va='center', color=TEXT_COLOR, fontsize=10)

# Invert y-axis to match image (West at top)
ax1.invert_yaxis()


# --- Plot 2: Sum of Sales by Category (Donut Chart) ---
ax2 = fig.add_subplot(gs[1, 1:]) # Row 1, Col 1-2 (spanning two columns)
category_sales = df.groupby('Category')['SalesAmount'].sum()

# Custom colors for categories
category_colors = [PURPLE_ACCENT, PURPLE_PRIMARY, PURPLE_LIGHT] # Adjusted for different categories

wedges, texts, autotexts = ax2.pie(category_sales,
                                   autopct=lambda p: f'{p:.1f}% ({format_sales(p * sum(category_sales)/100, None)})',
                                   startangle=90,
                                   counterclock=False, # To match segment order
                                   colors=category_colors,
                                   wedgeprops=dict(width=0.4, edgecolor=BACKGROUND_COLOR)) # Donut hole

# Center text for total sales (optional, but good for donuts)
total_sales_value = df['SalesAmount'].sum()
# ax2.text(0, 0, f'{format_sales(total_sales_value, None)}', ha='center', va='center',
#          fontsize=20, color=TEXT_COLOR, fontweight='bold')

# Adjust autopct text color
for autotext in autotexts:
    autotext.set_color(TEXT_COLOR)
    autotext.set_fontsize(10) # Smaller font for percentage and value

# Add legend outside the circle for category names
ax2.legend(wedges, category_sales.index, title="Category", loc="center left", bbox_to_anchor=(0.95, 0.5),
           frameon=False, labelcolor=TEXT_COLOR, title_fontsize=12)
ax2.set_title('Sum of Sales by Category', color=TEXT_COLOR, fontsize=16)
ax2.set_facecolor(BACKGROUND_COLOR)
ax2.set_aspect('equal') # Ensures circular pie


# --- Plot 3: Sum of Sales by Month (Area/Line Chart) ---
ax3 = fig.add_subplot(gs[2, :]) # Row 2, spanning all columns
monthly_sales = df.groupby('Month')['SalesAmount'].sum().sort_index()

# Get ordered month names
month_names = [calendar.month_abbr[m] for m in monthly_sales.index]

ax3.plot(month_names, monthly_sales.values, color=PURPLE_PRIMARY, linewidth=2, marker='o', markersize=4)
ax3.fill_between(month_names, monthly_sales.values, color=PURPLE_PRIMARY, alpha=0.3) # Area fill
ax3.set_title('Sum of Sales by Month', color=TEXT_COLOR, fontsize=16)
ax3.set_xlabel('Month', color=TEXT_COLOR)
ax3.set_ylabel('Sum of Sales', color=TEXT_COLOR)
ax3.tick_params(axis='x', colors=TEXT_COLOR, rotation=45) # Rotate month labels if they overlap
ax3.tick_params(axis='y', colors=TEXT_COLOR)
ax3.set_facecolor(BACKGROUND_COLOR) # Plot area background
ax3.grid(True, linestyle='--', alpha=0.7, color=GRID_COLOR)

# Format y-axis ticks
max_monthly_sales = monthly_sales.max()
yticks = np.linspace(0, max_monthly_sales * 1.1, 4) # 4 ticks, slightly above max
ax3.set_yticks(yticks)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(format_sales))

# Adjust layout to prevent overlapping titles/labels
plt.tight_layout(rect=[0, 0, 1, 0.95]) # Adjust rect to make space for the main title
plt.show()

print("\nStatic dashboard plots generated.")

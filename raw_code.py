import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
import pandas as pd
import seaborn as sns
import datetime

PRISM_DISCLOSURE = datetime.datetime(2013, 6, 6)

# Get and inspect the data
df = pd.read_csv('./data/terrorism_data.csv', index_col=0, parse_dates=[3], infer_datetime_format=True)
print(df.head())
print(df.describe())


# Build a function for printing the data in the desired way
def make_figure(in_frame, split_at=None, title='Article View Trends'):
    """
    Takes the input data and creates a plot similar to figure 3 in the paper
    :param dataframe: A pandas data frame with the dates (dtype=PeriodIndex) as index and views as its only column
    :param split_at: The date at which the data shall be split
    :param title: Figure title
    :return: Plots the figure
    """
    # Prepare the dataframe for seaborn (https://stackoverflow.com/questions/52112979/having-xticks-to-display-months-in-a-seaborn-regplot-with-pandas)
    dataframe = in_frame.copy()
    dataframe.index = dataframe.index.to_timestamp()
    dataframe['date_ordinal'] = mdates.date2num(dataframe.index)
    colors = {'Monthly Page Views': 'blue', 'trend': 'darkgrey'}
    # The actual plot
    fig, ax = plt.subplots(figsize=[18, 6])
    if split_at is None:
        sns.regplot(x='date_ordinal', y='views', data=dataframe, ax=ax, color=colors['Monthly Page Views'])
    else:
        colors['Prism Disclosure, 6/6/2013'] = 'red'
        df1 = dataframe.loc[dataframe.index < split_at]
        df2 = dataframe.loc[dataframe.index >= split_at]
        sns.regplot(x='date_ordinal', y='views', data=df1, ax=ax, color=colors['Monthly Page Views'],
                    scatter_kws={'color': colors['Monthly Page Views'], 's': 30},
                    line_kws={'color': colors['trend']})
        sns.regplot(x='date_ordinal', y='views', data=df2, ax=ax, color=colors['Monthly Page Views'],
                    scatter_kws={'color': colors['Monthly Page Views'], 's': 30},
                    line_kws={'color': colors['trend']})
        ax.vlines(mdates.date2num(split_at), 0, 1, color=colors['Prism Disclosure, 6/6/2013'], transform=ax.get_xaxis_transform(), label=split_at)
    print("debug")
    # Formatting and Visualization
    fig.patch.set_facecolor('lightgrey')
    fig.suptitle(title)
    ax.set_xlabel('Month / Year')
    ax.set_ylabel('Monthly Page Views')
    ax.set_xlim(dataframe['date_ordinal'].min() - 15, dataframe['date_ordinal'].max() + 15)
    # Seaborn has problems handling datetime objects for labeling, adjusting the x-Axis to display them as desired
    loc = mdates.MonthLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(loc))
    # Add a custom legend
    legend_patches = []
    for entry, c in colors.items():
        legend_patches.append(mpatches.Patch(color=c, label=entry))
    font = FontProperties()
    font.set_size('large')
    fig.autofmt_xdate()
    plt.legend(handles=legend_patches, title='Legend', bbox_to_anchor=(0, 0), loc='lower left', prop=font,
               ncol=len(legend_patches), fancybox=True, shadow=True)


# Analyze data for outliers and remove them if necessary
df_months = df.copy()
df_months['date'] = df['date'].dt.to_period('M')  # Reduction to month/year
monthly_views = df_months.groupby('date').sum()
make_figure(monthly_views, split_at=PRISM_DISCLOSURE, title='Pre and Post June 2013 Article View Trends')

# Looks weird, how many 0 pageviews are there?
no_views = df_months[['views', 'date']].loc[df_months['views'] == 0].groupby('date').count()
for month in df_months['date'].unique():
    if month in no_views.index.tolist():
        pass
    else:
        no_views = no_views.append(pd.DataFrame([0], [month]))
no_views.sort_index(inplace=True)
fig, ax = plt.subplots(figsize=[18, 6])
ax.set_xlabel("Year - Month")
ax.set_ylabel("Number of Article-days with 0 Views")
sns.barplot(x=no_views.index, y=no_views['views'], data=no_views, ax=ax)
fig.autofmt_xdate()

# Perform the actual replication
make_figure(monthly_views.loc[:datetime.date(2014, 6, 30)], split_at=PRISM_DISCLOSURE,
            title='Pre and Post June 2013 Article View Trends, Outliers Excluded')


plt.show()

"""INFOSCI 301 idiom recipes. Replace placeholder data and verify every transformation."""

# 01 · Compare / Values and ranks / Sorted bar
s = df.groupby('group')['value'].sum().sort_values()
s.plot.barh(color='#315EFB')

# 02 · Compare / Values and ranks / Dot plot
s = df.groupby('group')['value'].sum().sort_values()
plt.hlines(s.index, 0, s); plt.scatter(s, s.index)

# 03 · Compare / Values and ranks / Lollipop
s = df.groupby('group')['value'].sum().sort_values()
plt.vlines(s.index, 0, s); plt.scatter(s.index, s)

# 04 · Compare / Change and groups / Slope graph
wide = df.pivot(index='group', columns='period', values='value')
for _, row in wide.iterrows(): plt.plot(wide.columns, row, marker='o')

# 05 · Compare / Change and groups / Dumbbell
wide = df.pivot(index='group', columns='condition', values='value')
plt.hlines(wide.index, wide.iloc[:,0], wide.iloc[:,1]); plt.scatter(wide.iloc[:,0], wide.index); plt.scatter(wide.iloc[:,1], wide.index)

# 06 · Compare / Change and groups / Line chart
for key, g in df.sort_values('time').groupby('group'):
    plt.plot(g.time, g.value, marker='o', label=key)

# 07 · Compare / Change and groups / Small multiples
import seaborn as sns
sns.relplot(data=df, x='time', y='value', col='group', col_wrap=3, kind='line', facet_kws={'sharey':True})

# 08 · Compare / Composition and profiles / Stacked bar
wide = df.pivot_table(index='whole', columns='part', values='value', aggfunc='sum')
wide.plot.bar(stacked=True)

# 09 · Compare / Composition and profiles / 100% stacked
wide = df.pivot_table(index='whole', columns='part', values='value', aggfunc='sum')
(wide.div(wide.sum(axis=1), axis=0)).plot.bar(stacked=True)

# 10 · Compare / Composition and profiles / Donut
s = df.groupby('part')['value'].sum()
plt.pie(s, labels=s.index, wedgeprops={'width':.38}, autopct='%1.0f%%')

# 11 · Compare / Composition and profiles / Aligned profile
for key, g in df.groupby('entity'):
    plt.plot(g.metric, g.value, marker='o', label=key)

# 12 · Compare / Composition and profiles / Radar
theta = np.linspace(0, 2*np.pi, len(values), endpoint=False)
ax = plt.subplot(projection='polar'); ax.plot(np.r_[theta,theta[0]], np.r_[values,values[0]])

# 13 · Understand variation / One variable / Histogram
import seaborn as sns
sns.histplot(data=df, x='value', bins=20)

# 14 · Understand variation / One variable / KDE
import seaborn as sns
sns.kdeplot(data=df, x='value', bw_adjust=1, fill=True)

# 15 · Understand variation / One variable / ECDF
import seaborn as sns
sns.ecdfplot(data=df, x='value')

# 16 · Understand variation / One variable / Box plot
import seaborn as sns
sns.boxplot(data=df, x='group', y='value'); sns.stripplot(data=df, x='group', y='value', color='black', alpha=.35)

# 17 · Understand variation / One variable / Violin
import seaborn as sns
sns.violinplot(data=df, x='group', y='value', inner='quartile')

# 18 · Understand variation / One variable / Raincloud
import PtitPrince as pt
pt.RainCloud(data=df, x='group', y='value', orient='v')

# 19 · Understand variation / Relationships and density / Scatterplot
import altair as alt
alt.Chart(df).mark_circle().encode(x='x:Q', y='y:Q', color='group:N', tooltip=list(df.columns))

# 20 · Understand variation / Relationships and density / Regression view
import seaborn as sns
sns.regplot(data=df, x='x', y='y', ci=95)

# 21 · Understand variation / Relationships and density / Hexbin
plt.hexbin(df.x, df.y, gridsize=24, mincnt=1, cmap='viridis'); plt.colorbar(label='count')

# 22 · Understand variation / Relationships and density / Pair plot
import seaborn as sns
sns.pairplot(df, vars=['a','b','c'], hue='group', corner=True)

# 23 · Understand variation / Relationships and density / Correlation heatmap
import seaborn as sns
corr = df.select_dtypes('number').corr()
sns.heatmap(corr, vmin=-1, vmax=1, cmap='vlag', annot=True)

# 24 · Understand variation / Relationships and density / 2D contour
grid = df.pivot(index='y', columns='x', values='z')
plt.contourf(grid.columns, grid.index, grid.values, levels=10, cmap='viridis'); plt.colorbar()

# 25 · Understand variation / Uncertainty and models / Interval / forest
plt.errorbar(df.estimate, df.label, xerr=[df.estimate-df.lower, df.upper-df.estimate], fmt='o')
plt.axvline(0, color='0.5', lw=1)

# 26 · Understand variation / Uncertainty and models / Fan chart
plt.fill_between(df.time, df.q10, df.q90, alpha=.18)
plt.fill_between(df.time, df.q25, df.q75, alpha=.32); plt.plot(df.time, df.median)

# 27 · Understand variation / Uncertainty and models / Calibration
from sklearn.calibration import CalibrationDisplay
CalibrationDisplay.from_predictions(df.outcome, df.probability, n_bins=10)

# 28 · Understand variation / Uncertainty and models / Residual view
import seaborn as sns
sns.residplot(data=df, x='fitted', y='observed', lowess=True); plt.axhline(0, color='0.5')

# 29 · Reveal structure / Hierarchy and flow / Treemap
import plotly.express as px
px.treemap(df, path=['parent','child'], values='value', color='value')

# 30 · Reveal structure / Hierarchy and flow / Sunburst
import plotly.express as px
px.sunburst(df, path=['level1','level2'], values='value', color='level1')

# 31 · Reveal structure / Hierarchy and flow / Sankey
import plotly.graph_objects as go
go.Figure(go.Sankey(node={'label':labels}, link={'source':source,'target':target,'value':value}))

# 32 · Reveal structure / Hierarchy and flow / Alluvial
import plotly.express as px
px.parallel_categories(df, dimensions=['stage1','stage2','stage3'], color='weight')

# 33 · Reveal structure / Cycles and opposition / Polar / Burtin
from pycirclize import Circos
# Map genuinely cyclic sectors and values; see the official pyCirclize examples.

# 34 · Reveal structure / Cycles and opposition / Population pyramid
y = np.arange(len(df))
plt.barh(y, -df.left, label='Left'); plt.barh(y, df.right, label='Right'); plt.axvline(0, color='0.3')

# 35 · Reveal structure / Arranged tables / Ordered heatmap
import seaborn as sns
ordered = matrix.loc[row_order, col_order]
sns.heatmap(ordered, cmap='viridis')

# 36 · Reveal structure / Arranged tables / Faceted table
styled = df.sort_values(['group','item']).style.format(precision=2).background_gradient(subset=['value'])
display(styled)

# 37 · Reveal structure / Arranged tables / Missingness matrix
import missingno as msno
msno.matrix(df.sort_values('group'))

# 38 · Reveal structure / Arranged tables / UpSet matrix
from upsetplot import UpSet, from_indicators
UpSet(from_indicators(['A','B','C'], df), show_counts=True).plot()

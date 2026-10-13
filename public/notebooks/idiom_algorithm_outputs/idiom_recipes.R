# INFOSCI 301 idiom recipes
# Replace placeholder data and verify every transformation.

# 01 · Compare / Values and ranks / Sorted bar
library(ggplot2)
ggplot(df, aes(reorder(group, value), value)) + geom_col(fill='#315EFB') + coord_flip()

# 02 · Compare / Values and ranks / Dot plot
library(ggplot2)
ggplot(df, aes(value, reorder(group, value))) + geom_point(size=3, colour='#315EFB')

# 03 · Compare / Values and ranks / Lollipop
library(ggplot2)
ggplot(df, aes(group, value)) + geom_segment(aes(xend=group, y=0, yend=value)) + geom_point(size=3)

# 04 · Compare / Change and groups / Slope graph
library(ggplot2)
ggplot(df, aes(period, value, group=group, colour=group)) + geom_line() + geom_point()

# 05 · Compare / Change and groups / Dumbbell
library(ggplot2)
ggplot(wide, aes(x=before, xend=after, y=group, yend=group)) + geom_segment() + geom_point(aes(x=before)) + geom_point(aes(x=after))

# 06 · Compare / Change and groups / Line chart
library(ggplot2)
ggplot(df, aes(time, value, colour=group)) + geom_line() + geom_point()

# 07 · Compare / Change and groups / Small multiples
library(ggplot2)
ggplot(df, aes(time, value)) + geom_line() + facet_wrap(~group) + coord_cartesian(ylim=range(df$value))

# 08 · Compare / Composition and profiles / Stacked bar
library(ggplot2)
ggplot(df, aes(whole, value, fill=part)) + geom_col()

# 09 · Compare / Composition and profiles / 100% stacked
library(ggplot2)
ggplot(df, aes(whole, value, fill=part)) + geom_col(position='fill') + scale_y_continuous(labels=scales::percent)

# 10 · Compare / Composition and profiles / Donut
library(ggplot2)
ggplot(df, aes(x=2, y=value, fill=part)) + geom_col() + coord_polar(theta='y') + xlim(.5, 2.5)

# 11 · Compare / Composition and profiles / Aligned profile
library(ggplot2)
ggplot(df, aes(metric, value, group=entity, colour=entity)) + geom_line() + geom_point()

# 12 · Compare / Composition and profiles / Radar
library(ggplot2)
ggplot(df, aes(metric, value, group=entity, colour=entity)) + geom_polygon(fill=NA) + coord_polar()

# 13 · Understand variation / One variable / Histogram
library(ggplot2)
ggplot(df, aes(value)) + geom_histogram(bins=20, fill='#315EFB', colour='white')

# 14 · Understand variation / One variable / KDE
library(ggplot2)
ggplot(df, aes(value)) + geom_density(fill='#315EFB', alpha=.3, adjust=1)

# 15 · Understand variation / One variable / ECDF
library(ggplot2)
ggplot(df, aes(value)) + stat_ecdf(geom='step')

# 16 · Understand variation / One variable / Box plot
library(ggplot2)
ggplot(df, aes(group, value)) + geom_boxplot() + geom_jitter(width=.08, alpha=.3)

# 17 · Understand variation / One variable / Violin
library(ggplot2)
ggplot(df, aes(group, value)) + geom_violin() + geom_boxplot(width=.12)

# 18 · Understand variation / One variable / Raincloud
library(ggplot2); library(ggdist)
ggplot(df, aes(group, value, fill=group)) + stat_halfeye() + geom_jitter(width=.08, alpha=.3)

# 19 · Understand variation / Relationships and density / Scatterplot
library(ggplot2)
ggplot(df, aes(x, y, colour=group)) + geom_point(alpha=.65)

# 20 · Understand variation / Relationships and density / Regression view
library(ggplot2)
ggplot(df, aes(x, y)) + geom_point() + geom_smooth(method='lm', se=TRUE)

# 21 · Understand variation / Relationships and density / Hexbin
library(ggplot2); library(hexbin)
ggplot(df, aes(x, y)) + geom_hex(bins=24) + scale_fill_viridis_c()

# 22 · Understand variation / Relationships and density / Pair plot
library(GGally)
ggpairs(df, columns=c('a','b','c'), aes(colour=group, alpha=.5))

# 23 · Understand variation / Relationships and density / Correlation heatmap
library(ComplexHeatmap)
Heatmap(cor(df[c('a','b','c')], use='pairwise.complete.obs'), name='r')

# 24 · Understand variation / Relationships and density / 2D contour
library(ggplot2)
ggplot(df, aes(x, y, z=z)) + geom_contour_filled() + coord_equal()

# 25 · Understand variation / Uncertainty and models / Interval / forest
library(forestplot)
forestplot(labeltext=df$label, mean=df$estimate, lower=df$lower, upper=df$upper, zero=0)

# 26 · Understand variation / Uncertainty and models / Fan chart
library(ggplot2)
ggplot(df, aes(time, median)) + geom_ribbon(aes(ymin=q10,ymax=q90), alpha=.18) + geom_ribbon(aes(ymin=q25,ymax=q75), alpha=.32) + geom_line()

# 27 · Understand variation / Uncertainty and models / Calibration
library(ggplot2)
ggplot(calibration, aes(predicted, observed)) + geom_abline(slope=1, intercept=0, linetype=2) + geom_line() + geom_point()

# 28 · Understand variation / Uncertainty and models / Residual view
library(ggplot2)
ggplot(df, aes(fitted, residual)) + geom_hline(yintercept=0, colour='grey60') + geom_point() + geom_smooth(se=FALSE)

# 29 · Reveal structure / Hierarchy and flow / Treemap
library(ggplot2); library(treemapify)
ggplot(df, aes(area=value, fill=parent, label=child)) + geom_treemap() + geom_treemap_text()

# 30 · Reveal structure / Hierarchy and flow / Sunburst
library(plotly)
plot_ly(df, labels=~label, parents=~parent, values=~value, type='sunburst', branchvalues='total')

# 31 · Reveal structure / Hierarchy and flow / Sankey
library(networkD3)
sankeyNetwork(Links=links, Nodes=nodes, Source='source', Target='target', Value='value', NodeID='name')

# 32 · Reveal structure / Hierarchy and flow / Alluvial
library(ggplot2); library(ggalluvial)
ggplot(df, aes(axis1=stage1, axis2=stage2, axis3=stage3, y=weight)) + geom_alluvium(aes(fill=stage1)) + geom_stratum()

# 33 · Reveal structure / Cycles and opposition / Polar / Burtin
library(circlize)
# Map genuinely cyclic sectors and quantitative values; see the official circlize book.

# 34 · Reveal structure / Cycles and opposition / Population pyramid
library(ggplot2)
long$plot_value <- ifelse(long$side=='Left', -long$value, long$value)
ggplot(long, aes(plot_value, ordered_group, fill=side)) + geom_col() + geom_vline(xintercept=0)

# 35 · Reveal structure / Arranged tables / Ordered heatmap
library(ComplexHeatmap)
Heatmap(matrix[row_order, col_order], name='value', cluster_rows=FALSE, cluster_columns=FALSE)

# 36 · Reveal structure / Arranged tables / Faceted table
library(reactable)
reactable(df, groupBy='group', searchable=TRUE, defaultSorted='item')

# 37 · Reveal structure / Arranged tables / Missingness matrix
library(ComplexHeatmap)
Heatmap(is.na(df) * 1, name='missing', col=c('0'='white','1'='#C2413A'))

# 38 · Reveal structure / Arranged tables / UpSet matrix
library(ComplexHeatmap)
m = make_comb_mat(df[c('A','B','C')]); UpSet(m)

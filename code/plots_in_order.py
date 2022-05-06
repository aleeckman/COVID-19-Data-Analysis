import data_munging

# Plot 1: New cases vs Date
(p9.ggplot(WHO_covid_top_five, p9.aes(x='Date_reported', y='New_cases', group='Country', color='Country')) +
    p9.geom_smooth(span=.05, se=False, alpha = 1) 
 + p9.geom_point(alpha = 0.1)
 + p9.theme_538()
 + p9.xlab('Date')
 + p9.ylab('New Cases per Day')
 + p9.scale_x_datetime(date_breaks='2 month')
 + p9.theme(axis_text_x=p9.element_text(rotation=45, hjust=1))
)

# Plot 2:
(p9.ggplot(WHO_covid_top_five, p9.aes(x='Date_reported', y='New_deaths', group='Country', color='Country')) +
    p9.geom_smooth(span=.05, se=False, alpha = 1) 
 + p9.geom_point(alpha = 0.1)
 + p9.theme_538()
 + p9.xlab('Date')
 + p9.ylab('New Deaths per Day')
 + p9.scale_x_datetime(date_breaks='2 month')
 + p9.theme(axis_text_x=p9.element_text(rotation=45, hjust=1))
)

# Plot 3:
(p9.ggplot(containment_index_top_five, p9.aes(x='Date_reported', y='containment_index', group='Country', color='Country')) +
    p9.geom_line()
 + p9.theme_538()
 + p9.xlab('Date')
 + p9.ylab('Health and Containment Index')
 + p9.scale_x_datetime(date_breaks='2 month')
 + p9.theme(axis_text_x=p9.element_text(rotation=45, hjust=1))
)

# Plot 4: First Histogram
(p9.ggplot(containment_index, p9.aes(x='containment_index')) +
    p9.geom_histogram(binwidth=1, fill='green', alpha=.7)
 + p9.theme_538()
 + p9.xlab('Containment Index')
 + p9.ggtitle('Containment Index Values from 01/01/2020 to 05/26/2021')
)

#Plot 5:
(p9.ggplot(containment_index_post_ann, p9.aes(x='containment_index')) +
    p9.geom_histogram(binwidth=1, fill='green', alpha=.7)
 + p9.theme_538()
 + p9.xlab('Containment Index')
 + p9.ggtitle('Containment Index Values Following WHO Announcement')
)

# Plot 6: Government Effectiveness
(p9.ggplot(gov_eff_ind, p9.aes(x='Government Effectiveness: Estimate'))
 + p9.geom_density(fill='dodgerblue', color='dodgerblue', alpha = 0.2)
 + p9.theme_538()
)

#Plot 7: Inferential Beginning

fig1 = px.scatter(avg_con_ind, x='Gov_Eff_Per', y='avg(containment_index)',
                 color='avg(containment_index)', hover_name='Country', trendline='lowess')
fig1.show()

#Plot 8:
fig2 = px.scatter(avg_cc_by_gov_eff, x='Gov_Eff_Per', y='Cumulative_cases_pop_scaled',
                 color='Cumulative_cases_pop_scaled', hover_name='Country', trendline='lowess')
fig2.show()


#Plot 9: Nice slider ones
fig3 = px.scatter(eff_gov, x='containment_index', y='Cumulative_cases_pop_scaled', 
                 animation_frame='Date_reported',
                 labels = {'containment_index':'Containment Index', 
                           'Cumulative_cases_pop_scaled':'Percent of Population Infected'},
                 color = "Country", size = "Population", size_max=50,
                 range_x=[0,100], range_y=[-2,12],
                 animation_group="Country", hover_name='Country')
fig3.show()

# Plot 10: 
fig4 = px.scatter(eff_gov, x='containment_index', y='New_cases_pop_scaled', 
                 animation_frame='Date_reported',
                 labels = {'containment_index':'Containment Index', 
                           'New_cases_pop_scaled':'New Percent of Population Infected'},
                 color = "Country", size = "Population", size_max=50,
                 range_x=[0,100], range_y=[-0.05,0.15],
                 animation_group="Country", hover_name='Country')
fig4.show()

# Plot 11:
fig5 = px.line(pearson_corr_df, y="pearson_corr", title='Pearson Correlation between New Cases (Scaled) and Containment Index')
fig5.show()
import requests
import requests_cache
import pandas as pd
import numpy as np
import sqlalchemy as sqla
import plotnine as p9
import matplotlib.pyplot as plt
import datetime
import plotly 
import plotly.express as px
import fuzzymatcher
from plotly import *
from fuzzymatcher import link_table, fuzzy_left_join
import statsmodels.formula.api as sm

## Help Function
def fw_join_and_clean(df_main, df_right, join_by_left, join_by_right, keep, clean_by):
    
    merged_df = fuzzy_left_join(df_main, df_right, join_by_left, join_by_right)
    merged_df = merged_df[keep]
    
    merged_df = merged_df.rename(columns=clean_by)
    
    return(merged_df)


## Read In Data
sqlite_file = 'covid.sqlite'
covid_conn = sqla.create_engine('sqlite:///' + sqlite_file)
requests_cache.install_cache('iso_cache')

WHO_covid = pd.read_csv('../data/WHO-COVID-19-global-data.csv')
containment_index = pd.read_csv('../data/covid-containment-and-health-index.csv')
pop_stats = pd.read_csv('../data/API_SP.POP.TOTL_DS2_en_csv_v2_2252106.csv', skiprows = 4)
gov_eff_ind = pd.read_csv('../data/WGIData.csv')

#-------------------- WHO DATASET ---------------------#
WHO_covid['Date_reported'] = pd.to_datetime(WHO_covid['Date_reported'], format='%Y-%m-%d')
WHO_covid = WHO_covid.drop(columns=['Country_code', 'WHO_region'])

data_05_27_2021 = (WHO_covid[WHO_covid['Date_reported'] == '2021-05-27'])

total_num_cases = sum(data_05_27_2021['Cumulative_cases'])
total_num_deaths = sum(data_05_27_2021['Cumulative_deaths'])
mortality_rate = total_num_deaths / total_num_cases

print("As of 2021, the total number of cases reported is {} with the total number of deaths being {}"
     .format(total_num_cases, total_num_deaths))
print("This gives us an approximate mortality rate of {}% (NOTE: this percentage does not take into account time of infection and therefore is likely not fully accurate)".format(mortality_rate*100))

top_five_countries = data_05_27_2021.nlargest(5, 'Cumulative_cases')
WHO_covid_top_five = WHO_covid[WHO_covid['Country'].isin(top_five_countries['Country'])]

num_days = datetime.timedelta(26)
WHO_covid['Date_of_Impacting_Restrictions'] = WHO_covid['Date_reported'] - num_days

WHO_covid.to_sql('WHO_covid', covid_conn, if_exists='replace')
WHO_covid_post = pd.read_sql_query("select * from WHO_covid where Date_reported > '2020-03-11'",
                                               covid_conn)

WHO_covid_post['Date_reported'] = pd.to_datetime(WHO_covid_post['Date_reported'])
WHO_covid_post['Date_of_Impacting_Restrictions'] = pd.to_datetime(WHO_covid_post['Date_of_Impacting_Restrictions'])

WHO_covid_post = WHO_covid_post.drop(columns = 'index')

WHO_country_list = WHO_covid_post['Country'].unique()

WHO_covid_post = WHO_covid_post[WHO_covid_post['Country'] != 'United States Virgin Islands']


#-------------------- OXFORD DATASET ---------------------#
containment_index['Day'] = pd.to_datetime(containment_index['Day'], format='%Y-%m-%d')
containment_index = containment_index.rename(columns={'Day':'Date_reported', 'Entity':'Country'})
containment_index = containment_index.drop(columns = ['Code'])

top_five_countries_ci = top_five_countries.replace('United States of America', 'United States')
containment_index_top_five = containment_index[containment_index['Country'].isin(top_five_countries_ci['Country'])]

containment_index.to_sql('con_index', covid_conn, if_exists='replace')
containment_index_post_ann = pd.read_sql_query("select * from con_index where Date_reported > '2020-03-11'", covid_conn)

containment_index.to_sql('con_index', covid_conn, if_exists='replace')
containment_index_post = pd.read_sql_query("select * from con_index where Date_reported between '2020-02-14' and '2021-05-02'",
                                               covid_conn)

containment_index_post['Date_reported'] = pd.to_datetime(containment_index_post['Date_reported'])
containment_index_post = containment_index_post.drop(columns = 'index')

ci_country_list = containment_index_post['Country'].unique()

containment_index_post = containment_index_post[containment_index_post['Date_reported'] <= '2021-05-27']


#---------------------- MERGED DATASET --------------------#
merge_ci_WHO = fw_join_and_clean(df_main = containment_index_post, df_right = WHO_covid_post, 
                                 join_by_left=["Country", "Date_reported"], 
                                 join_by_right=["Country", "Date_of_Impacting_Restrictions"],
                                 keep = ['Country_left', 'Date_reported_left', 'Date_reported_right', 
                                         'Date_of_Impacting_Restrictions', 'containment_index', 
                                         'New_cases', 'Cumulative_cases', 'New_deaths', 
                                         'Cumulative_deaths'],
                                 clean_by = {'Country_left':'Country', 
                                             'Date_reported_right':'Date_reported'})

merge_ci_WHO = merge_ci_WHO[merge_ci_WHO['Date_reported_left'] == merge_ci_WHO['Date_of_Impacting_Restrictions']]
merge_ci_WHO = merge_ci_WHO.drop(columns='Date_reported_left')

# Population statistics
pop_stats = pop_stats[['Country Name', '2019']]
pop_stats = pop_stats.rename(columns={'Country Name':'Country'})

merged_country_list = merge_ci_WHO['Country'].unique()
pop_country_list = pop_stats['Country'].unique()

regions = ['Arab World', 'East Asia & Pacific (excluding high income)',
          'Early-demographic dividend', 'East Asia & Pacific', 
          'Europe & Central Asia (excluding high income)',
          'Europe & Central Asia', 'Euro area', 'European Union',
          'Fragile and conflict affected situations',
          'High income', 'South Asia (IDA & IBRD)', 'South Asia', 'North America',
          'South Asia (IDA & IBRD)'] 

pop_stats = pop_stats[~pop_stats['Country'].isin(regions)]

merge_ci_WHO = fw_join_and_clean(df_main = merge_ci_WHO, 
                                 df_right = pop_stats, 
                                 join_by_left=["Country"], 
                                 join_by_right=["Country"],
                                 keep = ['Country_left', 'Date_reported', 'Date_of_Impacting_Restrictions', 
                                         'containment_index', 'New_cases', 'Cumulative_cases', 'New_deaths', 
                                         'Cumulative_deaths', '2019'],
                                 clean_by = {'Country_left':'Country', 
                                             '2019':'Population'})

# Government Indicator
gov_eff_ind = gov_eff_ind[gov_eff_ind['Indicator Name'].isin(['Government Effectiveness: Estimate', 'Government Effectiveness: Percentile Rank'])]
gov_eff_ind = gov_eff_ind[['Country Name', 'Indicator Name', '2019']]
gov_eff_ind = gov_eff_ind.rename(columns={'Country Name':'Country'})

gov_eff_ind = gov_eff_ind.pivot_table(index='Country', 
                                      columns='Indicator Name', 
                                      values='2019', 
                                      fill_value=0).rename_axis(None, axis=1).reset_index()

gov_eff_country_list = gov_eff_ind['Country'].unique()


merge_ci_WHO = fw_join_and_clean(df_main = merge_ci_WHO, 
                                 df_right = gov_eff_ind, 
                                 join_by_left=["Country"], 
                                 join_by_right=["Country"],
                                 keep = ['Country_left', 'Date_reported', 'Date_of_Impacting_Restrictions', 
                                         'containment_index', 'New_cases', 'Cumulative_cases', 'New_deaths', 
                                         'Cumulative_deaths', 'Population', 'Government Effectiveness: Estimate',
                                         'Government Effectiveness: Percentile Rank'],
                                 clean_by = {'Country_left':'Country',
                                           'Government Effectiveness: Estimate': 'Gov_Eff_Est',
                                           'Government Effectiveness: Percentile Rank':'Gov_Eff_Per'})

#-------------------- Inferential Analysis ----------------------#
merge_ci_WHO.to_sql('merged', covid_conn, if_exists='replace')

avg_con_ind = pd.read_sql_query("""select Country, Population, Gov_Eff_Est,
                                Gov_Eff_Per, avg(containment_index) from merged group by Country""", covid_conn)

avg_cc_by_gov_eff = pd.read_sql_query("""select Country, Gov_Eff_Per,
                                ((Cumulative_cases / Population) * 100) as Cumulative_cases_pop_scaled
                                from merged where Date_reported between '2021-05-26' and '2021-05-27'""", covid_conn)

url = 'https://restcountries.eu/rest/v2/all'
req_iso = requests.get(url)
iso_df = pd.json_normalize(req_iso.json())
iso_df = iso_df[['name', 'alpha3Code']]
iso_df = iso_df.rename(columns={'name':'Country'})

merge_ci_WHO = fw_join_and_clean(df_main = merge_ci_WHO, 
                                 df_right = iso_df, 
                                 join_by_left=["Country"], 
                                 join_by_right=["Country"],
                                 keep = ['Country_left', 'alpha3Code', 'Date_reported', 'Date_of_Impacting_Restrictions', 
                                         'containment_index', 'New_cases', 'Cumulative_cases', 'New_deaths', 
                                         'Cumulative_deaths', 'Population', 'Gov_Eff_Est',
                                         'Gov_Eff_Per'],
                                 clean_by = {'Country_left':'Country'})

merge_ci_WHO.to_sql('merged', covid_conn, if_exists='replace')

merge_ci_WHO = pd.read_sql_query("""select *, 
                                ((Cumulative_cases / Population) * 100) as Cumulative_cases_pop_scaled,
                                ((New_cases / Population) * 100) as New_cases_pop_scaled
                                from merged""", covid_conn)
merge_ci_WHO['Date_reported'] = (pd.to_datetime(merge_ci_WHO['Date_reported'])).dt.strftime('%Y-%m-%d')
merge_ci_WHO['Date_of_Impacting_Restrictions'] = pd.to_datetime(merge_ci_WHO['Date_of_Impacting_Restrictions'])
merge_ci_WHO = merge_ci_WHO.drop(columns = 'index')

# Weekly Data
for i in pd.date_range(start='2020-03-11', end='2021-05-26', freq='W'):
    date = pd.to_datetime(i)
    date = date.strftime('%Y-%m-%d')
    merge_ci_WHO[merge_ci_WHO['Date_reported'] == date].to_sql('weekly', covid_conn, if_exists='append')

eff_gov = pd.read_sql_query("select * from weekly where Gov_Eff_Per > 50", covid_conn)

eff_gov['Date_reported'] = (pd.to_datetime(eff_gov['Date_reported'])).dt.strftime('%Y-%m-%d')
eff_gov['Date_of_Impacting_Restrictions'] = pd.to_datetime(eff_gov['Date_of_Impacting_Restrictions'])
eff_gov = eff_gov.dropna()

# Correlation and Regression
ols_result = sm.ols(formula='New_cases_pop_scaled~containment_index',
                   data=merge_ci_WHO).fit()

# Borrowed from HW 3
query = '''
select Date_reported,
count(*) as n, 
sum(containment_index * New_cases_pop_scaled) as cross, 
sum(containment_index * containment_index) as sqr_1, 
sum(New_cases_pop_scaled * New_cases_pop_scaled) as sqr_2, 
avg(containment_index) as mu_1, 
avg(New_cases_pop_scaled) as mu_2 
from weekly where Gov_Eff_Per > 50
group by Date_reported 
'''

pearson_corr_df = pd.read_sql_query(query, con=covid_conn)
pearson_corr_df['Date_reported'] = pd.to_datetime(pearson_corr_df['Date_reported'], format='%Y-%m-%d')
pearson_corr_df = pearson_corr_df.set_index('Date_reported')


pearson_corr_df['pearson_corr'] = ((pearson_corr_df['cross'] - pearson_corr_df['n']*pearson_corr_df['mu_1']*pearson_corr_df['mu_2']) /
                                  ((pearson_corr_df['sqr_1'] - pearson_corr_df['n']*pearson_corr_df['mu_1']**2)**0.5 *
                                  (pearson_corr_df['sqr_2'] - pearson_corr_df['n']*pearson_corr_df['mu_2']**2)**0.5))
pearson_corr_df

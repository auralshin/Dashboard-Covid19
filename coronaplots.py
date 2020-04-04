#!/usr/bin/env python
# coding: utf-8

# In[70]:


import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class CoronaPlots(object):

    def __init__(self, confirmed_url, deaths_url, recovered_url, country_codes_file):
        self.__load_datasets__(confirmed_url, deaths_url,
                               recovered_url, country_codes_file)
        self.__compute_totals__()
        self.__get_today_data__()
        self.__summary_values__()
        self.__build_table__()

    def __import_from_github__(self, url, category):
        '''Importing and preformatting the data'''

        df = pd            .read_csv(url)            .melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
                  var_name='Datetime',
                  value_name=category)\
            .drop(columns=['Lat', 'Long'])

        df['Datetime'] = pd.to_datetime(df.Datetime)

        return(df)

    def __load_datasets__(self, confirmed_url, deaths_url, recovered_url, country_codes_file):
        '''Loading Confirmed, Deaths and Recovered
           datasets from CSSEGISandData
           '''
        self.conf = self.__import_from_github__(confirmed_url, 'Confirmed')
        self.deaths = self.__import_from_github__(deaths_url, 'Deaths')
        self.recovered = self.__import_from_github__(
            recovered_url, 'Recovered')
        self.codes = pd.read_csv(country_codes_file)

    def __compute_totals__(self):

        self.total = pd            .merge(pd.merge(self.conf, self.deaths), self.recovered)            .groupby('Datetime').sum()            .reset_index()            .melt(id_vars=['Datetime'],
                  var_name='type',
                  value_name='value')

        self.total.columns = ['Date', 'Category', 'Cases']

    def __get_today_data__(self):
        # only last day data
        last_1d = self.conf.set_index(self.conf.Datetime).last('1D')

        # appending country codes
        self.today = pd.merge(last_1d, self.codes,
                              left_on='Country/Region', right_on='COVID-19',
                              how='left')\
            .groupby(['Codes', 'Country/Region', 'Names'])\
            .sum()\
            .reset_index()\
            .sort_values(['Confirmed'], ascending=False)

    def build_timeline(self):
        # TIMELINE
        timeline = px.line(self.total, x="Date", y="Cases", log_y=True,
                           color="Category", line_group="Category",
                           line_shape="spline", render_mode="svg",
                           height=250, template='plotly_white',)

        # LEGEND
        timeline.update_layout(
            legend_orientation="h",
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)',),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            legend_title='',)

        # HOVER TEMPLATE
        timeline.update_traces(hovertemplate='<b>%{x}</b><br>%{y}',)

        # REMOVE AXIS TITLES
        timeline.update_xaxes(title_text=None, fixedrange=True)
        timeline.update_yaxes(title_text=None, fixedrange=True)

        return(timeline)

    def build_map(self):

        choropleth = go.Figure(data=go.Choropleth(

            # Codes and counts
            locations=self.today['Codes'],
            z=np.log10(self.today.Confirmed),

            # Hover data
            text=self.today['Codes'].str.cat(
                self.today.Confirmed.apply(str), sep='<br>'),
            customdata=self.today['Confirmed'],
            hoverinfo='text',

            # Appearance
            colorscale=[[0, '#799AC4'], [1, '#BB4440']],

            colorbar=dict(
                tickvals=[1, 2, 3, 4],
                ticktext=["<10", "100", "1K", ">10K"],
            ),

            autocolorscale=False,
            marker_line_color='darkgrey',
            marker_line_width=0.5,
        ))

        choropleth.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            dragmode=False,
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='kavrayskiy7',
            )
        )
        return(choropleth)

    def __summary_values__(self):
        # Values that will be displayed on the page
        self.total_countries = self.today['Country/Region'].count()
        self.last_update = str(
            list(self.conf.Datetime.sort_values())[-1].date())
        self.total_confirmed_cases = int(self.today.Confirmed.sum())

    def __build_table__(self):
        self.summary_table = self.today[['Country/Region', 'Confirmed']]


# In[ ]:





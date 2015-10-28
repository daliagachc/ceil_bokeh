# [sql]
connection='mysql://server:server@10.8.3.1/'
# [sql_ceil]
data_base_name_ceil='ceilometer_ceilometer02'
bs_table_name_ceil = 'backscatering'
st_table_name_ceil = 'status'
time_column_name_ceil = 'time'
plot_title_ceil = 'ceilometer backscatering'
# [sql_weewx]
data_base_name_weewx='weewx_ceilometer02'
table_name_weewx = 'archive'
time_column_name_weewx = 'dateTime'
column_names_weewx = ['pressure','outTemp','outHumidity','rainRate']
column_units_weewx = ['[mb]','[C]','[%]','[mm/hour]']
plot_title_weewx = "weather conditions"
# [plot]
time_int=300
time_span_first=3600*24
time_int_data_range=3600
border_left = 120
plot_height = 250
plot_width = 800
data_range_plot_height = 150

#average data for different time ranges is seconds

data_average_interval_list=[
    [3600*4,30], #for less than 4 hours average to 30 seconds
    [3600*12,60], # for less thant 12 houts average to 1 minute
    [3600*24,300], # for less than 1 day average to 5 minutes
    [3600*24*7,60*30], # 1 week to half an hour
    [3600*24*7*4,3600*2], # 1 month to 2 hours
    [3600*24*7*4*6,3600*12], # 6 months to 12 hours
    [3600*24*7*4*12,3600*24], # 1 year to 1 day
    [3600*24*7*4*12*5,3600*24*7] # 5 years and more to 7 days

]

utc_shift = -3600*4
utc_start = 0 # local = 0 ; utc = 1

logging_level = 'DEBUG'
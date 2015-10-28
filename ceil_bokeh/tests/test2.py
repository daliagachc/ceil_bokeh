from ceil_bokeh import sql_con

# df=sql_con.get_data_bs(time_int=600)
# df=sql_con.get_data_ws(time_int=1)
df=sql_con.get_data_tm(
    'dateTime',600,'weewx_ceilometer02',
    'archive',"mysql://server:server@10.8.3.1/")


print df
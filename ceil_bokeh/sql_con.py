__author__ = 'diego'
'''This modules handles all interactions with sql through sql alchemy'''
import logging
logger = logging.getLogger(__name__)
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy.sql import select
from sqlalchemy import func
import pandas as pd
import  ceil_bokeh.logging_functions as log_fun

from ceil_bokeh import constants as cs


def round_time(time_interval, time_column):
    t_i = float(time_interval)
    return (func.round(time_column / t_i) * t_i).label('round_time' + time_column.key)


def correct_bs(column_offset, column_bs, index):
    return (func.avg((column_bs - column_offset) * func.power(index, 2))).label(column_bs.key)

@log_fun.log_start_end
def get_data_bs(time_int=cs.time_int,
                t_min=0,
                t_max=10 ** 10):
    connection=cs.connection
    data_base_name=cs.data_base_name_ceil
    bs_table_name=cs.bs_table_name_ceil
    st_table_name=cs.st_table_name_ceil
    time_column_name=cs.time_column_name_ceil
    # sql setup
    eng = create_engine(connection)
    meta = MetaData()
    # reflect tables. Maybe it would be best to write a class since we know the structure
    meta.reflect(bind=eng,
                 schema=data_base_name,
                 only=[bs_table_name, st_table_name])

    bs_table = meta.tables[data_base_name + '.' + bs_table_name]
    st_table = meta.tables[data_base_name + '.' + st_table_name]

    bs_column_names = bs_table.columns.keys()
    bs_column_names.remove(time_column_name)
    # st_column_names = st_table.columns.keys()

    rounded_time_query = round_time(time_int, bs_table.c[time_column_name])

    correct_bs_query_list = []

    for i, col in enumerate(bs_column_names):
        correct = correct_bs(st_table.c.zero_offset, bs_table.columns[col], i + 1)
        correct_bs_query_list.append(correct)

    select_query = select([rounded_time_query] + correct_bs_query_list)

    select_query = select_query.where(bs_table.c[time_column_name] == st_table.c[time_column_name])
    select_query = select_query.where(bs_table.c[time_column_name] >= t_min)
    select_query = select_query.where(bs_table.c[time_column_name] < t_max)

    select_query = select_query.group_by('round_time' + time_column_name)

    # select_query = select_query.limit(1000)

    con = eng.connect()

    rs = con.execute(select_query)

    res = rs.fetchall()

    data = pd.DataFrame(res,columns=bs_table.columns.keys())



    return data

@log_fun.log_start_end
def get_data_tm(time_column_name,
                time_int,
                data_base_name,
                table_name,
                connection=cs.connection):
    eng = create_engine(connection)
    meta = MetaData()

    table = Table(table_name,
                  meta,
                  Column(time_column_name, Integer, primary_key=True),
                  schema=data_base_name)

    time_column = table.columns[time_column_name]
    # st_column_names = st_table.columns.keys()

    rounded_time_query = round_time(time_int, time_column)

    select_query = select([rounded_time_query])
    # print time_column_name
    select_query = select_query.group_by('round_time' + time_column_name)

    select_query = select_query

    # print select_query

    con = eng.connect()

    rs = con.execute(select_query)


    res = rs.fetchall()


    data = pd.DataFrame(res)

    return data

@log_fun.log_start_end
def get_data_ws(time_int=cs.time_int,
                t_min=0,
                t_max=10 ** 10):
    connection = cs.connection
    data_base_name = cs.data_base_name_weewx
    table_name = cs.table_name_weewx
    time_column_name = cs.time_column_name_weewx
    column_names = cs.column_names_weewx
    eng = create_engine(connection)

    meta = MetaData()

    meta.reflect(bind=eng,
                 schema=data_base_name,
                 only=[table_name])

    archive = Table(table_name,
                    meta,
                    autoload=True,
                    schema=data_base_name,
                    autoload_with=eng)

    rounded_time_query = round_time(time_int, archive.c[time_column_name])

    select_query = [rounded_time_query]

    # print archive.c[time_column_name].key
    for column in column_names:
        select_query.append(
            func.avg(
                archive.c[column]
            ).label(column)
        )

    select_query = select(select_query)

    select_query = select_query.where(archive.c[time_column_name] >= t_min)
    select_query = select_query.where(archive.c[time_column_name] < t_max)

    select_query = select_query.group_by('round_time' + time_column_name)
    # print select_query
    con = eng.connect()

    rs = con.execute(select_query)

    # logging.debug("trying to fetch results")
    res = rs.fetchall()
    # logging.debug("results fetched")
    columns = [time_column_name] + column_names

    data = pd.DataFrame(res,
                        columns=columns
                        )
    # # transform seconds to miliseconds
    #
    # data[time_column_name] = data[time_column_name].apply(lambda x: x * 1000)
    # # data=data.to_dict(orient='list')
    # # lets return a pandas dataframe instead of a dict
    return data
